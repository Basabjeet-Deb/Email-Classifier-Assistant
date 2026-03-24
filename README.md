# 📧 Email Classifier Assistant

> An intelligent email classification system that automatically organizes inbox messages using machine learning and natural language processing.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Technology Stack](#technology-stack)
- [Performance Metrics](#performance-metrics)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

Email Classifier Assistant is a full-stack machine learning application that demonstrates how AI can be applied to solve real-world productivity challenges. The system automatically categorizes incoming emails into five distinct categories:

- **Important** - Urgent messages requiring immediate attention
- **Transactional** - Receipts, confirmations, and order updates
- **Promotional** - Marketing emails and promotional offers
- **Social** - Social media notifications and updates
- **Spam** - Unwanted or suspicious messages

This project showcases a complete ML pipeline from data preprocessing to model deployment, including a modern web interface for real-time email classification and analytics.

---

## 🔍 Problem Statement

Modern email users face significant challenges:

- **Volume Overload**: Average professionals receive 100+ emails daily
- **Time Waste**: Manual email sorting consumes 20-30 minutes per day
- **Missed Priorities**: Important messages get buried in promotional clutter
- **Context Switching**: Constant interruptions reduce productivity

**Solution**: An automated classification system that intelligently organizes emails, allowing users to focus on what matters most.

---

## ✨ Key Features

### 1. Hybrid Classification System
Combines machine learning with rule-based validation for improved accuracy:
- **TF-IDF + LinearSVC** for primary classification
- **Keyword matching** for validation and confidence boosting
- **Ensemble decision logic** that leverages both approaches

### 2. Self-Learning Feedback Loop
- Users can correct misclassifications through the UI
- System automatically retrains when sufficient feedback is collected (50+ samples)
- Continuous improvement from real-world usage patterns

### 3. Real Gmail Integration
- Secure OAuth 2.0 authentication
- Direct Gmail API integration for fetching emails
- Bulk operations (archive, delete) on classified emails

### 4. Comprehensive Analytics Dashboard
- Real-time classification metrics
- Category distribution visualization
- Temporal patterns (daily/hourly trends)
- Model performance tracking

### 5. Production-Ready Architecture
- RESTful API with FastAPI
- Modern React frontend with responsive design
- SQLite database for analytics persistence
- Caching layer for improved performance

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Inbox   │  │Analytics │  │ Settings │  │ Feedback │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI + Python)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer: Authentication, Email Ops, Analytics     │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐        │
│  │   Gmail    │   │     ML     │   │  Database  │        │
│  │    API     │   │  Pipeline  │   │  (SQLite)  │        │
│  └────────────┘   └────────────┘   └────────────┘        │
└─────────────────────────────────────────────────────────────┘
```
### Component Breakdown

**Frontend Layer**
- React 18 with Vite for fast development
- TanStack Query for efficient data fetching
- Recharts for data visualization
- Tailwind CSS for responsive design

**Backend Layer**
- FastAPI for high-performance API endpoints
- Gmail API client for email operations
- ML classification service with caching
- Self-learning service for model retraining

**Data Layer**
- SQLite for analytics and feedback storage
- Trained model persistence (pickle format)
- OAuth token management

---

## 🤖 Machine Learning Pipeline

### 1. Data Preprocessing

```python
# Email cleaning and normalization
- Remove HTML tags and tracking pixels
- Extract structured features (links, numbers, currency)
- Normalize text (lowercase, special characters)
- Limit body length to first 120 words
```

### 2. Feature Engineering

**Dual Vectorization Approach:**
- **Word-level TF-IDF**: Captures semantic meaning (1-2 grams, 15K features)
- **Character-level TF-IDF**: Handles spelling variations (3-5 grams, 8K features)
- **Combined feature space**: ~9,285 dimensions

**Structured Features:**
```python
- Domain extraction (e.g., amazon.com → DOMAIN_AMAZON)
- Subject weighting (3x repetition for importance)
- Metadata tokens (HAS_LINK, HAS_PRICE, HAS_DATE)
```

### 3. Model Architecture

**Primary Classifier: LinearSVC**
- Fast training and inference
- Effective for high-dimensional text data
- Calibrated with sigmoid for probability estimates

**Hybrid Decision Logic:**
```python
if keyword_confidence >= 0.85 and ml_confidence >= 0.75:
    # Both agree with high confidence
    final_confidence = min(ml_confidence + 0.08, 0.99)
    return ml_category, final_confidence
else:
    # Use ML prediction (most accurate)
    return ml_category, ml_confidence
```

### 4. Training Process

```bash
# Initial training
python retrain_robust_model.py

# Training data composition:
- 5,000 labeled emails (base dataset)
- 2,500 synthetic realistic emails
- 15+ user feedback samples
- Total: ~7,515 training samples
```

### 5. Self-Learning Loop

```
User Feedback → CSV Storage → Threshold Check (50 samples)
                                      ↓
                              Automatic Retraining
                                      ↓
                              Model Update → Deployment
```

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| FastAPI | REST API framework |
| scikit-learn | ML algorithms |
| NumPy/SciPy | Numerical computing |
| Google API Client | Gmail integration |
| SQLite | Analytics database |
| Uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| TanStack Query | Data fetching |
| Recharts | Data visualization |
| Tailwind CSS | Styling |
| Axios | HTTP client |

### Machine Learning
| Component | Implementation |
|-----------|----------------|
| Feature Extraction | TF-IDF (word + char n-grams) |
| Classifier | LinearSVC with calibration |
| Preprocessing | Custom robust pipeline |
| Validation | Keyword-based rules |

---

## 📊 Performance Metrics

### Model Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Dataset Accuracy** | 94-98% | On held-out test set |
| **Real-World Confidence** | 75-85% | Average on Gmail emails |
| **Feature Dimensions** | ~9,285 | Word + character n-grams |
| **Training Samples** | 7,515 | Including synthetic data |
| **Processing Speed** | 20-50ms | Per email classification |
| **Model Size** | ~860KB | Compressed pickle file |

### Classification Breakdown (Real Gmail Data)

```
Category          Precision    Recall    F1-Score
─────────────────────────────────────────────────
Important         0.82         0.79      0.80
Transactional     0.88         0.85      0.86
Promotional       0.91         0.94      0.92
Social            0.76         0.73      0.74
Spam              0.95         0.89      0.92
─────────────────────────────────────────────────
Weighted Avg      0.87         0.86      0.86
```

### System Performance

- **API Response Time**: <100ms (with caching)
- **Concurrent Users**: Tested up to 10 simultaneous
- **Memory Footprint**: ~100MB (without transformer models)
- **Database Size**: <5MB for 1000 classified emails

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Gmail API credentials ([Get them here](https://console.cloud.google.com/))

### Step 1: Clone Repository

```bash
git clone https://github.com/Basabjeet-Deb/Email-Classifier-Assistant.git
cd Email-Classifier-Assistant
```

### Step 2: Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Place your Gmail OAuth credentials
# Save as credentials.json in the root directory
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

### Step 4: Configuration

Create a `.env` file in the root directory (optional):

```env
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:5173
```

---

## 💻 Usage

### Running Locally

**Terminal 1 - Start Backend:**
```bash
python server.py
```
Backend will run on: `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will run on: `http://localhost:5173`

### First-Time Setup

1. Open `http://localhost:5173` in your browser
2. Click "Connect Gmail" and authorize the application
3. Click "Scan Emails" to fetch and classify your inbox
4. View results in the email table
5. Correct any misclassifications using the feedback button
6. Check analytics dashboard for insights

### Retraining the Model

**Manual retraining:**
```bash
python retrain_robust_model.py
```

**Automatic retraining:**
- System automatically retrains after collecting 50 feedback samples
- Progress tracked in the Settings page

---

## 📁 Project Structure

```
Email-Classifier-Assistant/
├── backend/
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── models/
│   │   ├── tfidf_classifier_robust.py  # Main ML model
│   │   ├── keyword_classifier.py       # Rule-based classifier
│   │   └── zero_shot_classifier.py     # Optional transformer
│   ├── services/
│   │   ├── classification_service.py   # Hybrid classification
│   │   ├── gmail_service.py            # Gmail API integration
│   │   └── self_learning_service.py    # Feedback & retraining
│   ├── utils/
│   │   ├── email_processor.py          # Feature extraction
│   │   └── robust_preprocessor.py      # Text cleaning
│   ├── caching/
│   │   └── lru_cache.py                # Classification cache
│   └── metrics/
│       └── tracker.py                  # Performance tracking
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── EmailTableEnhanced.jsx  # Main email view
│       │   ├── Analytics.jsx           # Dashboard
│       │   ├── EmailDetails.jsx        # Email viewer
│       │   └── Settings.jsx            # Configuration
│       ├── hooks/
│       │   ├── useEmails.js            # Email data hook
│       │   └── useAnalytics.js         # Analytics hook
│       └── api/
│           └── client.js               # API client
├── models/
│   └── tfidf_classifier.pkl            # Trained model
├── data/
│   └── feedback_dataset.csv            # User feedback
├── server.py                            # Main entry point
├── database.py                          # SQLite operations
├── retrain_robust_model.py             # Training script
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## 📚 API Documentation

### Authentication

**Start OAuth Flow**
```http
GET /api/auth/login
```

**Check Connection Status**
```http
GET /api/status
```

### Email Operations

**Scan and Classify Emails**
```http
POST /api/scan
Content-Type: application/json

{
  "account_id": "user@gmail.com",
  "max_results": 50,
  "query": "in:inbox"
}
```

**Submit Feedback**
```http
POST /api/feedback
Content-Type: application/json

{
  "email_id": "abc123",
  "sender": "sender@example.com",
  "subject": "Email subject",
  "body": "Email body",
  "predicted_category": "Promotional",
  "correct_category": "Important",
  "confidence": 0.75
}
```

### Analytics

**Get Analytics Data**
```http
GET /api/analytics/{account_id}?days=30
```

**Get System Metrics**
```http
GET /api/metrics
```

For complete API documentation, visit: `http://localhost:8000/docs` (when server is running)

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-language support (currently English-optimized)
- [ ] Custom category creation by users
- [ ] Email threading and conversation grouping
- [ ] Priority scoring within categories
- [ ] Integration with other email providers (Outlook, Yahoo)
- [ ] Mobile application (React Native)
- [ ] Advanced NLP with transformer models (BERT, RoBERTa)
- [ ] Automated email responses for common queries
- [ ] Calendar integration for meeting detection

### Technical Improvements
- [ ] Kubernetes deployment configuration
- [ ] Redis caching for distributed systems
- [ ] PostgreSQL migration for production scale
- [ ] A/B testing framework for model comparison
- [ ] Explainable AI features (LIME, SHAP)
- [ ] Real-time classification with WebSockets

---

## 🤝 Contributing

Contributions are welcome! This project is designed as a learning resource and demonstration system.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **scikit-learn** for providing robust ML algorithms
- **FastAPI** for the excellent web framework
- **Google** for Gmail API access
- **React community** for UI components and tools

---

## 📧 Contact

**Basabjeet Deb**
- GitHub: [@Basabjeet-Deb](https://github.com/Basabjeet-Deb)
- Email: basabjeet.557@gmail.com

---

## 🎓 Project Status

**Status**: Prototype / Demonstration System

This project is designed to showcase:
- Full-stack machine learning application development
- Real-world ML pipeline implementation
- Integration with external APIs (Gmail)
- Self-learning systems with feedback loops
- Modern web development practices

**Note**: This is a demonstration system built for educational and portfolio purposes. For production deployment, additional considerations around security, scalability, and compliance would be necessary.

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**
