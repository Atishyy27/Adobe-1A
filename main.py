# main.py
import os
import time
from src.config import INPUT_DIR, OUTPUT_DIR
from src.pdf_parser import extract_raw_lines
from src.heading_detector import HeadingDetector
from src.json_generator import generate_json_output

def process_single_pdf(pdf_path, detector):
    pdf_filename = os.path.basename(pdf_path)
    print(f"🚀 Processing: {pdf_filename}")
    
    try:
        pages_data, toc, body_font, unique_fonts = extract_raw_lines(pdf_path)
        if not pages_data:
            print(f"⚠️ Could not extract data from {pdf_filename}.")
            return

        title, outline = "Untitled Document", []
        # A reliable TOC is the best source of truth.
        # Heuristic: if TOC has a decent number of entries, use it.
        if toc and len(toc) > 3:
            title, outline = detector.detect_headings_via_toc(toc)
        else:
            print("⚠️ TOC unreliable or absent. Falling back to ML model.")
            title, outline = detector.predict(pages_data, body_font, unique_fonts)

        output_filename = os.path.splitext(pdf_filename)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        generate_json_output(title, outline, output_path)

    except Exception as e:
        print(f"❌ ERROR processing {pdf_filename}: {e}", flush=True)

def main():
    start_time = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize the detector once
    detector = HeadingDetector()
    if not detector.model:
        print("Halting execution due to missing model file.")
        return
        
    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDFs found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(pdf_files)} PDF(s). Starting processing...")
    for pdf_file in pdf_files:
        process_single_pdf(pdf_file, detector)

    end_time = time.time()
    print(f"\n✅ Processing complete in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()