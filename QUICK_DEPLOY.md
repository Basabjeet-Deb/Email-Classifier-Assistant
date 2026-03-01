# Quick Deploy Guide - Get Your App Online in 10 Minutes! 🚀

## Fastest Way: Render (100% Free)

### 1. Push to GitHub (2 minutes)

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy Backend (3 minutes)

1. Go to [Render](https://dashboard.render.com/) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Fill in:
   - **Name**: `email-classifier-api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - **PYTHON_VERSION**: `3.11.9` (Important!)
   - **ENVIRONMENT**: `production`
6. Click **"Create Web Service"**
7. **Copy your URL**: `https://email-classifier-api.onrender.com`

**Note:** First deployment takes 5-10 minutes. This is normal!

### 3. Deploy Frontend (3 minutes)

1. Click **"New +"** → **"Static Site"**
2. Connect same GitHub repo
3. Fill in:
   - **Name**: `email-classifier-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://email-classifier-api.onrender.com` (your backend URL)
5. Click **"Create Static Site"**

### 4. Update Google OAuth (2 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 Client ID
4. Add to **Authorized redirect URIs**:
   ```
   https://email-classifier-api.onrender.com
   https://email-classifier-frontend.onrender.com
   ```
5. Click **Save**

### 5. Done! 🎉

Visit your app: `https://email-classifier-frontend.onrender.com`

---

## Important Notes

### ⚠️ First Load is Slow
- Free tier services "sleep" after 15 minutes
- First request takes 30-60 seconds to wake up
- After that, it's fast!

### 💡 Keep It Awake (Optional)
Use [UptimeRobot](https://uptimerobot.com/) to ping your app every 14 minutes:
1. Sign up for free
2. Add monitor: `https://email-classifier-api.onrender.com/api/status`
3. Set interval: 14 minutes

### 🔒 Security
- Never commit `credentials.json` to GitHub
- Upload it manually in Render dashboard if needed
- Or use environment variables

### 📊 Free Tier Limits
- **750 hours/month** (enough for 1 service 24/7)
- **512MB RAM** (enough for our app)
- **100GB bandwidth** (plenty for personal use)

---

## Alternative: Railway (Also Free)

Railway gives you $5 free credit per month (~500 hours).

### Quick Deploy:
1. Go to [Railway](https://railway.app/)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Railway auto-detects everything!
5. Add environment variable: `ENVIRONMENT=production`
6. Get your URL and update Google OAuth

---

## Troubleshooting

**Build fails with PyTorch error?**
- Make sure you set `PYTHON_VERSION=3.11.9` in environment variables
- The app requires Python 3.11, not 3.14+
- Redeploy after setting the correct version

**App won't start?**
- Check logs in Render dashboard
- Verify Python version is 3.11+
- Ensure all files are committed to GitHub

**OAuth not working?**
- Double-check redirect URIs in Google Console
- Make sure you're using HTTPS URLs
- Wait 5 minutes for Google to update

**Classification is slow?**
- First classification loads ML models (slow)
- Subsequent classifications use cache (fast)
- This is normal on free tier

---

## Need Help?

1. Check full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review logs in platform dashboard
3. Open an issue on GitHub

---

**Your app is now live and accessible from anywhere! Share the URL and start classifying emails! 🎉**
