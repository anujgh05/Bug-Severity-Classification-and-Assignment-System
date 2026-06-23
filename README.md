

---

# Bug Severity Classification and Assignment System

An automated, data-driven Intelligent Triage Engine designed to optimize software maintenance workflows. The system leverages machine learning to classify incoming bug reports into distinct severity tiers and utilizes advanced semantic vector mapping to automatically route tasks to the most suitable developers while dynamically balancing active workloads.

## 🚀 Core Features

* **Automated Severity Classification:** Implements a Support Vector Machine (SVM) pipeline using TF-IDF feature engineering to classify bug descriptions into four severity metrics (`Low`, `Medium`, `High`, `Critical`).
* **Confidence-Based Gatekeeper (DSS):** Utilizes Platt Scaling probability estimations to enforce a minimum $55\%$ operational threshold. Ambiguous, low-confidence entries are flagged for manual review to preserve data integrity.
* **Dynamic Semantic Routing:** Maps incoming text requests against available development pools via **Cosine Similarity** matrix comparisons to ensure precise expertise alignment.
* **Dynamic Load Balancing:** Implements a structural heuristic step-penalty ($\Delta = 0.15$) on overloaded nodes ($\ge 5$ active tickets) to prevent developer burnout and minimize pipeline bottlenecks.
* **Relational Integrity Core:** Backed by an atomic, multi-table PostgreSQL transaction layer tracking ticket states, team workload metrics, and permanent historical allocations.

---

## 🏗️ System Architecture

The system is engineered as an integrated **Three-Tier Architecture** that enforces a strict separation of concerns between raw mathematical modeling, server routing, and structural data storage.

```text
  [ Presentation Layer ]          [ Application Layer ]            [ Data Layer ]
  ┌────────────────────┐          ┌────────────────────┐        ┌──────────────────┐
  │  React / HTML UI   │ ◄──────► │ Flask / FastAPI    │ ◄────► │  PostgreSQL DB   │
  │  (Triage Dashboard)│  (REST)  │ (Predict Pipeline) │ (SQL)  │ (Bugs & Devs tabs)│
  └────────────────────┘          └────────────────────┘        └──────────────────┘

```

1. **Presentation Layer:** A responsive dashboard for users to submit bug entries and triage managers to supervise flagged tasks.
2. **Application Layer:** An isolated processing backend orchestrating text normalization, TF-IDF transformations, SVM soft-classification boundaries, and localized corpus vectorization.
3. **Data Layer:** A reliable PostgreSQL instance handling relational schema enforcement, primary key B-Tree indexing, and transaction tracking.

> ⚠️ **Development Status Note on Frontend:** The current implementation of `app.py` serves strictly as a **temporary backend prototype and functional proof-of-concept**. It renders basic HTML elements to demonstrate data flows, pipeline logs, and database entry generation. Building the decoupled, comprehensive production frontend (e.g., using a modern component-based framework like React) is planned for the next implementation phase.

---

## 📁 Repository Structure

```text
├── artifacts/                  # Trained serialized assets (.pkl, .csv)
├── src/
│   ├── components/
│   │   ├── data_ingestion.py   # Pipeline raw content importing
│   │   ├── data_transformation.py # Feature extraction and token clean sweeps
│   │   └── model_trainer.py    # SVM model training script
│   ├── pipeline/
│   │   ├── predict_pipeline.py # Classification inference logic
│   │   └── assignment_pipeline.py # Cosine similarity allocation matching
│   ├── exception.py            # Global custom system exceptions tracker
│   ├── logger.py               # Runtime operational activity logging
│   └── utils.py                # Serialized model read/write helpers
├── app.py                      # Temporary web routing backend execution engine
├── requirements.txt            # System dependencies list
└── README.md                   # Technical project overview documentation

```

---

## 🛠️ Installation & Setup

### 1. Prerequisites

Ensure you have the following environments configured on your machine:

* Python 3.8+
* Anaconda / Miniconda Environment Manager
* PostgreSQL Database Engine

### 2. Environment Configuration

Clone the repository and spin up an isolated virtual environment:

```bash
# Clone the workspace
git clone https://github.com/yourusername/bug-triage-system.git
cd bug-triage-system

# Create and activate environment
conda create -p venv python=3.9 -y
conda activate venv/

# Install engineering dependencies
pip install -r requirements.txt

```

### 3. Database Initialisation

Ensure your PostgreSQL instance is running locally. Modify the `CONN_INFO` variable parameters inside your configuration initialization scripts to match your user credentials (`user`, `password`, `port`), then seed the tables:

```bash
python src/utils/db_init.py

```

*This handles conditional execution to generate `developer_profiles`, `bug_reports`, and `assignment_history` schemas and sets up initial dummy developer pool configurations.*

### 4. Booting up the Application Server

Fire up the server pipeline instance:

```bash
python app.py

```

Navigate to `http://127.0.0.1:5000/` in your web browser to access the temporary submission dashboard interface.

---

## 📊 Database Schema Blueprint

The application shifts away from flat file layouts to guarantee transactional consistency using three cross-referenced entities:

* **`developer_profiles`**: Tracks workforce identities, raw semantic competence text parameters (`expertise_profile`), operational status flags, and cumulative backlog ticket numbers.
* **`bug_reports`**: Captures incoming user text structures, target classifications, probability scalars, allocation tags, and cosine alignment percentages.
* **`assignment_history`**: Maintains historical audit entries tracking whether tasks were executed via automated pipelines or manual administrator interventions.

---

## 🔬 Core Methodologies Implemented

* **Text Normalization:** Lowercasing, punctuation filtering, stopword elimination, and lemmatization using NLTK parsing engines.
* **Term Frequency-Inverse Document Frequency (TF-IDF):** Transforms unstructured raw text matrices into standard quantitative configurations.
* **Support Vector Machine (SVM):** Utilizes radial basis function kernels coupled with Platt Scaling mapping loops to enable probability confidence thresholds.
* **Cosine Proximity Function:** Captures semantic directionality alignment between localized multi-dimensional vectors.

---