import os
import time
from multiprocessing import Pool, cpu_count

# Import all the modules
from src.pdf_parser import extract_text_blocks
from src.heading_detector import detect_headings
from src.json_generator import generate_json_output

# Define paths for local testing
INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

def process_single_pdf(pdf_path):
    """The processing pipeline for one PDF."""
    print(f"Processing: {os.path.basename(pdf_path)}")

    # 1. Parse the PDF
    pages_data = extract_text_blocks(pdf_path)
    if not pages_data:
        return

    # 2. Detect the headings
    title, outline = detect_headings(pages_data)

    # 3. Generate the JSON output
    filename = os.path.basename(pdf_path)
    output_filename = os.path.splitext(filename)[0] + ".json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    generate_json_output(title, outline, output_path)

def main():
    """Main function to find and process all PDFs."""
    start_time = time.time()

    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDFs found in '{INPUT_DIR}'. Please add a PDF to test.")
        return

    print(f"Found {len(pdf_files)} PDF(s). Starting processing...")

    # Use multiprocessing for performance
    with Pool(processes=cpu_count()) as pool:
        pool.map(process_single_pdf, pdf_files)

    print(f"\nProcessing complete in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()