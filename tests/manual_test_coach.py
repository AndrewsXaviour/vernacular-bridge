from fastapi.testclient import TestClient
from orchestrator import app
import json
import os

client = TestClient(app)

if __name__ == "__main__":
    results = {}
    try:
        # 1. Weak Answer Test
        print("Running Weak Answer Test...")
        payload_weak = {
            "question": "Explain the process of photosynthesis in detail.",
            "student_answer": "Plants make food using sunlight. It happens in leaves.",
            "language_config": {"primary": "tamil", "secondary": "english"}
        }
        res_weak = client.post("/coach", json=payload_weak)
        results["weak_answer"] = res_weak.json()
        
        # 2. Strong Answer Test
        print("Running Strong Answer Test...")
        payload_strong = {
            "question": "Explain the process of photosynthesis in detail.",
            "student_answer": "Photosynthesis is the biological process by which autotrophic organisms like green plants convert light energy into chemical energy, specifically glucose, using carbon dioxide and water. Chlorophyll in chloroplasts absorbs light, and oxygen is released as a byproduct. It involves light-dependent and Calvin cycle stages.",
            "language_config": {"primary": "tamil", "secondary": "english"}
        }
        res_strong = client.post("/coach", json=payload_strong)
        results["strong_answer"] = res_strong.json()
        
        output_path = os.path.join("tests", "manual_test_results.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Manual tests completed. Results saved to {output_path}")
        
    except Exception as e:
        print(f"Error during manual test: {e}")
