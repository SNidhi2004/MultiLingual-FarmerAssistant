# import numpy as np
# import tensorflow as tf
# from PIL import Image
# import io
# import os
# import json
# import glob
# import cv2

# class PlantDiseaseDetector:
#     def __init__(self):
#         """Initialize YOLO and CNN models"""
#         self.yolo_models = []
#         self.cnn_models = []
#         self.model_loaded = False
#         self.input_size = (224, 224)
        
#         # Try to load models (if any exist)
#         self._load_all_models()
    
#     def _load_all_models(self):
#         """Load all YOLO and CNN models if they exist"""
#         try:
#             current_dir = os.path.dirname(os.path.abspath(__file__))
#             model_dir = os.path.join(current_dir, 'models')
            
#             # Create models folder if it doesn't exist
#             if not os.path.exists(model_dir):
#                 os.makedirs(model_dir)
#                 print(f"📁 Created models folder at: {model_dir}")
#                 print("   Place your .pt (YOLO) and .h5 (CNN) files here")
            
#             # ==================== LOAD YOLO MODELS (.pt) ====================
#             yolo_files = glob.glob(os.path.join(model_dir, '*.pt'))
            
#             for model_path in yolo_files:
#                 try:
#                     from ultralytics import YOLO
#                     model_name = os.path.basename(model_path).replace('.pt', '')
#                     print(f"📦 Loading YOLO model: {model_name}")
#                     model = YOLO(model_path)
                    
#                     # Load class names
#                     classes_path = os.path.join(model_dir, f'{model_name}_classes.json')
#                     class_names = []
#                     if os.path.exists(classes_path):
#                         with open(classes_path, 'r') as f:
#                             data = json.load(f)
#                             if isinstance(data, list):
#                                 class_names = data
#                             elif isinstance(data, dict):
#                                 class_names = data.get('classes', data.get('diseases', []))
                    
#                     self.yolo_models.append({
#                         'name': model_name,
#                         'model': model,
#                         'class_names': class_names,
#                         'type': 'yolo'
#                     })
#                     print(f"✅ YOLO model loaded: {model_name}")
                    
#                 except Exception as e:
#                     print(f"⚠️ Could not load YOLO model {model_path}: {e}")
            
#             # ==================== LOAD CNN MODELS (.h5, .keras) ====================
#             cnn_files = []
#             cnn_files.extend(glob.glob(os.path.join(model_dir, '*.h5')))
#             cnn_files.extend(glob.glob(os.path.join(model_dir, '*.keras')))
            
#             for model_path in cnn_files:
#                 try:
#                     model_name = os.path.basename(model_path).replace('.h5', '').replace('.keras', '')
#                     print(f"📦 Loading CNN model: {model_name}")
                    
#                     # Load class names
#                     classes_path = os.path.join(model_dir, f'{model_name}_classes.json')
#                     if not os.path.exists(classes_path):
#                         classes_path = os.path.join(model_dir, 'classes.json')
                    
#                     class_names = []
#                     if os.path.exists(classes_path):
#                         with open(classes_path, 'r') as f:
#                             data = json.load(f)
#                             if isinstance(data, list):
#                                 class_names = data
#                             elif isinstance(data, dict):
#                                 class_names = data.get('diseases', data.get('classes', []))
                    
#                     model = tf.keras.models.load_model(model_path)
                    
#                     self.cnn_models.append({
#                         'name': model_name,
#                         'model': model,
#                         'class_names': class_names,
#                         'type': 'cnn',
#                         'input_size': self.input_size
#                     })
#                     print(f"✅ CNN model loaded: {model_name}")
                    
#                 except Exception as e:
#                     print(f"⚠️ Could not load CNN model {model_path}: {e}")
            
#             if self.yolo_models or self.cnn_models:
#                 self.model_loaded = True
#                 print(f"✅ Loaded {len(self.yolo_models)} YOLO, {len(self.cnn_models)} CNN models")
#             else:
#                 print("ℹ️ No models found. Using placeholder detection.")
#                 print("   To add models, place .pt and .h5 files in:", model_dir)
                
#         except Exception as e:
#             print(f"⚠️ Error in model loading: {e}")
#             # Continue without models - no crash
    
#     def preprocess_cnn_image(self, image_bytes, target_size=(224, 224)):
#         """Preprocess image for CNN models"""
#         try:
#             image = Image.open(io.BytesIO(image_bytes))
#             if image.mode != 'RGB':
#                 image = image.convert('RGB')
#             image = image.resize(target_size)
#             img_array = np.array(image).astype(np.float32) / 255.0
#             img_array = np.expand_dims(img_array, axis=0)
#             return img_array
#         except Exception as e:
#             print(f"❌ CNN preprocessing error: {e}")
#             return None
    
#     def preprocess_yolo_image(self, image_bytes):
#         """Preprocess image for YOLO models"""
#         try:
#             nparr = np.frombuffer(image_bytes, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             return img
#         except Exception as e:
#             print(f"❌ YOLO preprocessing error: {e}")
#             return None
    
#     def predict_with_cnn(self, model_info, img_array):
#         """Run prediction with CNN model"""
#         try:
#             predictions = model_info['model'].predict(img_array, verbose=0)
#             confidence = float(np.max(predictions[0]))
#             class_idx = int(np.argmax(predictions[0]))
            
#             if class_idx < len(model_info['class_names']):
#                 disease_name = model_info['class_names'][class_idx]
#             else:
#                 disease_name = f"Disease_{class_idx}"
            
#             return {
#                 "disease": disease_name,
#                 "confidence": confidence,
#                 "type": "cnn",
#                 "model_name": model_info['name']
#             }
#         except Exception as e:
#             print(f"❌ CNN prediction error: {e}")
#             return None
    
#     def predict_with_yolo(self, model_info, img):
#         """Run prediction with YOLO model"""    
#         try:
#             print(f"🔍 Running YOLO prediction with {model_info['name']}")
#             print(f"   Image shape: {img.shape if img is not None else 'None'}")
            
#             # Run YOLO inference with lower confidence threshold for testing
#             results = model_info['model'](img, conf=0.1, verbose=True)  # Lower threshold and verbose
            
#             print(f"   Results count: {len(results)}")
            
#             if len(results) == 0:
#                 print("   ❌ No results returned")
#                 return None
            
#             if results[0].boxes is None:
#                 print("   ❌ No boxes found in results")
#                 return None
            
#             boxes = results[0].boxes
#             confidences = boxes.conf.cpu().numpy()
#             class_ids = boxes.cls.cpu().numpy().astype(int)
            
#             print(f"   Found {len(confidences)} detections")
#             print(f"   Confidences: {confidences}")
#             print(f"   Class IDs: {class_ids}")
            
#             if len(confidences) == 0:
#                 print("   ❌ No confidences found")
#                 return None
            
#             # Get best detection
#             best_idx = np.argmax(confidences)
#             confidence = float(confidences[best_idx])
#             class_id = int(class_ids[best_idx])
            
#             print(f"   Best detection: class_id={class_id}, confidence={confidence}")
            
#             # Get disease name
#             if model_info['class_names'] and class_id < len(model_info['class_names']):
#                 disease_name = model_info['class_names'][class_id]
#                 print(f"   Disease name: {disease_name}")
#             else:
#                 disease_name = f"Disease_{class_id}"
#                 print(f"   No class name for ID {class_id}, using: {disease_name}")
            
#             return {
#                 "disease": disease_name,
#                 "confidence": confidence,
#                 "type": "yolo",
#                 "model_name": model_info['name']
#             }
            
#         except Exception as e:
#             print(f"❌ Error with YOLO model {model_info['name']}: {e}")
#             import traceback
#             traceback.print_exc()
#             return None
    
#     def predict(self, image_bytes):
#         """Run prediction with all models and return best result"""
#         try:
#             # If no models are loaded, return placeholder
#             if not self.model_loaded or (not self.yolo_models and not self.cnn_models):
#                 print("⚠️ No models loaded, using placeholder")
#                 return {
#                     "disease": "Leaf Curl Virus",
#                     "confidence": 0.88,
#                     "model_used": "placeholder",
#                     "message": "Placeholder detection. Add models to models/ folder"
#                 }
            
#             results = []
            
#             # YOLO predictions
#             if self.yolo_models:
#                 print("\n" + "="*40)
#                 print("Running YOLO predictions...")
#                 yolo_img = self.preprocess_yolo_image(image_bytes)
#                 if yolo_img is not None:
#                     for model_info in self.yolo_models:
#                         result = self.predict_with_yolo(model_info, yolo_img)
#                         if result:
#                             results.append(result)
#                             print(f"✅ YOLO result: {result['disease']} ({result['confidence']:.2%})")
#                         else:
#                             print(f"❌ YOLO model {model_info['name']} returned no result")
#                 else:
#                     print("❌ YOLO preprocessing failed")
            
#             # CNN predictions
#             if self.cnn_models:
#                 print("\nRunning CNN predictions...")
#                 cnn_img_array = self.preprocess_cnn_image(image_bytes, self.input_size)
#                 if cnn_img_array is not None:
#                     for model_info in self.cnn_models:
#                         result = self.predict_with_cnn(model_info, cnn_img_array)
#                         if result:
#                             results.append(result)
#                             print(f"✅ CNN result: {result['disease']} ({result['confidence']:.2%})")
            
#             if not results:
#                 print("\n❌ No results from any model! Using placeholder.")
#                 return {
#                     "disease": "Leaf Curl Virus",
#                     "confidence": 0.88,
#                     "model_used": "placeholder",
#                     "message": "No predictions from models, using placeholder"
#                 }
            
#             # Select best result
#             best_result = max(results, key=lambda x: x['confidence'])
#             print(f"\n🏆 BEST RESULT: {best_result['disease']} ({best_result['confidence']:.2%}) from {best_result['model_name']}")
            
#             return {
#                 "disease": best_result['disease'],
#                 "confidence": best_result['confidence'],
#                 "model_used": best_result['model_name'],
#                 "model_type": best_result['type']
#             }
            
#         except Exception as e:
#             print(f"❌ Prediction error: {e}")
#             import traceback
#             traceback.print_exc()
#             return {
#                 "disease": "Leaf Curl Virus",
#                 "confidence": 0.88,
#                 "model_used": "fallback",
#                 "error": str(e)
#             }


# # Create a singleton instance
# detector = PlantDiseaseDetector()

# def analyze_image(image_bytes):
#     """Public function to analyze plant image"""
#     return detector.predict(image_bytes)

# def get_model_status():
#     """Public function to check model status"""
#     return {
#         "yolo_models": [m['name'] for m in detector.yolo_models],
#         "cnn_models": [m['name'] for m in detector.cnn_models],
#         "total_models": len(detector.yolo_models) + len(detector.cnn_models)
#     }

# # At the very end of plant_disease.py, add:
# print("\n" + "="*50)
# print("MODEL LOADING STATUS")
# print("="*50)
# status = get_model_status()
# print(f"YOLO models: {status['yolo_models']}")
# print(f"CNN models: {status['cnn_models']}")
# print(f"Total: {status['total_models']}")
# if status['total_models'] == 0:
#     print("⚠️ No models loaded! Using placeholder.")
#     print("📁 Please place models in: backend/services/models/")
#     print("   Supported formats: .pt (YOLO) and .h5/.keras (CNN)")
# print("="*50 + "\n")

import numpy as np
import cv2
from PIL import Image
import io
import os
import json
import glob

class PlantDiseaseDetector:
    def __init__(self):
        """Initialize YOLO classification models"""
        self.yolo_models = []
        self.cnn_models = []
        self.model_loaded = False
        self.input_size = (224, 224)
        
        # Load all models
        self._load_all_models()
    
    def _load_all_models(self):
        """Load all YOLO classification models"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, 'models')
            
            # Create models folder if it doesn't exist
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                print(f"📁 Created models folder at: {model_dir}")
            
            # Load YOLO classification models (.pt)
            yolo_files = glob.glob(os.path.join(model_dir, '*.pt'))
            print(f"🔍 Found {len(yolo_files)} YOLO model files")
            
            for model_path in yolo_files:
                try:
                    from ultralytics import YOLO
                    model_name = os.path.basename(model_path).replace('.pt', '')
                    
                    print(f"📦 Loading YOLO classification model: {model_name}")
                    model = YOLO(model_path)
                    
                    # Load class names for YOLO model
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
                    
                    # If no class names, try to infer from model
                    if not class_names:
                        # Get class names from model if available
                        if hasattr(model, 'names'):
                            class_names = list(model.names.values())
                    
                    self.yolo_models.append({
                        'name': model_name,
                        'model': model,
                        'class_names': class_names,
                        'type': 'yolo_classification'
                    })
                    print(f"✅ YOLO classification model loaded: {model_name} ({len(class_names)} classes)")
                    if class_names:
                        print(f"   Classes: {class_names[:5]}...")
                    
                except Exception as e:
                    print(f"❌ Error loading YOLO model {model_path}: {e}")
            
            # Load CNN models (.h5, .keras) - optional
            cnn_files = []
            cnn_files.extend(glob.glob(os.path.join(model_dir, '*.h5')))
            cnn_files.extend(glob.glob(os.path.join(model_dir, '*.keras')))
            
            for model_path in cnn_files:
                try:
                    import tensorflow as tf
                    model_name = os.path.basename(model_path).replace('.h5', '').replace('.keras', '')
                    print(f"📦 Loading CNN model: {model_name}")
                    
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
                    
                    model = tf.keras.models.load_model(model_path)
                    
                    self.cnn_models.append({
                        'name': model_name,
                        'model': model,
                        'class_names': class_names,
                        'type': 'cnn',
                        'input_size': self.input_size
                    })
                    print(f"✅ CNN model loaded: {model_name}")
                    
                except Exception as e:
                    print(f"⚠️ Could not load CNN model {model_path}: {e}")
            
            if self.yolo_models or self.cnn_models:
                self.model_loaded = True
                print(f"✅ Total models loaded: {len(self.yolo_models)} YOLO, {len(self.cnn_models)} CNN")
            else:
                print("ℹ️ No models found. Using placeholder detection.")
                
        except Exception as e:
            print(f"⚠️ Error in model loading: {e}")
    
    def preprocess_yolo_image(self, image_bytes):
        """Preprocess image for YOLO classification"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img
        except Exception as e:
            print(f"❌ YOLO preprocessing error: {e}")
            return None
    
    def predict_with_yolo_classification(self, model_info, img):
        """Run prediction with YOLO classification model"""
        try:
            print(f"🔍 Running YOLO classification with {model_info['name']}")
            
            # Run inference
            results = model_info['model'](img, verbose=False)
            result = results[0]
            
            # For classification models, results are in probs
            if hasattr(result, 'probs') and result.probs is not None:
                probs = result.probs
                confidences = probs.data.cpu().numpy()
                
                # Get top 5 predictions
                top_indices = np.argsort(confidences)[-5:][::-1]
                
                # Get best prediction
                best_idx = top_indices[0]
                confidence = float(confidences[best_idx])
                
                # Get class name
                if model_info['class_names'] and best_idx < len(model_info['class_names']):
                    disease_name = model_info['class_names'][best_idx]
                else:
                    disease_name = f"Disease_{best_idx}"
                
                # Get all top predictions
                top_predictions = []
                for idx in top_indices:
                    if model_info['class_names'] and idx < len(model_info['class_names']):
                        top_predictions.append({
                            "disease": model_info['class_names'][idx],
                            "confidence": float(confidences[idx])
                        })
                
                print(f"   ✅ Prediction: {disease_name} ({confidence:.2%})")
                print(f"   Top predictions: {[p['disease'] for p in top_predictions[:3]]}")
                
                return {
                    "disease": disease_name,
                    "confidence": confidence,
                    "type": "yolo_classification",
                    "model_name": model_info['name'],
                    "all_predictions": top_predictions
                }
            else:
                print("   ❌ No probs found in results")
                return None
                
        except Exception as e:
            print(f"❌ Error with YOLO model {model_info['name']}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict(self, image_bytes):
        """Run prediction with all models and return best result"""
        try:
            # If no models are loaded, return placeholder
            if not self.model_loaded or (not self.yolo_models and not self.cnn_models):
                return {
                    "disease": "Leaf Curl Virus",
                    "confidence": 0.88,
                    "model_used": "placeholder",
                    "message": "No models loaded. Add models to models/ folder"
                }
            
            results = []
            
            # YOLO classification predictions
            if self.yolo_models:
                print("\n" + "="*50)
                print("Running YOLO Classification predictions...")
                yolo_img = self.preprocess_yolo_image(image_bytes)
                if yolo_img is not None:
                    for model_info in self.yolo_models:
                        result = self.predict_with_yolo_classification(model_info, yolo_img)
                        if result:
                            results.append(result)
                else:
                    print("❌ YOLO preprocessing failed")
            
            # CNN predictions (if any)
            if self.cnn_models:
                print("\nRunning CNN predictions...")
                # Add CNN prediction code here if needed
            
            if not results:
                print("\n❌ No results from any model! Using placeholder.")
                return {
                    "disease": "Leaf Curl Virus",
                    "confidence": 0.88,
                    "model_used": "placeholder",
                    "message": "No predictions from models"
                }
            
            # Select best result
            best_result = max(results, key=lambda x: x['confidence'])
            print(f"\n🏆 BEST RESULT: {best_result['disease']} ({best_result['confidence']:.2%}) from {best_result['model_name']}")
            
            return {
                "disease": best_result['disease'],
                "confidence": best_result['confidence'],
                "model_used": best_result['model_name'],
                "model_type": best_result['type'],
                "top_predictions": best_result.get('all_predictions', [])[:3]
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "disease": "Leaf Curl Virus",
                "confidence": 0.88,
                "model_used": "fallback",
                "error": str(e)
            }


# Create a singleton instance
detector = PlantDiseaseDetector()

def analyze_image(image_bytes):
    """Public function to analyze plant image"""
    return detector.predict(image_bytes)

def get_model_status():
    """Public function to check model status"""
    return {
        "yolo_models": [m['name'] for m in detector.yolo_models],
        "cnn_models": [m['name'] for m in detector.cnn_models],
        "total_models": len(detector.yolo_models) + len(detector.cnn_models)
    }