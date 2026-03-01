# Troubleshooting Guide

## Common Deployment Issues

### 1. PyTorch Version Error

**Error:**
```
ERROR: Could not find a version that satisfies the requirement torch==2.2.0
```

**Cause:** Python version mismatch. PyTorch 2.2.0 doesn't support Python 3.14+.

**Solution:**
1. Ensure `runtime.txt` exists with: `python-3.11.9`
2. In Render dashboard, set environment variable:
   - `PYTHON_VERSION`: `3.11.9`
3. Redeploy the service

**Files to check:**
- `runtime.txt` - Should contain `python-3.11.9`
- `.python-version` - Should contain `3.11.9`
- `requirements.txt` - Should have `torch>=2.0.0` (not `torch==2.2.0`)

---

### 2. Build Timeout

**Error:**
```
Build exceeded time limit
```

**Cause:** ML models are large and take time to install.

**Solution:**
1. This is normal for first deployment
2. Wait 10-15 minutes
3. If it fails, try again (Render caches dependencies)

---

### 3. Service Won't Start

**Error:**
```
Service failed to start
```

**Cause:** Missing environment variables or incorrect start command.

**Solution:**
1. Check Render logs for specific error
2. Verify start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Ensure environment variables are set:
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`

---

### 4. OAuth Authentication Fails

**Error:**
```
redirect_uri_mismatch
```

**Cause:** Google OAuth redirect URIs not updated.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: APIs & Services → Credentials
3. Click your OAuth 2.0 Client ID
4. Add to Authorized redirect URIs:
   ```
   https://your-backend-url.onrender.com
   https://your-frontend-url.onrender.com
   ```
5. Save and wait 5 minutes for Google to update

---

### 5. CORS Error

**Error:**
```
Access to fetch at 'https://backend.com/api/...' from origin 'https://frontend.com' has been blocked by CORS policy
```

**Cause:** Frontend URL not in CORS allowed origins.

**Solution:**
1. Check `server.py` CORS configuration
2. Ensure `ENVIRONMENT=production` is set (allows all origins in production)
3. Or add specific frontend URL to `allowed_origins` list

---

### 6. 502 Bad Gateway

**Error:**
```
502 Bad Gateway
```

**Cause:** Service is starting up (cold start) or crashed.

**Solution:**
1. Wait 30-60 seconds for cold start
2. Check Render logs for crash errors
3. Verify all dependencies installed correctly
4. Check RAM usage (free tier: 512MB limit)

---

### 7. Classification is Very Slow

**Issue:** First classification takes 2-3 minutes.

**Cause:** ML models loading on-demand.

**Solution:**
1. This is normal for first classification
2. Subsequent classifications use cache (fast)
3. Consider upgrading to paid tier for more RAM
4. Or use smaller model (see Performance Tips below)

---

### 8. Database Resets After Deployment

**Issue:** Analytics data disappears after redeployment.

**Cause:** Free tier doesn't persist storage.

**Solution:**
1. Use Render's persistent disk (paid feature)
2. Or use external database (PostgreSQL)
3. Or accept that data resets (for personal use)

---

### 9. Service Keeps Sleeping

**Issue:** App takes 30-60 seconds to respond after inactivity.

**Cause:** Free tier services sleep after 15 minutes.

**Solution:**
1. Use [UptimeRobot](https://uptimerobot.com/) to ping every 14 minutes
2. Set up monitor for: `https://your-backend.onrender.com/api/status`
3. Or upgrade to paid tier (no sleep)

---

### 10. Out of Memory Error

**Error:**
```
MemoryError or Killed
```

**Cause:** ML models exceed 512MB RAM limit.

**Solution:**
1. Use smaller model:
   ```python
   # In main.py
   model="typeform/distilbert-base-uncased-mnli"  # Smaller
   ```
2. Reduce batch size:
   ```python
   batch_size=8  # Instead of 32
   ```
3. Or upgrade to paid tier (more RAM)

---

## Performance Tips

### Reduce Model Size

Edit `main.py`:
```python
# Use smaller model
_ml_pipeline = pipeline(
    "zero-shot-classification", 
    model="typeform/distilbert-base-uncased-mnli",  # 250MB instead of 800MB
    device=-1,
    batch_size=8
)
```

### Increase Cache Size

Edit `main.py`:
```python
# Increase cache for better performance
if len(_classification_cache) > 5000:  # Instead of 1000
```

### Optimize for Free Tier

1. **Reduce dependencies**: Remove unused packages
2. **Use CDN**: Vercel for frontend (faster)
3. **Enable compression**: Gzip responses
4. **Lazy load models**: Only load when needed

---

## Checking Logs

### Render
1. Go to your service dashboard
2. Click "Logs" tab
3. View real-time logs
4. Look for errors in red

### Railway
1. Click on your service
2. View "Deployments" tab
3. Click on latest deployment
4. View build and runtime logs

### Vercel
1. Go to your project
2. Click "Deployments"
3. Click on latest deployment
4. View "Build Logs" and "Function Logs"

---

## Getting Help

1. **Check logs first**: Most issues show up in logs
2. **Review this guide**: Common issues covered here
3. **Platform docs**: 
   - [Render Docs](https://render.com/docs)
   - [Railway Docs](https://docs.railway.app/)
   - [Vercel Docs](https://vercel.com/docs)
4. **GitHub Issues**: Open an issue with:
   - Error message
   - Platform used
   - Logs (sanitized)
   - Steps to reproduce

---

## Quick Fixes Checklist

- [ ] Python version is 3.11.9 (check `runtime.txt`)
- [ ] All environment variables set correctly
- [ ] OAuth redirect URIs updated in Google Console
- [ ] Start command is correct
- [ ] All files committed and pushed to GitHub
- [ ] Waited 5-10 minutes for first deployment
- [ ] Checked logs for specific errors

---

## Still Having Issues?

1. Try redeploying (sometimes fixes transient issues)
2. Clear build cache and redeploy
3. Check platform status page for outages
4. Contact platform support (they're usually helpful)
5. Open a GitHub issue with details

---

**Most issues are resolved by:**
1. Setting correct Python version (3.11.9)
2. Updating OAuth redirect URIs
3. Waiting for cold start (30-60s)
4. Checking logs for specific errors
