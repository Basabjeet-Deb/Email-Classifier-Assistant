"""
API routes for the email classifier backend.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List

from backend.services.classification_service import get_classification_service
from backend.config import ENVIRONMENT, BACKEND_URL, FRONTEND_URL
from backend.services.gmail_service import GmailService
from backend.services.self_learning_service import get_self_learning_service
import database as db


app = FastAPI(title="Email Classifier Assistant API v2.0")

# CORS Configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://email-classifier-frontend-mnj8.onrender.com",
    "https://email-classifier-assistant.onrender.com",
    FRONTEND_URL,
]

if ENVIRONMENT == "production":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ScanRequest(BaseModel):
    account_id: str = "default"
    max_results: int = 50
    query: str = "in:inbox category:promotions OR is:unread"

class DeleteRequest(BaseModel):
    account_id: str
    message_ids: List[str]

class FeedbackRequest(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    predicted_category: str
    correct_category: str
    confidence: float = 0.0
    classifier_used: str = "Unknown"


# Initialize services
classification_service = get_classification_service()
gmail_service = GmailService()
self_learning_service = get_self_learning_service()


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "Email Classifier Assistant API",
        "version": "2.0.0",
        "status": "running",
        "memory_optimized": True,
        "docs": "/docs"
    }


@app.get("/api/status")
def get_status():
    """Check Gmail authentication status."""
    try:
        connected_accounts = gmail_service.get_connected_accounts()
        
        if connected_accounts:
            return {"status": "connected", "accounts": connected_accounts}
        return {"status": "disconnected", "accounts": []}
    except Exception as e:
        return {"status": "error", "accounts": [], "error": str(e)}


@app.get("/api/auth/login")
def auth_login():
    """Start OAuth flow - returns authorization URL."""
    try:
        redirect_uri = f"{BACKEND_URL}/api/auth/callback"
        authorization_url, state = gmail_service.create_auth_flow(redirect_uri)
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
    except Exception as e:
        import traceback
        print(f"ERROR in auth_login: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/callback")
def auth_callback(code: str, state: str = None):
    """Handle OAuth callback from Google."""
    try:
        email_address = gmail_service.handle_auth_callback(code, BACKEND_URL)
        
        print(f"Successfully authenticated: {email_address}")
        
        return RedirectResponse(url=f"{FRONTEND_URL}?auth=success&email={email_address}")
    except Exception as e:
        import traceback
        print(f"ERROR in auth_callback: {str(e)}")
        print(traceback.format_exc())
        return RedirectResponse(url=f"{FRONTEND_URL}?auth=error&message={str(e)}")


@app.post("/api/scan")
def scan_emails(req: ScanRequest):
    """Scan and classify emails."""
    try:
        # Get Gmail service
        service = gmail_service.authenticate(req.account_id)
        if not service:
            raise HTTPException(status_code=401, detail=f"Failed to authenticate with Gmail for {req.account_id}")
        
        # Fetch emails
        emails = gmail_service.fetch_emails(service, req.max_results, req.query)
        
        # Classify each email
        classified_emails = []
        for email in emails:
            result = classification_service.classify_email(
                email['subject'],
                email['sender'],
                email['snippet']
            )
            
            classified_email = {
                **email,
                'category': result['category'],
                'confidence': result['confidence'],
                'classifier_used': result['classifier_used'],
                'classification_time_ms': result['processing_time_ms']
            }
            classified_emails.append(classified_email)
        
        # Store in database
        db.store_batch_classifications(req.account_id, classified_emails)
        
        # Get metrics
        metrics = classification_service.get_system_metrics()
        
        return {
            "status": "success",
            "total_count": len(classified_emails),
            "emails": classified_emails,
            "processing_time_ms": sum(e['classification_time_ms'] for e in classified_emails),
            "metrics": metrics
        }
    except Exception as e:
        import traceback
        print(f"ERROR in scan_emails: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/delete")
def delete_emails(request: DeleteRequest):
    """Delete emails."""
    try:
        service = gmail_service.authenticate(request.account_id)
        if not service:
            raise HTTPException(status_code=401, detail=f"Failed to authenticate")
        
        if not request.message_ids:
            return {"status": "success", "deleted_count": 0}
        
        count = gmail_service.delete_messages(service, request.message_ids)
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/archive")
def archive_emails(request: DeleteRequest):
    """Archive emails."""
    try:
        service = gmail_service.authenticate(request.account_id)
        if not service:
            raise HTTPException(status_code=401, detail=f"Failed to authenticate")
        
        if not request.message_ids:
            return {"status": "success", "archived_count": 0}
        
        count = gmail_service.archive_messages(service, request.message_ids)
        return {"status": "success", "archived_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
def get_metrics():
    """Get system metrics."""
    try:
        metrics = classification_service.get_system_metrics()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/category-stats")
def get_category_stats():
    """Get category distribution statistics."""
    try:
        stats = classification_service.get_category_stats()
        return {
            "status": "success",
            "categories": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for classification correction."""
    try:
        self_learning_service.store_feedback(
            email_id=request.email_id,
            sender=request.sender,
            subject=request.subject,
            body=request.body,
            predicted_category=request.predicted_category,
            correct_category=request.correct_category,
            confidence=request.confidence,
            classifier_used=request.classifier_used
        )
        
        return {
            "status": "success",
            "message": "Feedback received. Thank you for helping improve the classifier!"
        }
    except Exception as e:
        import traceback
        print(f"ERROR in submit_feedback: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/{account_id}")
def get_analytics(account_id: str, days: int = 30):
    """Get analytics data."""
    try:
        analytics = db.get_analytics_summary(account_id, days)
        insights = db.get_insights(account_id)
        return {
            "status": "success",
            "analytics": analytics,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/retrain-tfidf")
def retrain_tfidf():
    """Manually trigger TF-IDF classifier retraining."""
    try:
        success = self_learning_service.manual_retrain()
        if success:
            return {
                "status": "success",
                "message": "TF-IDF classifier retraining initiated"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initiate retraining")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback/stats")
def get_feedback_stats():
    """Get feedback statistics and self-learning status."""
    try:
        stats = self_learning_service.get_feedback_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
