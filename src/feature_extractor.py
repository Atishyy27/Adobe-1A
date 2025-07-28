# src/feature_extractor.py
import re
import pandas as pd
from .config import FEATURE_COLUMNS

def calculate_features(lines_on_page, body_font, unique_fonts):
    """Calculates a feature vector for each line on a page."""
    
    if not lines_on_page:
        return pd.DataFrame(columns=FEATURE_COLUMNS)

    # Calculate average font size for the page
    avg_font_size = sum(line['font_size'] for line in lines_on_page) / len(lines_on_page)
    
    features_list = []
    for i, line in enumerate(lines_on_page):
        prev_line = lines_on_page[i-1] if i > 0 else None
        next_line = lines_on_page[i+1] if i < len(lines_on_page) - 1 else None
        
        page_width = line['page_dims']['width']
        page_height = line['page_dims']['height']

        # --- Feature Engineering ---
        features = {
            'font_size': line['font_size'],
            'is_bold': 1 if line['is_bold'] else 0,
            'is_italic': 1 if line['is_italic'] else 0,
            'x_pos_normalized': line['bbox'][0] / page_width,
            'y_pos_normalized': line['bbox'][1] / page_height,
            'line_height': line['bbox'][3] - line['bbox'][1],
            'space_above': (line['bbox'][1] - prev_line['bbox'][3]) if prev_line else page_height * 0.1,
            'space_below': (next_line['bbox'][1] - line['bbox'][3]) if next_line else page_height * 0.1,
            'line_length_chars': len(line['text']),
            'word_count': len(line['text'].split()),
            'is_all_caps': 1 if line['text'].isupper() and len(line['text']) > 1 else 0,
            'starts_with_number': 1 if re.match(r"^\s*(\d+(\.\d+)*|[A-Z])\.?\s", line['text']) else 0,
            'is_centered': 1 if abs((line['bbox'][0] + line['bbox'][2])/2 - page_width/2) < page_width * 0.1 else 0,
            'font_size_ratio_to_avg': line['font_size'] / avg_font_size if avg_font_size > 0 else 1,
            'is_different_font': 1 if line['font_name'] != body_font and len(unique_fonts) > 1 else 0
        }
        features_list.append(features)
        
    df = pd.DataFrame(features_list)
    # Ensure all columns are present, filling missing with 0
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
            
    return df[FEATURE_COLUMNS] # Return in a consistent order