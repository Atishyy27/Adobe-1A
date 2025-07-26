# main.py – CLI version (NOT FastAPI)

import os
import json
from services import structuring

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            try:
                result = structuring.get_document_structure(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                print(f"✓ Processed: {filename}")
            except Exception as e:
                print(f"✗ Failed: {filename} – {e}")

if __name__ == "__main__":
    main()
