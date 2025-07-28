# src/heading_detector.py
import joblib
from .config import MODEL_FILE, FEATURE_COLUMNS
from .feature_extractor import calculate_features

def clean_text(text):
    """Removes heading numbers and extra whitespace."""
    text = re.sub(r"^\s*(\d+(\.\d+)*|[A-Z])\.?\s*", "", text).strip()
    return re.sub(r'\s+', ' ', text)

class HeadingDetector:
    def __init__(self):
        """Loads the pre-trained model."""
        try:
            self.model = joblib.load(MODEL_FILE)
            print("✅ ML Model loaded successfully.")
        except FileNotFoundError:
            print(f"❌ Model file not found at {MODEL_FILE}. Please run train.py first.")
            self.model = None

    def predict(self, pages_data, body_font, unique_fonts):
        """
        Uses the ML model to predict heading levels for an entire document.
        """
        if not self.model:
            return [], "Untitled Document"

        all_headings = []
        doc_title = "Untitled Document"
        
        # Use first page's most prominent text as a fallback title
        if pages_data and pages_data[0]:
            first_page_lines = pages_data[0]
            if first_page_lines:
                doc_title = max(first_page_lines, key=lambda l: l['font_size'])['text']

        for page_lines in pages_data:
            if not page_lines:
                continue

            # 1. Get features
            features_df = calculate_features(page_lines, body_font, unique_fonts)
            
            # 2. Predict with the model
            if not features_df.empty:
                predictions = self.model.predict(features_df)
                
                # 3. Collect headings
                for line, label in zip(page_lines, predictions):
                    if label in ["H1", "H2", "H3"]:
                        text = clean_text(line["text"])
                        if text:
                            all_headings.append({
                                "level": label,
                                "text": text,
                                "page": line["page_num"]
                            })
                    elif label == "Title":
                        doc_title = line["text"] # Update title if model finds one

        # Deduplicate headings (same text on same page)
        final_headings = []
        seen = set()
        for h in all_headings:
            identifier = (h['text'].lower(), h['page'])
            if identifier not in seen:
                final_headings.append(h)
                seen.add(identifier)

        return doc_title, final_headings

    def detect_headings_via_toc(self, toc):
        """Processes headings from a reliable Table of Contents."""
        print("✅ Using built-in Table of Contents.")
        outline = []
        for level, title, page in toc:
            if level <= 3:
                outline.append({"level": f"H{level}", "text": title, "page": page})
        return "TOC-based Title", outline