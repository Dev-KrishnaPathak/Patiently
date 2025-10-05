# 🚀 Deploy Backend to Render.com - Step by Step

## ✅ Prerequisites
- GitHub repository with code pushed
- Cerebras API key ready

---

## 📝 Method 1: Using render.yaml (Automatic - RECOMMENDED)

### Step 1: Push render.yaml
The `render.yaml` file is already in your repository. Just ensure it's pushed:

```bash
git status
git push origin main
```

### Step 2: Connect to Render

1. Go to: https://dashboard.render.com/register
2. Sign up with GitHub (recommended) or email
3. Authorize Render to access your GitHub repositories

### Step 3: Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Blueprint"**
3. Connect your repository: **Dev-KrishnaPathak/Patiently**
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

### Step 4: Add Environment Variable

1. After service is created, go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add:
   ```
   Key: CEREBRAS_API_KEY
   Value: your_cerebras_api_key_here
   ```
4. Click **"Save Changes"**

### Step 5: Deploy!

1. Render will automatically start deploying
2. Wait ~5-10 minutes for first deployment
3. Watch the logs for "Application startup complete"
4. Copy your service URL (e.g., `https://patiently-backend.onrender.com`)

---

## 📝 Method 2: Manual Configuration (If render.yaml doesn't work)

### Step 1: Create Account
1. Go to: https://dashboard.render.com/register
2. Sign up with GitHub

### Step 2: New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repository: **Dev-KrishnaPathak/Patiently**
3. Configure:

**Basic Settings:**
```
Name: patiently-backend
Region: Oregon (or closest to you)
Branch: main
Root Directory: backend          ⚠️ CRITICAL - Must be "backend"
Runtime: Python 3
```

**Build & Deploy:**
```
Build Command: pip install --upgrade pip && pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Free
```

### Step 3: Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

```
CEREBRAS_API_KEY = your_api_key_here
PYTHON_VERSION = 3.11.0
```

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (~5-10 minutes)
3. Monitor logs in real-time

---

## ✅ Verify Deployment

### Check Health Endpoint
Once deployed, test:
```
https://your-app-name.onrender.com/
```

Should return:
```json
{
  "status": "healthy",
  "service": "DocuSage API",
  "version": "1.0.0"
}
```

### Check API Docs
Visit:
```
https://your-app-name.onrender.com/docs
```

You should see the FastAPI interactive documentation.

---

## 🔧 Update Frontend with Backend URL

### Step 1: Get Your Backend URL
From Render dashboard, copy your service URL:
```
https://patiently-backend.onrender.com
```

### Step 2: Update Dashboard.jsx

**File**: `frontend/src/pages/Dashboard.jsx`

**Change line 5:**
```javascript
// Old
const API_BASE_URL = 'http://localhost:8000/api'

// New
const API_BASE_URL = 'https://patiently-backend.onrender.com/api'
```

### Step 3: Commit and Push
```bash
cd c:\Users\krish\Desktop\Doc
git add frontend/src/pages/Dashboard.jsx
git commit -m "Update API URL to Render backend"
git push origin main
```

GitHub Actions will automatically redeploy your frontend!

---

## 📊 Understanding Render Free Tier

### ✅ Included:
- 750 hours/month (enough for 1 service)
- Automatic SSL certificates
- Continuous deployment from GitHub
- PostgreSQL database (if needed)
- Auto-sleep after 15 min inactivity

### ⚠️ Limitations:
- **Cold starts**: Service sleeps after 15 min of inactivity
- First request after sleep takes ~30-60 seconds to wake up
- 512 MB RAM
- Shared CPU

### 💡 Cold Start Solution:
Use a free service like UptimeRobot to ping your API every 5 minutes:
```
https://uptimerobot.com
Add Monitor: https://your-app.onrender.com/
```

---

## 🐛 Troubleshooting

### Issue: Build fails with "No requirements.txt"
**Solution**: Make sure `rootDir: backend` is set in render.yaml or dashboard settings

### Issue: Module not found errors
**Solution**: Check that all dependencies are in `requirements.txt`
```bash
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

### Issue: Application startup failed
**Solution**: Check logs in Render dashboard
- Look for import errors
- Verify CEREBRAS_API_KEY is set
- Check Python version compatibility

### Issue: CORS errors in frontend
**Solution**: Already fixed in `main.py` with:
```python
allow_origins=["*"]
```

### Issue: Slow first request
**Solution**: This is normal! Free tier has cold starts.
- First request after sleep: ~30-60 seconds
- Subsequent requests: Fast
- Consider upgrading to paid tier ($7/month) for always-on

---

## 🎯 Testing Your Deployed API

### 1. Health Check
```bash
curl https://patiently-backend.onrender.com/
```

### 2. API Documentation
Open in browser:
```
https://patiently-backend.onrender.com/docs
```

### 3. Upload Test (via frontend)
Once frontend is updated with backend URL:
1. Visit: https://dev-krishnapathak.github.io/Patiently/
2. Go to Dashboard
3. Upload a medical report
4. Should work! 🎉

---

## 📈 Monitoring & Logs

### View Logs:
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

### Metrics:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔄 Auto-Deploy

Every time you push to `main` branch:
1. GitHub notifies Render
2. Render pulls latest code
3. Runs build command
4. Deploys new version
5. Zero downtime deployment

---

## 💰 Upgrade Options (Optional)

### Starter Plan ($7/month):
- ✅ No cold starts (always on)
- ✅ 512 MB RAM
- ✅ Faster CPU

### Standard Plan ($25/month):
- ✅ 2 GB RAM
- ✅ Dedicated CPU
- ✅ Better performance

For hobby/demo projects, **FREE tier is perfect!**

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] `render.yaml` in repository (or manual config done)
- [ ] `CEREBRAS_API_KEY` environment variable set
- [ ] Service deployed successfully
- [ ] Health endpoint tested (`/`)
- [ ] API docs accessible (`/docs`)
- [ ] Frontend updated with backend URL
- [ ] End-to-end test (upload document)
- [ ] UptimeRobot configured (optional)

---

## 🎉 Success!

Your backend is now live at:
```
https://patiently-backend.onrender.com
```

Your full application:
```
Frontend: https://dev-krishnapathak.github.io/Patiently/
Backend:  https://patiently-backend.onrender.com
```

**Congratulations! Your app is fully deployed! 🚀**
