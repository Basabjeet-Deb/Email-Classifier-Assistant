# Email Classifier Assistant - Project Structure

## 📁 Core Files

### Backend (Python/FastAPI)
```
backend/
├── api/
│   └── routes.py                    # API endpoints
├── models/
│   ├── keyword_classifier.py        # Rule-based classifier
│   ├── tfidf_classifier_robust.py   # ML classifier (primary)
│   └── zero_shot_classifier.py      # Transformer fallback (disabled)
├── services/
│   ├── classification_service.py    # Orchestrates classifiers
│   ├── gmail_service.py             # Gmail API integration
│   └── self_learning_service.py     # Auto-retraining system
├── utils/
│   ├── email_processor.py           # Email feature extraction
│   └── robust_preprocessor.py       # Text cleaning for ML
├── caching/
│   └── lru_cache.py                 # Prediction caching
├── metrics/
│   └── tracker.py                   # Performance tracking
└── config.py                        # Configuration

server_v2.py                         # Main server entry point
```

### Frontend (React/Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx          # Login page
│   │   ├── ModernSidebar.jsx        # Navigation
│   │   ├── Navbar.jsx               # Top bar
│   │   ├── EmailTableEnhanced.jsx   # Email list
│   │   ├── EmailDetails.jsx         # Email preview
│   │   ├── Settings.jsx             # Settings page
│   │   ├── Analytics.jsx            # Analytics dashboard
│   │   ├── AIInsightsDashboard.jsx  # AI insights
│   │   └── ...                      # Other components
│   ├── api/
│   │   └── client.js                # API client
│   ├── hooks/
│   │   ├── useEmails.js             # Email data hook
│   │   └── useAnalytics.js          # Analytics hook
│   ├── App.jsx                      # Main app
│   └── main.jsx                     # Entry point
├── package.json
└── vite.config.js
```

### Data & Models
```
data/
└── feedback_dataset.csv             # User feedback for retraining

models/
└── tfidf_classifier.pkl             # Trained ML model

email_intent_dataset_5000.csv        # Training dataset
```

### Configuration
```
credentials.json                     # Gmail OAuth credentials
requirements.txt                     # Python dependencies
runtime.txt                          # Python version
Procfile                            # Deployment config
render.yaml                         # Render deployment
```

## 🚀 Key Scripts

### Training
- `retrain_robust_model.py` - Retrain ML model with robust preprocessing

### Documentation
- `README.md` - Project overview
- `SELF_LEARNING_GUIDE.md` - Self-learning system guide
- `ROBUST_MODEL_SUMMARY.md` - Model training details
- `PROJECT_STRUCTURE.md` - This file

## 🎯 Active Components

### Classification Pipeline
1. **Cache Check** - Check if email already classified
2. **TF-IDF Classifier** (Primary) - Robust ML model
3. **Keyword Classifier** - Rule-based validation
4. **Hybrid Decision** - Combine both for best results

### Self-Learning System
1. **Feedback Collection** - User corrections stored
2. **Automatic Retraining** - Triggers at 50 samples
3. **Model Update** - Combines feedback with training data
4. **Continuous Improvement** - Gets better over time

## 📊 Model Performance

- **Test Accuracy:** 100%
- **Average Confidence:** 99.92% (on test data)
- **Real-World Confidence:** 75-85% (with calibration)
- **Features:** 9,178 (word + char ngrams)
- **Training Samples:** 6,000

## 🔧 Configuration

Edit `backend/config.py`:
- `FEEDBACK_RETRAIN_THRESHOLD = 50` - Samples for auto-retrain
- `MIN_FEEDBACK_FOR_RETRAIN = 10` - Minimum for manual retrain
- `USE_ZERO_SHOT = False` - Disable transformer (saves RAM)

## 🗑️ Removed Files

The following files were removed as they're no longer needed:
- `server.py` - Old server (replaced by server_v2.py)
- `main.py` - Duplicate entry point
- `database.py` - Unused database module
- `backend/models/tfidf_classifier.py` - Old classifier
- `backend/models/tfidf_classifier_structured.py` - Intermediate version
- `backend/models/tfidf_classifier_improved.py` - Intermediate version
- `backend/services/feedback_service.py` - Old feedback service
- `test_self_learning.py` - Test script
- `test_tfidf_model.py` - Test script
- `verify_integration.py` - Test script
- Various markdown documentation files (consolidated)

## 📝 Notes

- Use `server_v2.py` as the main entry point
- Frontend runs on port 5173
- Backend runs on port 8000
- Model file: `models/tfidf_classifier.pkl`
- Feedback data: `data/feedback_dataset.csv`
