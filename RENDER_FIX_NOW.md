# 🚨 URGENT FIX - Render Dashboard Settings

## The Problem
Render is running `pip install -r requirements.txt` from the **root directory**, but the file is in the **backend/** directory.

**Error:**
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

---

## ✅ SOLUTION: Update Settings in Render Dashboard

### Go to Your Service Settings

1. Open: https://dashboard.render.com
2. Click on your service: **patiently-backend**
3. Click **"Settings"** tab (left sidebar)
4. Scroll to **"Build & Deploy"** section

---

### Change These 3 Settings:

#### 1. Root Directory
```
OLD: (blank or empty)
NEW: backend
```
⚠️ **CRITICAL:** Type exactly `backend` (lowercase, no slashes)

#### 2. Build Command
```
OLD: pip install -r requirements.txt
NEW: pip install --upgrade pip && pip install -r requirements.txt
```

#### 3. Start Command  
```
OLD: uvicorn main:app --host 0.0.0.0 --port $PORT
NEW: uvicorn main:app --host 0.0.0.0 --port $PORT
```
(This should already be correct)

---

### Save & Redeploy

1. Scroll to bottom
2. Click **"Save Changes"**
3. Render will automatically trigger a new deployment
4. Watch the logs for success!

---

## 🎯 What This Does

**Root Directory: backend** tells Render:
- ✅ Look in `/backend/` folder for all files
- ✅ Run all commands relative to `/backend/`
- ✅ `requirements.txt` will be found at `/backend/requirements.txt`

---

## 📸 Visual Guide

**Root Directory field should look like:**
```
┌─────────────────────────────────┐
│ Root Directory                  │
│ ┌─────────────────────────────┐ │
│ │ backend                     │ │ ← Type this!
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

## ✅ Expected Result

After saving, Render will rebuild and you should see:

```
==> Cloning from https://github.com/Dev-KrishnaPathak/Patiently
==> Checking out commit...
==> Using Python version 3.13.4
==> Running build command 'pip install --upgrade pip && pip install -r requirements.txt'...
Collecting fastapi==0.101.1
  Downloading fastapi-0.101.1-py3-none-any.whl
Collecting uvicorn[standard]==0.23.0
  Downloading uvicorn-0.23.0-py3-none-any.whl
...
Successfully installed fastapi-0.101.1 uvicorn-0.23.0 ...
==> Build succeeded! 🎉
==> Deploying...
```

---

## 🔄 Alternative: Delete & Recreate (If Settings Don't Stick)

If changing the Root Directory doesn't work:

1. **Delete the current service**:
   - Go to Settings → Danger Zone
   - Click "Delete Web Service"

2. **Create new service with correct settings from start**:
   - Click "New +" → "Web Service"
   - Connect repository: **Dev-KrishnaPathak/Patiently**
   - ⚠️ **SET ROOT DIRECTORY TO: `backend`** ⚠️
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `CEREBRAS_API_KEY`

---

## 📋 Checklist

- [ ] Go to Render Dashboard → Settings
- [ ] Set **Root Directory** = `backend`
- [ ] Verify **Build Command** includes `pip install`
- [ ] Click **"Save Changes"**
- [ ] Wait for automatic redeploy
- [ ] Check logs for "Build succeeded"
- [ ] Test: `https://your-app.onrender.com/`

---

## 🆘 If Still Failing

Screenshot the following and share:
1. Render Settings → Build & Deploy section
2. The full build log error
3. Your service URL

The issue is 100% the **Root Directory** setting!

---

**Fix this ONE setting and it will work! 🚀**
