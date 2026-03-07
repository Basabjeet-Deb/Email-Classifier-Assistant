# Self-Learning Email Classifier System

## Overview

The email classifier now includes a **self-learning system** that automatically improves the model based on user feedback. When users correct misclassifications, the system collects this feedback and automatically retrains the model when enough samples are gathered.

## Key Features

✅ **Automatic Feedback Collection**
- Captures full email context (sender, subject, body)
- Stores feedback in CSV and database
- Tracks prediction confidence and classifier used

✅ **Structured Data Format**
- Uses domain + subject + body structure
- Improves model context understanding
- Better feature extraction for training

✅ **Automatic Retraining**
- Triggers when feedback threshold is reached (default: 50 samples)
- Runs in background (non-blocking)
- Combines feedback with existing training data
- Thread-safe to prevent concurrent retraining

✅ **Feedback Statistics**
- Track total feedback samples
- Monitor category distribution
- See samples until next retrain
- View retraining history

✅ **Manual Retraining**
- Trigger retraining on-demand via API
- Useful for immediate model updates
- Requires minimum 10 feedback samples

## Configuration

Edit `backend/config.py` to customize:

```python
# Self-Learning Configuration
SELF_LEARNING_ENABLED = True  # Enable automatic retraining
FEEDBACK_RETRAIN_THRESHOLD = 50  # Retrain after N feedback samples
MIN_FEEDBACK_FOR_RETRAIN = 10  # Minimum feedback samples needed
```

## API Endpoints

### 1. Submit Feedback
**POST** `/api/feedback`

Submit user correction for a misclassified email.

**Request Body:**
```json
{
  "email_id": "abc123",
  "sender": "orders@amazon.com",
  "subject": "Your order has shipped",
  "body": "Track your package here...",
  "predicted_category": "Promotional",
  "correct_category": "Transactional",
  "confidence": 0.75,
  "classifier_used": "tfidf"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback received. Thank you for helping improve the classifier!"
}
```

### 2. Get Feedback Statistics
**GET** `/api/feedback/stats`

Get current feedback statistics and self-learning status.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_samples": 25,
    "category_distribution": {
      "Promotional": 10,
      "Transactional": 8,
      "Social": 5,
      "Important": 2
    },
    "samples_until_retrain": 25,
    "last_retrain_count": 0,
    "retrain_threshold": 50
  }
}
```

### 3. Manual Retraining
**POST** `/api/retrain-tfidf`

Manually trigger model retraining (requires 10+ feedback samples).

**Response:**
```json
{
  "status": "success",
  "message": "TF-IDF classifier retraining initiated"
}
```

## How It Works

### 1. User Corrects Classification
When a user sees a misclassified email, they can provide the correct category through the frontend.

### 2. Feedback Storage
The system stores:
- Email metadata (sender, subject, body)
- Predicted vs. correct category
- Confidence score
- Classifier used
- Timestamp

### 3. Automatic Retraining Trigger
When feedback count reaches the threshold (default: 50 samples):
- System automatically starts retraining in background
- Loads all feedback data
- Combines with existing training data
- Retrains TF-IDF model with structured features
- Saves updated model

### 4. Model Improvement
The retrained model:
- Learns from user corrections
- Improves accuracy on similar emails
- Increases prediction confidence
- Better handles edge cases

## Retraining Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load Feedback Data                                       │
│    - Read from feedback_dataset.csv                         │
│    - Extract (sender, subject, body, correct_category)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Load Existing Training Data                              │
│    - email_intent_dataset_5000.csv                          │
│    - combined_data.csv (Kaggle dataset)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Combine Datasets                                          │
│    - Merge feedback with existing data                      │
│    - Total: 88,000+ training samples                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Create Structured Features                               │
│    - Format: DOMAIN_<domain> SUBJECT_<subject> BODY_<body>  │
│    - Example: "DOMAIN_amazon.com SUBJECT_order shipped..."  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Train TF-IDF Model                                        │
│    - TfidfVectorizer: 12000 features, bigrams               │
│    - LogisticRegression: C=2, max_iter=2000                 │
│    - 80/20 train/test split                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Evaluate & Save                                           │
│    - Test accuracy: ~99%                                     │
│    - Average confidence: ~90%                                │
│    - Save to models/tfidf_classifier.pkl                    │
└─────────────────────────────────────────────────────────────┘
```

## Testing

Run the test script to verify the self-learning system:

```bash
python test_self_learning.py
```

This will:
- Initialize the self-learning service
- Show current feedback statistics
- Simulate adding feedback samples
- Display updated statistics
- Explain retraining triggers

## Frontend Integration

To integrate with the frontend, update the feedback submission:

```javascript
// When user corrects a classification
const submitFeedback = async (email, correctCategory) => {
  const response = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email_id: email.id,
      sender: email.sender,
      subject: email.subject,
      body: email.snippet,
      predicted_category: email.category,
      correct_category: correctCategory,
      confidence: email.confidence,
      classifier_used: email.classifier_used
    })
  });
  
  const data = await response.json();
  console.log(data.message);
};

// Get feedback statistics
const getFeedbackStats = async () => {
  const response = await fetch('/api/feedback/stats');
  const data = await response.json();
  return data.stats;
};
```

## Monitoring

### Check Feedback Progress
```bash
curl http://localhost:8000/api/feedback/stats
```

### View Feedback Data
```bash
cat data/feedback_dataset.csv
```

### Trigger Manual Retraining
```bash
curl -X POST http://localhost:8000/api/retrain-tfidf
```

## Best Practices

1. **Collect Diverse Feedback**
   - Encourage users to correct various types of misclassifications
   - Aim for balanced feedback across all categories

2. **Monitor Retraining**
   - Check logs for retraining success/failure
   - Review model performance after retraining

3. **Adjust Threshold**
   - Lower threshold (e.g., 25) for faster adaptation
   - Higher threshold (e.g., 100) for more stable updates

4. **Backup Models**
   - Keep previous model versions
   - Allow rollback if retraining degrades performance

5. **Validate Feedback**
   - Consider adding feedback validation
   - Filter out spam or invalid corrections

## Troubleshooting

### Retraining Not Triggering
- Check feedback count: `GET /api/feedback/stats`
- Verify threshold in `backend/config.py`
- Check logs for errors

### Low Model Performance After Retraining
- Ensure feedback quality is good
- Check category distribution balance
- Consider increasing minimum feedback requirement

### Database Errors
- Verify `data/feedback_dataset.csv` exists
- Check CSV format matches expected columns
- Ensure write permissions on data directory

## Future Enhancements

- [ ] A/B testing for model versions
- [ ] Confidence-based feedback prioritization
- [ ] Active learning (request feedback on uncertain predictions)
- [ ] Model performance tracking over time
- [ ] Feedback quality scoring
- [ ] Multi-model ensemble with feedback routing

## Summary

The self-learning system ensures your email classifier continuously improves based on real-world usage. As users correct misclassifications, the model learns and adapts, becoming more accurate over time without manual intervention.

**Key Metrics:**
- Current accuracy: ~99%
- Average confidence: ~90%
- Retraining threshold: 50 samples
- Minimum for manual retrain: 10 samples
- Training data: 88,000+ emails
