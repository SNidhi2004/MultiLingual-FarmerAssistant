import numpy as np
import cv2
from PIL import Image
import io
import os
import json
import glob


class PlantDiseaseDetector:
    def __init__(self):
        self.yolo_models = []
        self.cnn_models = []
        self.model_loaded = False
        self.input_size = (224, 224)
        self._load_all_models()

    def _load_all_models(self):
        try:
            # FIX: plant_disease.py lives in services/, models/ is inside services/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, 'models')

            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                print(f"Created models folder at: {model_dir}")
                print("  Place cnn_model.h5 and yolo_model.pt inside services/models/")
                print("  Also copy cnn_model_classes.json and yolo_model_classes.json there")

            # ---- YOLO models (.pt) ----
            yolo_files = glob.glob(os.path.join(model_dir, '*.pt'))
            print(f"Found {len(yolo_files)} YOLO model file(s) in {model_dir}")

            for model_path in yolo_files:
                try:
                    from ultralytics import YOLO
                    model_name = os.path.basename(model_path).replace('.pt', '')
                    print(f"Loading YOLO model: {model_name}")
                    model = YOLO(model_path)

                    # Look for matching classes JSON
                    classes_path = os.path.join(model_dir, f'{model_name}_classes.json')
                    if not os.path.exists(classes_path):
                        classes_path = os.path.join(model_dir, 'classes.json')

                    class_names = []
                    if os.path.exists(classes_path):
                        with open(classes_path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                class_names = data
                            elif isinstance(data, dict):
                                class_names = data.get('diseases', data.get('classes', []))

                    # Fallback: use names embedded in the model
                    if not class_names and hasattr(model, 'names'):
                        class_names = list(model.names.values())

                    self.yolo_models.append({
                        'name': model_name,
                        'model': model,
                        'class_names': class_names,
                        'type': 'yolo_classification'
                    })
                    print(f"YOLO model loaded: {model_name} ({len(class_names)} classes)")

                except Exception as e:
                    print(f"Error loading YOLO model {model_path}: {e}")

            # ---- CNN models (.h5 / .keras) ----
            cnn_files = (
                glob.glob(os.path.join(model_dir, '*.h5')) +
                glob.glob(os.path.join(model_dir, '*.keras'))
            )
            print(f"Found {len(cnn_files)} CNN model file(s) in {model_dir}")

            for model_path in cnn_files:
                try:
                    # Import tensorflow lazily so startup doesn't crash if TF absent
                    import tensorflow as tf

                    model_name = os.path.basename(model_path).replace('.h5', '').replace('.keras', '')
                    print(f"Loading CNN model: {model_name}")

                    classes_path = os.path.join(model_dir, f'{model_name}_classes.json')
                    if not os.path.exists(classes_path):
                        classes_path = os.path.join(model_dir, 'classes.json')

                    class_names = []
                    if os.path.exists(classes_path):
                        with open(classes_path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                class_names = data
                            elif isinstance(data, dict):
                                class_names = data.get('diseases', data.get('classes', []))

                    # compile=False avoids optimizer errors on older saved models
                    model = tf.keras.models.load_model(model_path, compile=False)

                    self.cnn_models.append({
                        'name': model_name,
                        'model': model,
                        'class_names': class_names,
                        'type': 'cnn',
                        'input_size': self.input_size
                    })
                    print(f"CNN model loaded: {model_name} ({len(class_names)} classes)")

                except Exception as e:
                    print(f"Could not load CNN model {model_path}: {e}")

            if self.yolo_models or self.cnn_models:
                self.model_loaded = True
                print(f"Total models: {len(self.yolo_models)} YOLO, {len(self.cnn_models)} CNN")
            else:
                print("No models found — using placeholder detection.")

        except Exception as e:
            print(f"Error in model loading: {e}")

    # ---- Preprocessing ----

    def preprocess_yolo_image(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img
        except Exception as e:
            print(f"YOLO preprocessing error: {e}")
            return None

    def preprocess_cnn_image(self, image_bytes, target_size=(224, 224)):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = image.resize(target_size)
            img_array = np.array(image).astype(np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"CNN preprocessing error: {e}")
            return None

    # ---- Prediction ----

    def predict_with_yolo_classification(self, model_info, img):
        try:
            print(f"Running YOLO classification with {model_info['name']}")
            results = model_info['model'](img, verbose=False)
            result = results[0]

            if hasattr(result, 'probs') and result.probs is not None:
                probs = result.probs
                confidences = probs.data.cpu().numpy()
                top_indices = np.argsort(confidences)[-5:][::-1]
                best_idx = int(top_indices[0])
                confidence = float(confidences[best_idx])

                class_names = model_info['class_names']
                disease_name = (
                    class_names[best_idx]
                    if class_names and best_idx < len(class_names)
                    else f"Disease_{best_idx}"
                )

                top_predictions = [
                    {
                        "disease": class_names[idx] if class_names and idx < len(class_names) else f"Disease_{idx}",
                        "confidence": float(confidences[idx])
                    }
                    for idx in top_indices
                ]

                print(f"  Prediction: {disease_name} ({confidence:.2%})")
                return {
                    "disease": disease_name,
                    "confidence": confidence,
                    "type": "yolo_classification",
                    "model_name": model_info['name'],
                    "all_predictions": top_predictions
                }
            else:
                # Fallback: detection model used instead of classification
                print("  No probs — trying boxes fallback")
                boxes = result.boxes
                if boxes is not None and len(boxes):
                    confidences_b = boxes.conf.cpu().numpy()
                    class_ids = boxes.cls.cpu().numpy().astype(int)
                    best_idx = int(np.argmax(confidences_b))
                    confidence = float(confidences_b[best_idx])
                    class_id = int(class_ids[best_idx])
                    class_names = model_info['class_names']
                    disease_name = (
                        class_names[class_id]
                        if class_names and class_id < len(class_names)
                        else f"Disease_{class_id}"
                    )
                    return {
                        "disease": disease_name,
                        "confidence": confidence,
                        "type": "yolo_detection",
                        "model_name": model_info['name'],
                        "all_predictions": []
                    }
                print("  No detections found")
                return None

        except Exception as e:
            print(f"Error with YOLO model {model_info['name']}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def predict_with_cnn(self, model_info, img_array):
        try:
            print(f"Running CNN prediction with {model_info['name']}")
            predictions = model_info['model'].predict(img_array, verbose=0)
            confidence = float(np.max(predictions[0]))
            class_idx = int(np.argmax(predictions[0]))

            class_names = model_info['class_names']
            disease_name = (
                class_names[class_idx]
                if class_names and class_idx < len(class_names)
                else f"Disease_{class_idx}"
            )

            print(f"  Prediction: {disease_name} ({confidence:.2%})")
            return {
                "disease": disease_name,
                "confidence": confidence,
                "type": "cnn",
                "model_name": model_info['name']
            }
        except Exception as e:
            print(f"CNN prediction error: {e}")
            return None

    def predict(self, image_bytes):
        try:
            if not self.model_loaded or (not self.yolo_models and not self.cnn_models):
                print("No models loaded — returning placeholder")
                return {
                    "disease": "Leaf Curl Virus",
                    "confidence": 0.88,
                    "model_used": "placeholder",
                    "message": "No models found. Place model files in services/models/"
                }

            results = []

            if self.yolo_models:
                yolo_img = self.preprocess_yolo_image(image_bytes)
                if yolo_img is not None:
                    for model_info in self.yolo_models:
                        result = self.predict_with_yolo_classification(model_info, yolo_img)
                        if result:
                            results.append(result)

            if self.cnn_models:
                cnn_img_array = self.preprocess_cnn_image(image_bytes, self.input_size)
                if cnn_img_array is not None:
                    for model_info in self.cnn_models:
                        result = self.predict_with_cnn(model_info, cnn_img_array)
                        if result:
                            results.append(result)

            if not results:
                print("No results from any model — returning placeholder")
                return {
                    "disease": "Leaf Curl Virus",
                    "confidence": 0.88,
                    "model_used": "placeholder",
                    "message": "No predictions from models"
                }

            best_result = max(results, key=lambda x: x['confidence'])
            print(f"BEST: {best_result['disease']} ({best_result['confidence']:.2%}) from {best_result['model_name']}")

            return {
                "disease": best_result['disease'],
                "confidence": best_result['confidence'],
                "model_used": best_result['model_name'],
                "model_type": best_result['type'],
                "top_predictions": best_result.get('all_predictions', [])[:3],
                "all_models_results": [
                    {
                        "model": r['model_name'],
                        "type": r['type'],
                        "disease": r['disease'],
                        "confidence": r['confidence']
                    }
                    for r in results
                ]
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "disease": "Leaf Curl Virus",
                "confidence": 0.88,
                "model_used": "fallback",
                "error": str(e)
            }


# Singleton
detector = PlantDiseaseDetector()


def analyze_image(image_bytes):
    return detector.predict(image_bytes)


def get_model_status():
    return {
        "yolo_models": [m['name'] for m in detector.yolo_models],
        "cnn_models": [m['name'] for m in detector.cnn_models],
        "total_models": len(detector.yolo_models) + len(detector.cnn_models)
    }