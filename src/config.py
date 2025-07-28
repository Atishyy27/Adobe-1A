# src/config.py
INPUT_DIR = "./input"
OUTPUT_DIR = "./output"
MODELS_DIR = "./models"
MODEL_FILE = f"{MODELS_DIR}/heading_classifier.joblib"

# The features our model will use
FEATURE_COLUMNS = [
    'font_size', 'is_bold', 'is_italic', 'x_pos_normalized', 'y_pos_normalized',
    'line_height', 'space_above', 'space_below', 'line_length_chars',
    'word_count', 'is_all_caps', 'starts_with_number', 'is_centered',
    'font_size_ratio_to_avg', 'is_different_font'
]