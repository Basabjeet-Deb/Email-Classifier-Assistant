# 📧 Email Classifier Assistant

AI-powered email classification system with self-learning capabilities. Automatically categorizes emails into Important, Transactional, Promotional, Social, and Spam using machine learning.

## ✨ Features

- **Smart Classification** - ML-based email categorization with 75-85% confidence
- **Self-Learning** - Automatically improves from user feedback
- **Gmail Integration** - OAuth authentication and API integration
- **Real-Time Analytics** - Track classification performance
- **Bulk Actions** - Archive/delete multiple emails at once
- **Responsive UI** - Modern React interface with dark theme

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Gmail API credentials

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd EmailClassifierAssistant
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Setup Gmail OAuth**
- Place `credentials.json` in the root directory
- Get credentials from [Google Cloud Console](https://console.cloud.google.com/)

### Running the Application

1. **Start Backend Server**
```bash
python server_v2.py
```
Backend runs on: http://localhost:8000

2. **Start Frontend (in new terminal)**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173

3. **Open Browser**
Navigate to http://localhost:5173

## 📊 Classification Categories

- **Important** - Urgent emails requiring immediate attention
- **Transactional** - Receipts, orders, confirmations
- **Promotional** - Marketing, sales, offers
- **Social** - Social media notifications
- **Spam** - Unwanted or suspicious emails

## 🤖 How It Works

### Classification Pipeline
1. **Cache Check** - Fast lookup for previously classified emails
2. **TF-IDF Classifier** - Primary ML model (robust preprocessing)
3. **Keyword Classifier** - Rule-based validation
4. **Hybrid Decision** - Combines both for optimal results

### Self-Learning System
1. User corrects misclassifications via feedback
2. System collects feedback with full email context
3. Automatic retraining triggers at 50 samples
4. Model improves continuously from real-world data

## 🎯 Model Performance

- **Test Accuracy:** 99.93%
- **Real-World Confidence:** 75-85%
- **Features:** 9,285 (word + character ngrams)
- **Training Data:** 7,515 emails (5K original + 15 feedback + 2.5K synthetic)
- **Processing Speed:** ~20-50ms per email

## 📁 Project Structure

```
EmailClassifierAssistant/
├── backend/              # Python backend
│   ├── api/             # API routes
│   ├── models/          # ML classifiers
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # UI components
│       ├── hooks/       # React hooks
│       └── api/         # API client
├── models/              # Trained ML models
├── data/                # Training & feedback data
├── server_v2.py         # Main server
└── retrain_robust_model.py  # Model training
```

## 🔧 Configuration

Edit `backend/config.py`:

```python
# Self-Learning
FEEDBACK_RETRAIN_THRESHOLD = 50  # Auto-retrain trigger
MIN_FEEDBACK_FOR_RETRAIN = 10    # Manual retrain minimum

# Model
USE_ZERO_SHOT = False            # Disable transformer (saves RAM)

# Categories
CATEGORIES = ['Important', 'Transactional', 'Promotional', 'Social', 'Spam']
```

## 📚 API Endpoints

### Authentication
- `GET /api/auth/login` - Start OAuth flow
- `GET /api/auth/callback` - OAuth callback
- `GET /api/status` - Check connection status

### Email Operations
- `POST /api/scan` - Scan and classify emails
- `POST /api/delete` - Delete emails
- `POST /api/archive` - Archive emails

### Feedback & Training
- `POST /api/feedback` - Submit classification correction
- `GET /api/feedback/stats` - Get feedback statistics
- `POST /api/retrain-tfidf` - Manually trigger retraining

### Analytics
- `GET /api/metrics` - Get system metrics
- `GET /api/category-stats` - Get category distribution
- `GET /api/analytics/{account_id}` - Get analytics data

## 🛠️ Development

### Retrain Model
```bash
python retrain_robust_model.py
```

### Run Tests
```bash
python -m pytest tests/
```

### Build Frontend
```bash
cd frontend
npm run build
```

## 📦 Deployment

### Render (Recommended)
1. Connect GitHub repository
2. Use `render.yaml` for configuration
3. Set environment variables
4. Deploy

### Manual Deployment
1. Build frontend: `cd frontend && npm run build`
2. Set `ENVIRONMENT=production`
3. Run: `python server_v2.py`

## 🔐 Security

- OAuth 2.0 for Gmail authentication
- No password storage
- Token-based authentication
- CORS protection
- Rate limiting

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review `SELF_LEARNING_GUIDE.md` for self-learning details

## 🎉 Acknowledgments

- Built with FastAPI, React, and scikit-learn
- Gmail API integration
- TF-IDF + LinearSVC for classification
- Self-learning system for continuous improvement

---

**Status:** ✅ Production Ready

**Version:** 2.0.0

**Last Updated:** March 2026
