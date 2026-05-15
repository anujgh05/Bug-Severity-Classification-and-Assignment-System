
# Bug Severity Classification and Assignment System

This project is a machine learning-based tool designed to automate the triage process for open-source projects. It specifically focuses on **classifying the severity** of incoming bug reports and **assigning the most suitable developer** based on historical performance.

## 🚀 Project Overview

The system utilizes data fetched from the **Mozilla Bugzilla API**. It processes raw bug summaries and descriptions to:

1. **Classify Severity**: Map reports into four categories: `Critical`, `High`, `Medium`, and `Low` using a **Support Vector Machine (SVM)**.
2. **Recommend Developers**: Suggest experts using **Cosine Similarity** based on their previous bug-fixing history.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/anujgh05/Bug-Severity-Classification-and-Assignment-System.git
cd "Bug-Severity-Classification-and-Assignment-System"

```


2. **Create a Virtual Environment:**
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate

```


3. **Install Dependencies:**
```bash
pip install -r requirements.txt

```


4. **Prepare NLTK Data:**
The system uses NLTK for text processing. Run these in your Python terminal if they don't download automatically:
```python
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

```



---

## 🏗️ Current Pipeline Progress

The project follows a modular component-based architecture:

* ✅ **Data Ingestion**: Fetches 3,000+ bug reports via API and performs an 80/20 train-test split.
* ✅ **Data Transformation**:
* Cleans text (stopword removal, lemmatization).
* Maps 8+ Bugzilla severity labels to a standardized 4-level hierarchy.
* Converts text to numerical vectors using **TF-IDF Vectorization**.


* ⏳ **Model Training**: *[In Progress]*
* ⏳ **Prediction Pipeline**: *[To be implemented]*

---

## 📝 Guidance for Contributors (Model Trainer & Predictor)

If you are implementing the remaining components, please follow these specifications:

### 1. Model Trainer (`src/components/model_trainer.py`)

* **Input**: Expects `train_arr` and `test_arr` (NumPy arrays) from the transformation step.
* **Data Format**:
* **Features**: All columns except the last one (TF-IDF features).
* **Target**: The very last column (Categorical Severity).


* **Model**: Implement a **Support Vector Machine (SVM)** with an RBF kernel.
* **Output**: Save the trained model as `artifacts/model.pkl`.

### 2. Prediction Pipeline (`src/pipeline/predict_pipeline.py`)

* This should be a standalone class that loads `model.pkl` and `preprocessor.pkl`.
* It must take a raw `summary` and `description` string, transform them using the loaded preprocessor, and return the predicted severity category.

---

## 📁 Directory Structure

```text
├── artifacts/           # Local data and serialized models (Git Ignored)
├── logs/                # Execution logs (Git Ignored)
├── src/
│   ├── components/      # Ingestion, Transformation, Trainer
│   ├── pipeline/        # Train and Predict pipelines
│   ├── logger.py        # Custom logging setup
│   └── exception.py     # Custom error handling
├── app.py               # Flask/Streamlit Web App (Planned)
└── requirements.txt     # Project dependencies

```

---

## 🏃 How to Run the Pipeline

To trigger the current workflow (Ingestion + Transformation), run:

```bash
python src/pipeline/train_pipeline.py

```
