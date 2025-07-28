# train.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
import joblib
import glob

# Import your own project modules
from src.pdf_parser import extract_raw_lines
from src.feature_extractor import calculate_features
from src.config import MODEL_FILE, MODELS_DIR

# --- Configuration ---
TRAINING_DATA_DIR = "./training_pdfs/" # Directory with your sample PDFs
LABELS_FILE = "./training_labels.csv" # The file we will create and label

def create_features_for_labeling():
    """Extracts features from all PDFs and saves them to a CSV for manual labeling."""
    all_features = []
    print("🚀 Starting feature extraction from PDFs...")
    pdf_files = glob.glob(os.path.join(TRAINING_DATA_DIR, "*.pdf"))
    if not pdf_files:
        print(f"❌ No PDFs found in {TRAINING_DATA_DIR}. Please add some sample PDFs to train on.")
        return

    for pdf_path in pdf_files:
        print(f"  - Processing {os.path.basename(pdf_path)}")
        pages_data, _, body_font, unique_fonts = extract_raw_lines(pdf_path)
        if not pages_data:
            continue
        
        for i, page_lines in enumerate(pages_data):
            if not page_lines:
                continue
                
            features_df = calculate_features(page_lines, body_font, unique_fonts)
            # Add identifiers and the text itself to make labeling easier
            features_df['pdf_name'] = os.path.basename(pdf_path)
            features_df['page_num'] = i + 1
            features_df['text'] = [line['text'] for line in page_lines]
            all_features.append(features_df)
    
    if not all_features:
        print("❌ No features were extracted. Check your PDFs.")
        return
        
    master_df = pd.concat(all_features, ignore_index=True)
    master_df['label'] = 'Body' # Default label
    
    # Save for manual labeling
    # Reorder columns to make labeling easy: put identifiers and text first.
    cols = ['pdf_name', 'page_num', 'text', 'label'] + [c for c in master_df.columns if c not in ['pdf_name', 'page_num', 'text', 'label']]
    master_df[cols].to_csv(LABELS_FILE, index=False, encoding='utf-8')
    print(f"\n✅ Feature extraction complete. Please manually label the 'label' column in '{LABELS_FILE}'.")
    print("   Use labels: Title, H1, H2, H3, Body")


def train_model():
    """Trains the classifier and saves the final model."""
    print("\n🚀 Starting model training...")
    try:
        df = pd.read_csv(LABELS_FILE)
    except FileNotFoundError:
        print(f"❌ Labels file not found: '{LABELS_FILE}'. Please run the feature extraction and labeling step first.")
        return

    # Drop rows that were not labeled (or keep them as 'Body')
    df.dropna(subset=['label'], inplace=True)
    if len(df[df['label'] != 'Body']) < 10:
        print("⚠️ Warning: Very few headings have been labeled. The model may not be accurate.")
        print("   Please label more lines as Title, H1, H2, or H3 in the CSV file.")

    X = df.drop(columns=['pdf_name', 'page_num', 'text', 'label'])
    y = df['label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"  - Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    
    # We use SGDClassifier (Logistic Regression) as it's very fast and effective.
    # class_weight='balanced' helps with the fact that most lines are 'Body' text.
    model = SGDClassifier(loss='log_loss', random_state=42, class_weight='balanced', alpha=1e-4)
    model.fit(X_train, y_train)

    # Evaluate
    predictions = model.predict(X_test)
    print("\n--- Model Evaluation Report ---")
    print(classification_report(y_test, predictions))
    print("----------------------------")

    # Save the trained model
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model trained and saved successfully to '{MODEL_FILE}'")


if __name__ == '__main__':
    # This is a two-step process.
    # 1. Run once to create the CSV.
    # 2. Open the CSV and label your data.
    # 3. Comment out the first function and run again to train the model.
    
    # --- Step 1: Create the CSV file for labeling ---
    # create_features_for_labeling()
    
    # --- Step 2: After labeling the CSV, run this ---
    train_model()