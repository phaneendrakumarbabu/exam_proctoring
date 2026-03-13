# Render Deployment - Quick Start (5 Minutes)

## TL;DR

1. **Push to GitHub** (already done)
   ```bash
   git push origin main
   ```

2. **Go to Render**: https://render.com

3. **Click "New +" → "Web Service"**

4. **Connect your GitHub repo**: `exam_proctoring`

5. **Fill in these fields**:
   - Name: `examguard`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app`

6. **Add Environment Variable**:
   - Key: `PYTHONUNBUFFERED`
   - Value: `1`

7. **Click "Create Web Service"** and wait 2-5 minutes

8. **Done!** Your app is live at the URL shown in Render dashboard

## Test It

```bash
curl https://your-app-name.onrender.com/api/ping
```

## Access Your App

- **Login**: https://your-app-name.onrender.com/
- **Exam**: https://your-app-name.onrender.com/exam
- **Dashboard**: https://your-app-name.onrender.com/dashboard

## Demo Credentials

```
Student ID: STU001
Password: pass123

Admin ID: ADMIN
Password: admin123
```

## Important

⚠️ **Free tier limitations**:
- Service sleeps after 15 min of inactivity
- Database resets on restart (use PostgreSQL for persistence)
- Limited to 0.5 GB RAM

For production, upgrade to a paid plan.

---

**Need help?** See `RENDER_DEPLOYMENT.md` for detailed guide.
