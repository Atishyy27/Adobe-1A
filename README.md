# PDF Outline Extractor - Adobe Hackathon 2025 (Round 1A)

## 🚀 Project Overview

This project is our solution for Round 1A of the Adobe India Hackathon 2025: "Connecting the Dots." The core challenge is to build a robust system that can parse any given text-based PDF and intelligently extract its hierarchical structure—specifically the document title and a nested outline of its headings (H1, H2, H3).

Our solution is engineered not just as a simple script, but as a resilient, multi-layered document intelligence engine. It is designed to handle a wide variety of document layouts and formatting styles with high accuracy, providing a solid foundation for the subsequent, more complex challenges of the hackathon.

## ✨ Core Features

* **Hybrid, Multi-Layered Strategy:** Our engine doesn't rely on a single technique. It uses a sophisticated three-tier fallback system (TOC -> ML Model -> Clustering) to ensure the highest possible accuracy for any given document.
* **High-Precision ML Detection:** At its core, the system leverages a powerful, pre-trained Document Image Transformer (DiT) model fine-tuned on the massive DocLayNet dataset, allowing it to understand document layouts visually.
* **Intelligent Typographical Analysis:** We use K-Means clustering as a smart refiner to analyze the document's unique font styles, automatically identifying the hierarchy of headings without hardcoded rules.
* **Table of Contents as Ground Truth:** The engine is smart enough to recognize and prioritize the document's built-in Table of Contents (TOC) as the most reliable source of truth when available.
* **Fully Dockerized & Portable:** The entire application is containerized with Docker, ensuring it runs consistently and meets the submission requirements of the hackathon.

## 🛠 Our Approach: The Three-Layered Shield

To achieve maximum robustness, we designed a hybrid strategy that combines the best of explicit metadata, visual layout analysis, and statistical style analysis. The system intelligently chooses the best method for each document.

### Tier 1: Table of Contents (The Ground Truth)
The first and most trusted layer is the PDF's own embedded Table of Contents.
* **How it works:** The engine first inspects the PDF for a valid TOC using PyMuPDF's `doc.get_toc()` method.
* **Why it's best:** If a substantial TOC exists, it provides a perfectly structured, author-intended outline with levels, text, and page numbers. In this case, our engine uses it directly and the process concludes, guaranteeing accuracy.

### Tier 2: ML-Powered Visual Detection (The Visual Expert)
If the TOC is missing or unreliable, the engine falls back to its core—a powerful vision-based model.
* **How it works:** Each PDF page is converted into an image and fed into a pre-trained Document Image Transformer (DiT) model. This model scans the page visually and draws bounding boxes around elements it identifies as `Title` or `Section-header`.
* **Why it's powerful:** This approach is not fooled by simple font sizes. It understands context, whitespace, and positioning, allowing it to correctly identify headings even in complex multi-column layouts.

### Tier 3: K-Means Clustering (The Style Analyst)
The final layer serves to refine the output from the ML model. The ML model tells us *what* is a heading; K-Means helps us determine *which level* (H1, H2, H3) it is.
* **How it works:** We collect all the font sizes used throughout the document. K-Means clustering is then used to group these sizes into distinct categories (e.g., a cluster for 12pt body text, a cluster for 16pt headings, a cluster for 24pt titles).
* **Why it's smart:** This allows the system to learn the document's specific typographical hierarchy on the fly. It then uses this learned hierarchy to assign the correct `H1`, `H2`, or `H3` level to the headings identified by the ML model in Tier 2.

## 💻 Technology Stack

* **Core Logic:** Python 3.10
* **PDF Parsing:** PyMuPDF (fitz)
* **ML Model:** Hugging Face Transformers library loading a pre-trained `microsoft/dit-base-finetuned-on-doclaynet`.
* **ML Framework:** PyTorch (CPU version)
* **Style Analysis:** Scikit-learn (for K-Means Clustering) & NumPy
* **Containerization:** Docker

## 📂 Project Structure



.
├── dit-model/              \# Stores the pre-trained ML model files (offline use)
├── input/                  \# Input PDFs are placed here
├── output/                 \# Generated JSON outlines are saved here
├── src/
│   ├── clustering\_analyzer.py  \# Logic for K-Means font style analysis
│   ├── heading\_detector.py   \# The main hybrid engine (TOC -\> ML -\> K-Means)
│   ├── json\_generator.py     \# Utility to format and save the final JSON
│   └── ...
├── main.py                 \# Main script to orchestrate the entire process
├── Dockerfile              \# Instructions to build the Docker container
└── requirements.txt        \# Python dependencies

`

## ⚙ Setup and Execution

### Prerequisites
* Docker Desktop installed and running.
* Git for version control.

### 1. Model Setup (One-Time Manual Step)
Our system uses a powerful pre-trained model which is not stored in the Git repository due to its size.

* Create a folder named `dit-model` in the project root.
* Download the model files from [this Hugging Face repository](https://huggingface.co/microsoft/dit-base-finetuned-on-doclaynet/tree/main).
* Place the following files inside the `dit-model` folder:
    * `config.json`
    * `pytorch_model.bin`
    * `preprocessor_config.json`

### 2. Build the Docker Image
This command packages the application and all its dependencies. The first build will take a long time (20-40 mins) as it downloads large libraries like PyTorch. Subsequent builds will be very fast.

bash
docker build -t adobe-hack-hybrid .
`

### 3\. Run the Application

Place your PDF files inside the `input` folder. Then, run the following command to start the container. It will automatically process all PDFs and save the JSON results in the `output` folder.

**For Windows (Command Prompt/PowerShell):**

bash
docker run --rm -v "%cd%/input:/app/input" -v "%cd%/output:/app/output" adobe-hack-hybrid


**For macOS/Linux:**

bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" adobe-hack-hybrid


## 展望 Future Work (Hint for Round 1B)

This robust structural analysis engine serves as the perfect foundation for Round 1B's persona-driven intelligence. The next steps involve integrating semantic understanding:

1.  **Content Chunking:** Group the text under each extracted heading.
2.  **Semantic Embedding:** Use a lightweight sentence-transformer model to generate vector embeddings for each content chunk.
3.  **Persona Matching:** Generate an embedding for the user persona and their "job-to-be-done."
4.  **Similarity Search:** Use cosine similarity to find and rank the document sections most relevant to the user's query.

## 🧑‍💻 Team Members

  * Atishay Jain
  * Dilpreet Singh Gill
  * Saloni Jain


```