# Deployment Guide - Free Hosting

This guide will help you deploy your Email Classifier Assistant to free hosting platforms with a public URL.

## Table of Contents
- [Option 1: Render (Recommended)](#option-1-render-recommended)
- [Option 2: Railway](#option-2-railway)
- [Option 3: Vercel + Render](#option-3-vercel--render)
- [Important Notes](#important-notes)

---

## Option 1: Render (Recommended)

Render offers free hosting for both backend and frontend with automatic HTTPS.

### Free Tier Limits
- 750 hours/month (enough for 1 service running 24/7)
- Spins down after 15 minutes of inactivity
- Cold start: ~30-60 seconds

### Step 1: Prepare Your Repository

1. Push your code to GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy Backend on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `email-classifier-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`

6. Click "Create Web Service"

7. Wait for deployment (5-10 minutes first time)

8. Copy your backend URL: `https://email-classifier-api.onrender.com`

### Step 3: Deploy Frontend on Render

1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `email-classifier-frontend`
   - **Branch**: `main`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. Add Environment Variable:
   - `VITE_API_URL`: `https://email-classifier-api.onrender.com`

5. Click "Create Static Site"

6. Your app will be live at: `https://email-classifier-frontend.onrender.com`

### Step 4: Update Google OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: APIs & Services → Credentials
3. Click your OAuth 2.0 Client ID
4. Add Authorized redirect URIs:
   ```
   https://email-classifier-api.onrender.com
   https://email-classifier-frontend.onrender.com
   ```
5. Save changes

### Step 5: Test Your Deployment

1. Visit: `https://email-classifier-frontend.onrender.com`
2. Click "Get Started"
3. Authenticate with Gmail
4. Start classifying emails!

---

## Option 2: Railway

Railway offers $5 free credit per month (enough for ~500 hours).

### Step 1: Deploy to Railway

1. Go to [Railway](https://railway.app/)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your repository
5. Railway auto-detects Python and deploys

### Step 2: Configure Environment

1. Click on your service
2. Go to "Variables" tab
3. Add:
   - `PORT`: `8000`
   - `ENVIRONMENT`: `production`
   - `PYTHON_VERSION`: `3.11.0`

### Step 3: Get Your URL

1. Go to "Settings" tab
2. Click "Generate Domain"
3. Copy your URL: `https://your-app.railway.app`

### Step 4: Deploy Frontend

1. Create new service in same project
2. Select "Deploy from GitHub repo"
3. Choose `frontend` folder as root
4. Add environment variable:
   - `VITE_API_URL`: `https://your-backend.railway.app`

### Step 5: Update OAuth

Same as Render Step 4, but use Railway URLs.

---

## Option 3: Vercel + Render

Use Vercel for frontend (best performance) and Render for backend.

### Step 1: Deploy Backend on Render

Follow "Option 1: Step 2" above.

### Step 2: Deploy Frontend on Vercel

1. Go to [Vercel](https://vercel.com/)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variable:
   - `VITE_API_URL`: `https://email-classifier-api.onrender.com`

6. Click "Deploy"

7. Your app will be live at: `https://your-app.vercel.app`

### Step 3: Update OAuth

Add Vercel URL to Google OAuth redirect URIs.

---

## Important Notes

### ⚠️ Free Tier Limitations

1. **Cold Starts**: Free services sleep after 15 minutes of inactivity
   - First request after sleep: 30-60 seconds
   - Solution: Use a service like [UptimeRobot](https://uptimerobot.com/) to ping every 14 minutes

2. **ML Models**: Large models (800MB) may cause issues
   - Render free tier: 512MB RAM limit
   - Solution: Models are loaded on-demand, but first classification will be slow

3. **Storage**: SQLite database resets on each deployment
   - Solution: Use Render's persistent disk (paid) or external database

### 🔒 Security Considerations

1. **Credentials File**: 
   - DO NOT commit `credentials.json` to GitHub
   - Upload manually via Render dashboard or use environment variables

2. **Token Files**:
   - Token files won't persist on free tier
   - Users need to re-authenticate after service restarts

3. **HTTPS**:
   - All platforms provide free HTTPS
   - Required for OAuth to work properly

### 🚀 Performance Tips

1. **Reduce Model Size**:
   ```python
   # In main.py, use smaller model:
   _ml_pipeline = pipeline(
       "zero-shot-classification", 
       model="typeform/distilbert-base-uncased-mnli",  # Smaller alternative
       device=-1
   )
   ```

2. **Increase Cache**:
   ```python
   # In main.py, increase cache size:
   if len(_classification_cache) > 5000:  # Increased from 1000
   ```

3. **Use CDN**:
   - Vercel automatically uses CDN for frontend
   - Faster load times globally

### 📊 Monitoring

1. **Render**:
   - Dashboard shows logs, metrics, and uptime
   - Free tier includes basic monitoring

2. **Railway**:
   - Real-time logs and metrics
   - Usage tracking for free credit

3. **Vercel**:
   - Analytics dashboard
   - Performance insights

### 🔄 Continuous Deployment

All platforms support automatic deployment:
- Push to GitHub → Automatic deployment
- No manual steps needed
- Rollback available if issues occur

### 💰 Cost Comparison

| Platform | Free Tier | Limits | Best For |
|----------|-----------|--------|----------|
| Render | 750 hrs/month | 512MB RAM, sleeps after 15min | Full-stack apps |
| Railway | $5 credit/month | ~500 hours | Backend APIs |
| Vercel | Unlimited | 100GB bandwidth | Frontend only |

### 🆘 Troubleshooting

**Issue**: Service won't start
- Check logs in dashboard
- Verify all dependencies in requirements.txt
- Ensure Python version is 3.11+

**Issue**: OAuth not working
- Verify redirect URIs in Google Console
- Check CORS settings in server.py
- Ensure HTTPS is enabled

**Issue**: Slow classification
- First request loads models (slow)
- Subsequent requests use cache (fast)
- Consider using smaller model

**Issue**: Database resets
- Free tier doesn't persist storage
- Use Render persistent disk (paid)
- Or use external database (PostgreSQL)

### 📝 Environment Variables Reference

**Backend**:
```
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
PORT=8000
FRONTEND_URL=https://your-frontend-url.com
```

**Frontend**:
```
VITE_API_URL=https://your-backend-url.com
```

---

## Next Steps

After deployment:

1. ✅ Test authentication flow
2. ✅ Verify email classification works
3. ✅ Check analytics dashboard
4. ✅ Monitor performance and errors
5. ✅ Set up uptime monitoring (optional)

## Support

If you encounter issues:
1. Check platform-specific logs
2. Review this guide
3. Open an issue on GitHub
4. Contact platform support

---

**Congratulations! Your Email Classifier is now live! 🎉**

Share your deployment URL and start classifying emails from anywhere!
