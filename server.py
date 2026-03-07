import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import main as email_core
import database as db

app = FastAPI(title="Email Classifier Assistant API")

# Get environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Enable CORS for frontend
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://email-classifier-frontend-mnj8.onrender.com",  # Your NEW frontend URL
    "https://email-classifier-assistant.onrender.com",  # Your NEW backend URL
    FRONTEND_URL,
]

# In production, allow all origins for simplicity
if ENVIRONMENT == "production":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static directory for our HTML/CSS/JS interface
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class DeleteRequest(BaseModel):
    account_id: str
    message_ids: list[str]

class ScanRequest(BaseModel):
    account_id: str = "default"
    max_results: int = 50
    query: str = "in:inbox category:promotions OR is:unread"

class FeedbackRequest(BaseModel):
    email_id: str
    predicted_category: str
    correct_category: str
    email_text: str
    confidence: float = 0.0
    classifier_used: str = "Unknown"

@app.get("/")
def read_index():
    """Serves the main dashboard HTML."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "error": "Dashboard UI not found",
        "message": "The static/index.html file is missing. Please ensure it exists.",
        "api_docs": "Visit /docs for API documentation"
    }

@app.get("/api/status")
def get_status():
    """Check which backend accounts are connected to Gmail."""
    # Look for anything named token_*.json in our directory
    connected_accounts = []
    for file in os.listdir(BASE_DIR):
        if file.startswith("token_") and file.endswith(".json"):
            # strip "token_" and ".json"
            acc_name = file[6:-5]
            if acc_name != "default":
                connected_accounts.append(acc_name)
    
    # Check default if no explicit emails found
    if not connected_accounts and os.path.exists(os.path.join(BASE_DIR, "token_default.json")):
        connected_accounts.append("default")

    if connected_accounts:
        return {"status": "connected", "accounts": connected_accounts}
    return {"status": "disconnected", "accounts": []}

@app.get("/api/auth/login")
def auth_login():
    """Start OAuth flow - returns authorization URL for user to visit."""
    try:
        # Get the backend URL from environment or construct it
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        redirect_uri = f"{backend_url}/api/auth/callback"
        
        flow = email_core.create_oauth_flow(redirect_uri=redirect_uri)
        if not flow:
            raise HTTPException(status_code=500, detail="Failed to create OAuth flow")
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        # Store state in session or return it to frontend
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
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_uri = f"{backend_url}/api/auth/callback"
        
        flow = email_core.create_oauth_flow(redirect_uri=redirect_uri)
        if not flow:
            raise HTTPException(status_code=500, detail="Failed to create OAuth flow")
        
        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Get user's email address
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'default')
        
        # Save credentials
        token_path = os.path.join(BASE_DIR, f'token_{email_address}.json')
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"Successfully authenticated: {email_address}")
        
        # Redirect back to frontend with success
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"{frontend_url}?auth=success&email={email_address}")
        
    except Exception as e:
        import traceback
        print(f"ERROR in auth_callback: {str(e)}")
        print(traceback.format_exc())
        # Redirect to frontend with error
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(url=f"{frontend_url}?auth=error&message={str(e)}")

@app.post("/api/auth")
def auth_new_account():
    """DEPRECATED: Use /api/auth/login instead.
    This endpoint is kept for backward compatibility but returns instructions."""
    return {
        "status": "redirect_required",
        "message": "Please use /api/auth/login to get authorization URL",
        "instructions": "Call GET /api/auth/login to start OAuth flow"
    }

@app.post("/api/scan")
def scan_emails(req: ScanRequest):
    """Triggers the inbox scanner. Uses TF-IDF + LogReg as primary classifier."""
    service = email_core.authenticate_gmail(req.account_id)
    if not service:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Gmail for {req.account_id}.")
    
    try:
        result = email_core.process_emails(
            service, 
            max_results=req.max_results, 
            query=req.query
        )
        
        # Store classifications in database for analytics
        db.store_batch_classifications(req.account_id, result['emails'])
        
        return {
            "status": "success",
            "processed_count": result['total_count'],
            "emails": result['emails'],
            "processing_time_ms": result['processing_time_ms'],
            "metrics": result['metrics']
        }
    except Exception as e:
        import traceback
        print(f"ERROR in scan_emails: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/delete")
def delete_emails(request: DeleteRequest):
    """Deletes a list of emails for a specific account."""
    service = email_core.authenticate_gmail(request.account_id)
    if not service:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Gmail for {request.account_id}.")
    
    if not request.message_ids:
        return {"status": "success", "deleted_count": 0, "message": "No IDs provided."}

    try:
        count = email_core.delete_messages(service, request.message_ids)
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/archive")
def archive_emails(request: DeleteRequest):
    """Archives a list of emails for a specific account by removing inbox label."""
    service = email_core.authenticate_gmail(request.account_id)
    if not service:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Gmail for {request.account_id}.")
    
    if not request.message_ids:
        return {"status": "success", "archived_count": 0, "message": "No IDs provided."}

    try:
        count = email_core.archive_messages(service, request.message_ids)
        return {"status": "success", "archived_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/{account_id}")
def get_analytics(account_id: str, days: int = 30):
    """Get analytics data for the specified account."""
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
    """Retrain the TF-IDF classifier using historical data from database."""
    try:
        success = email_core.retrain_tfidf_from_database()
        if success:
            return {
                "status": "success",
                "message": "TF-IDF classifier retrained successfully using historical data"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to retrain classifier")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    """Store user feedback for classification corrections."""
    try:
        # Store feedback in database for future model improvements
        db.store_feedback(
            email_id=request.email_id,
            predicted_category=request.predicted_category,
            correct_category=request.correct_category,
            email_text=request.email_text,
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
        if success:
            return {
                "status": "success",
                "message": "TF-IDF classifier retrained successfully using historical data"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to retrain classifier")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting FastAPI Backend Server...")
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    uvicorn.run("server:app", host=host, port=port, reload=(ENVIRONMENT == "development"))
