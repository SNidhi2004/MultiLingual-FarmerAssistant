# backend/test_model.py
from services.plant_disease import analyze_image

# Option 1: Use forward slashes (works on all OS)
with open("C:/Users/bsrao/Desktop/LHJ2.jpg", "rb") as f:
    result = analyze_image(f.read())

# Option 2: Or escape backslashes
# with open("C:\\Users\\bsrao\\Desktop\\LHJ2.jpg", "rb") as f:
#     result = analyze_image(f.read())

print(f"Predicted: {result['disease']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Model used: {result['model_used']}")
print(f"Model type: {result.get('model_type', 'unknown')}")
print(f"Top predictions: {result.get('top_predictions', [])}")

# If you want to see all results from all models:
if 'all_models_results' in result:
    print("\nAll models results:")
    for r in result['all_models_results']:
        print(f"  {r['model']} ({r['type']}): {r['disease']} ({r['confidence']:.2%})")