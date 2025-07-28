# src/json_generator.py
import json
import os

def generate_json_output(title, outline, output_path):
    """
    Formats the extracted title and outline into the required JSON structure
    and saves it to a file.
    """
    output_data = {
        "title": title,
        "outline": outline
    }

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Successfully saved JSON to {output_path}")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")