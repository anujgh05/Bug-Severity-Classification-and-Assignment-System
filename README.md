
# Bug Severity Classification and Assignment System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791)
![React](https://img.shields.io/badge/React-19.2%2B-61dafb)

**An intelligent automated bug triage system that leverages machine learning to classify bug severity and intelligently route tickets to developers based on expertise and workload.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Docs](#-api-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

The **Bug Severity Classification and Assignment System** is an intelligent triage engine that automates the process of classifying bug reports by severity and assigning them to the most appropriate developers. Built with machine learning and modern web technologies, this system optimizes software maintenance workflows by:

- **Automating severity classification** using trained machine learning models
- **Intelligently routing bugs** based on developer expertise and workload
- **Enforcing quality gates** with confidence thresholds for manual review
- **Providing role-based dashboards** for users, developers, and administrators
- **Tracking workload metrics** to prevent developer burnout

---

## 🚀 Features

### Core Capabilities

- **🤖 Intelligent Severity Classification**
  - Machine learning-powered bug classification (Low, Medium, High)
  - TF-IDF feature extraction with dimensionality reduction
  - Confidence-based prediction with automatic quality gates
  - Low-confidence predictions flagged for manual review

- **🎯 Smart Bug Assignment**
  - Semantic similarity-based routing using cosine distance
  - Expertise-aware developer matching
  - Dynamic load balancing to prevent burnout
  - Workload metric tracking per developer

- **👥 Role-Based Access Control**
  - **Users**: Submit bugs and track their status
  - **Developers**: View and manage assigned tickets
  - **Administrators**: Triage dashboard, override classifications, manage users

- **📊 Analytics & Dashboard**
  - Real-time bug status tracking
  - Developer workload visualization
  - Severity distribution metrics
  - Classification confidence metrics

- **🔒 Security Features**
  - Password hashing with SHA-256
  - Role-based access control
  - Protected API endpoints
  - CORS-enabled for frontend integration

---

## 🏗️ Architecture

### System Design

The system follows a **Three-Tier Architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                        │
│              React / Vite Frontend Dashboard                │
│          (Bug Submission, Triage, User Management)          │
└────────────────┬────────────────────────────┬────────────────┘
                 │ HTTP/REST                  │
                 ↓                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│              FastAPI Backend Server (api.py)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • User Authentication & Authorization                 │ │
│  │  • Bug Prediction Pipeline (Classification)            │ │
│  │  • Bug Assignment Pipeline (Routing & Load Balancing)  │ │
│  │  • Database Query Orchestration                        │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────┬────────────────┘
                 │ SQL Queries                │
                 ↓                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│         PostgreSQL Database (Multi-table Schema)            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Users Table (users, roles, credentials)             │ │
│  │  • Bugs Table (submissions, severity, status)          │ │
│  │  • Developers Table (expertise, workload metrics)      │ │
│  │  • Audit Logs (classification history, overrides)      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### ML Pipeline Components

```
Input Bug Description
         ↓
    [Text Preprocessing]
    - Tokenization
    - Lowercasing
    - Stop word removal
         ↓
    [Feature Extraction]
    - TF-IDF Vectorization
    - Dimensionality Reduction (TruncatedSVD)
         ↓
    [Classification Model]
    - Random Forest Classifier
    - Calibration (Platt Scaling)
         ↓
    [Confidence Gate]
    - 55% Confidence Threshold
    - Low confidence → Manual Review
         ↓
    [Assignment Pipeline]
    - Semantic Similarity Matching
    - Developer Workload Analysis
    - Load-balanced Routing
         ↓
    Assigned Developer + Severity
```

---

## 📋 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **PostgreSQL**: 13 or higher
- **RAM**: Minimum 4GB (8GB recommended for model training)
- **Disk Space**: 2GB for dependencies and artifacts

### Required Accounts/Services

- PostgreSQL database server (local or remote)
- (Optional) Cloud deployment services for production

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/anujgh05/Bug-Severity-Classification-and-Assignment-System
cd Bug-Severity-Classification-and-Assignment-System
```

### 2. Backend Setup

#### Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Create PostgreSQL Database

```sql
CREATE DATABASE "Minor Project";
```

#### Initialize Database Schema

```bash
python -c "from src.components.db_init import initialize_database; initialize_database()"
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Train the ML Model (Optional)

To train the model on your dataset:

```bash
python -c "from src.pipeline.train_pipeline import TrainPipeline; pipeline = TrainPipeline(); pipeline.initiate_train_pipeline()"
```

---

## ⚙️ Configuration

### Backend Configuration

Edit `api.py` to configure database connection:

```python
CONN_INFO = "host=localhost dbname='Minor Project' user=postgres password=YOUR_PASSWORD port=5432"
```

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/Minor Project
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173
SECRET_KEY=your_secret_key_here
CONFIDENCE_THRESHOLD=0.55
```

### Frontend Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`. Update `frontend/src/api/axios.js` if running on a different port.

---

## 🚀 Usage

### Start the Backend Server

```bash
# Make sure virtual environment is activated
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Build Frontend for Production

```bash
cd frontend
npm run build
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "user"
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username_or_email": "john_doe",
  "password": "securepass123",
  "role": "user"
}
```

### Bug Management Endpoints

#### Submit Bug Report

```http
POST /api/v1/bugs/submit
Content-Type: application/json

{
  "summary": "Login button not working",
  "description": "The login button on the homepage is unresponsive when clicked...",
  "reporter_user_id": 1
}
```

Response:
```json
{
  "bug_id": 101,
  "summary": "Login button not working",
  "predicted_severity": "High",
  "confidence": 0.87,
  "assigned_developer_id": 5,
  "status": "assigned"
}
```

#### Get User Bugs

```http
GET /api/v1/bugs/user/{user_id}
```

#### Get Developer Assigned Bugs

```http
GET /api/v1/bugs/developer/{developer_id}
```

#### Override Bug Classification (Admin)

```http
POST /api/v1/bugs/{bug_id}/override
Content-Type: application/json

{
  "severity": "Critical",
  "assigned_developer_id": 3
}
```

### Complete API Reference

For complete API documentation with all endpoints, parameters, and response schemas, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
bug-severity-system/
├── artifacts/                      # Trained ML models and datasets
│   ├── model.pkl                   # Serialized Random Forest model
│   ├── tfidf_vectorizer.pkl        # TF-IDF vectorizer
│   ├── train.csv                   # Training dataset
│   ├── test.csv                    # Test dataset
│   └── cleaned_bug_dataset.csv     # Preprocessed data
│
├── src/                            # Source code
│   ├── __init__.py
│   ├── exception.py                # Custom exception handling
│   ├── logger.py                   # Logging configuration
│   ├── utils.py                    # Utility functions
│   │
│   ├── components/                 # Data processing components
│   │   ├── __init__.py
│   │   ├── data_ingestion.py       # Load raw bug dataset
│   │   ├── data_transformation.py  # TF-IDF vectorization, preprocessing
│   │   ├── model_trainer.py        # Random Forest model training
│   │   ├── db_init.py              # Database schema initialization
│   │   └── figures.py              # Data visualization utilities
│   │
│   └── pipeline/                   # ML pipelines
│       ├── __init__.py
│       ├── train_pipeline.py       # End-to-end training pipeline
│       ├── prediction_pipeline.py  # Severity classification inference
│       └── assignment_pipeline.py  # Semantic routing & load balancing
│
├── frontend/                       # React Vite frontend
│   ├── public/
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── BugForm.jsx         # Bug submission form
│   │   │   ├── TriageTable.jsx     # Bug triage dashboard
│   │   │   ├── DevBoard.jsx        # Developer dashboard
│   │   │   ├── ConfidenceMeter.jsx # Confidence visualization
│   │   │   └── Layout.jsx          # Common layout wrapper
│   │   │
│   │   ├── pages/                  # Page components
│   │   │   ├── LoginPage.jsx
│   │   │   ├── UserLoginPage.jsx
│   │   │   ├── AdminLoginPage.jsx
│   │   │   ├── DeveloperLoginPage.jsx
│   │   │   ├── SubmitBugPage.jsx
│   │   │   ├── UserBugsPage.jsx
│   │   │   ├── DeveloperTasksPage.jsx
│   │   │   └── AdminTriagePage.jsx
│   │   │
│   │   ├── context/                # React Context
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   │
│   │   ├── api/                    # API integration
│   │   │   └── axios.js            # Axios instance with interceptors
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── logs/                           # Application logs
│
├── api.py                          # Main FastAPI application
├── setup.py                        # Package configuration
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .gitignore
```

---

## 🔌 Technologies Used

### Backend
- **FastAPI** - Modern async Python web framework
- **PostgreSQL** - Relational database
- **scikit-learn** - Machine learning library
- **NLTK** - Natural language processing
- **psycopg2** - PostgreSQL adapter

### Frontend
- **React 19.2** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - CSS framework
- **Lucide React** - Icon library

### ML/Data Processing
- **scikit-learn** - SVM, Random Forest, TF-IDF
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **NLTK** - Text preprocessing
- **beautifulsoup4** - HTML parsing

---

## 📊 Model Details

### Classification Model
- **Algorithm**: Random Forest Classifier (500 estimators)
- **Feature Engineering**: TF-IDF vectorization
- **Dimensionality Reduction**: TruncatedSVD (300 components)
- **Calibration**: Platt Scaling for probability estimation
- **Confidence Threshold**: 55% (predictions below this are flagged for review)

### Assignment Algorithm
- **Method**: Cosine Similarity-based semantic matching
- **Considerations**:
  - Developer expertise areas
  - Current workload (penalty for ≥ 5 active tickets)
  - Load balancing penalty: Δ = 0.15

---

## 🧪 Testing

### Run Unit Tests

```bash
# Test backend components
python -m pytest tests/ -v
```

### Test API Endpoints

Use the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- Try out endpoints directly in the browser

---

## 🔐 Security Considerations

- Passwords are hashed using SHA-256 with a salt
- CORS is configured for frontend origin
- Role-based access control is enforced
- SQL injection prevention through parameterized queries
- Input validation on all API endpoints

---

## 📈 Performance Optimization

- Database queries use indexed columns
- TruncatedSVD reduces model inference time
- Frontend uses Vite for fast build and HMR
- API responses are optimized with selective field retrieval
- Model artifacts are serialized for fast loading

---

## 🐛 Troubleshooting

### Database Connection Error
```
Error: could not connect to server: Connection refused
```
**Solution**: Ensure PostgreSQL is running and credentials are correct in `CONN_INFO`

### Model Not Found
```
Error: artifacts/model.pkl not found
```
**Solution**: Train the model using the train pipeline before running predictions

### Frontend Cannot Connect to API
```
Error: CORS policy: blocked by CORS
```
**Solution**: Verify the FastAPI server is running on `http://localhost:8000` and update `CORS` settings if needed

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change the port or kill the existing process using that port

---

## 📝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Write unit tests for new features

---


## 🙏 Acknowledgments

- scikit-learn team for the excellent ML library
- FastAPI documentation and community
- React team for the UI framework
- PostgreSQL for reliable data storage

---

## 📞 Support

For issues, questions, or suggestions, please:
- Open an [GitHub Issue](https://github.com/anujgh05/Bug-Severity-Classification-and-Assignment-System/issues)
- Email: anuj2005.ghimire@gmail.com

---


[⬆ Back to top](#bug-severity-classification-and-assignment-system)

</div>
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
git clone https://github.com/anujgh05/Bug-Severity-Classification-and-Assignment-System
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