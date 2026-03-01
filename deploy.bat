@echo off
REM Email Classifier Deployment Script for Windows

echo.
echo 🚀 Email Classifier Deployment Helper
echo ======================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not initialized
    echo Run: git init ^&^& git add . ^&^& git commit -m "Initial commit"
    exit /b 1
)

echo Choose deployment platform:
echo 1^) Render ^(Recommended - Free^)
echo 2^) Railway ^(Free $5 credit^)
echo 3^) Vercel + Render ^(Best performance^)
echo 4^) Manual setup
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 📦 Deploying to Render...
    echo.
    echo Steps:
    echo 1. Go to https://dashboard.render.com/
    echo 2. Click 'New +' -^> 'Web Service'
    echo 3. Connect your GitHub repository
    echo 4. Use these settings:
    echo    - Build Command: pip install -r requirements.txt
    echo    - Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
    echo    - Environment: PYTHON_VERSION=3.11.9, ENVIRONMENT=production
    echo.
    echo 5. For frontend, create a 'Static Site' with:
    echo    - Build Command: cd frontend ^&^& npm install ^&^& npm run build
    echo    - Publish Directory: frontend/dist
    echo    - Environment: VITE_API_URL=^<your-backend-url^>
    echo.
    echo 📖 Full guide: See DEPLOYMENT.md
) else if "%choice%"=="2" (
    echo.
    echo 🚂 Deploying to Railway...
    echo.
    echo Steps:
    echo 1. Go to https://railway.app/
    echo 2. Click 'Start a New Project'
    echo 3. Select 'Deploy from GitHub repo'
    echo 4. Railway will auto-detect and deploy
    echo.
    echo 📖 Full guide: See DEPLOYMENT.md
) else if "%choice%"=="3" (
    echo.
    echo ⚡ Deploying to Vercel + Render...
    echo.
    echo Backend ^(Render^):
    echo 1. Follow Render steps above for backend
    echo.
    echo Frontend ^(Vercel^):
    echo 1. Go to https://vercel.com/
    echo 2. Click 'Add New' -^> 'Project'
    echo 3. Import your GitHub repository
    echo 4. Set Root Directory: frontend
    echo 5. Add Environment: VITE_API_URL=^<your-backend-url^>
    echo.
    echo 📖 Full guide: See DEPLOYMENT.md
) else if "%choice%"=="4" (
    echo.
    echo 📝 Manual Setup
    echo.
    echo Required files created:
    echo ✅ render.yaml - Render configuration
    echo ✅ railway.json - Railway configuration
    echo ✅ vercel.json - Vercel configuration
    echo ✅ Procfile - General deployment config
    echo ✅ DEPLOYMENT.md - Full deployment guide
    echo.
    echo Read DEPLOYMENT.md for detailed instructions
) else (
    echo ❌ Invalid choice
    exit /b 1
)

echo.
echo ⚠️  Important: Update Google OAuth redirect URIs
echo 1. Go to https://console.cloud.google.com/
echo 2. APIs ^& Services -^> Credentials
echo 3. Add your deployment URL to Authorized redirect URIs
echo.
echo ✅ Deployment configuration complete!
echo 📖 See DEPLOYMENT.md for full instructions
echo.
pause
