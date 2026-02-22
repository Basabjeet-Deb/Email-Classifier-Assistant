import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

import main as email_core
import database as db

app = FastAPI(title="Email Classifier Assistant API")

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

@app.post("/api/auth")
def auth_new_account():
    """Explicitly triggers the OAuth flow to add a new account."""
    service = email_core.authenticate_gmail("default")
    if service:
        # The main logic automatically renames the default token to the real email
        return {"status": "success", "message": "Account added."}
    raise HTTPException(status_code=401, detail="Failed to authenticate.")

@app.post("/api/scan")
def scan_emails(req: ScanRequest):
    """Triggers the inbox scanner for a specific account with enhanced metrics."""
    service = email_core.authenticate_gmail(req.account_id)
    if not service:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Gmail for {req.account_id}.")
    
    try:
        result = email_core.process_emails(service, max_results=req.max_results, query=req.query)
        
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

if __name__ == "__main__":
    print("Starting FastAPI Backend Server...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
