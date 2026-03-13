# ExamGuard Deployment Options

## Deployment Platforms Configured

### 1. **Render** (Recommended for Beginners) ✅
- **Status**: Fully configured
- **Setup Time**: 5 minutes
- **Cost**: Free tier available
- **Best For**: Quick deployment, learning, small projects
- **Files**: `Procfile`, `render.yaml`
- **Guide**: See `RENDER_QUICK_START.md` or `RENDER_DEPLOYMENT.md`

**Quick Deploy**:
1. Go to https://render.com
2. Connect GitHub repo
3. Use settings from `RENDER_QUICK_START.md`
4. Done!

---

### 2. **Vercel** (Serverless)
- **Status**: Configured
- **Setup Time**: 5 minutes
- **Cost**: Free tier available
- **Best For**: Serverless, auto-scaling
- **Files**: `vercel.json`, `api/index.py`
- **Note**: May have cold start delays on free tier

**Deploy**:
1. Go to https://vercel.com
2. Import GitHub repo
3. Vercel auto-detects Flask and deploys

---

### 3. **Local Development**
- **Status**: Ready
- **Setup Time**: 2 minutes
- **Cost**: Free
- **Best For**: Testing, development

**Run Locally**:
```bash
cd exam_proctoring
python backend/app.py
```
Then visit: http://localhost:8000

---

## Comparison Table

| Feature | Render | Vercel | Local |
|---------|--------|--------|-------|
| **Setup Time** | 5 min | 5 min | 2 min |
| **Cost** | Free | Free | Free |
| **Uptime** | 99.9% | 99.9% | Manual |
| **Database** | Ephemeral | Ephemeral | Local |
| **Custom Domain** | Paid | Free | N/A |
| **Cold Starts** | ~1s | ~5s | Instant |
| **Best For** | Production | Serverless | Development |

---

## Recommended Deployment Path

### For Development
```
Local (http://localhost:8000)
    ↓
Test features locally
    ↓
Push to GitHub
```

### For Production
```
Render (https://examguard.onrender.com)
    ↓
Monitor performance
    ↓
Upgrade to paid tier if needed
    ↓
Add PostgreSQL for persistence
```

---

## Environment Variables

### Render
Set in Render dashboard:
```
PYTHONUNBUFFERED=1
FLASK_ENV=production
```

### Vercel
Set in `vercel.json` or dashboard:
```
PYTHONUNBUFFERED=1
```

### Local
Set in terminal:
```bash
# Windows PowerShell
$env:FLASK_ENV = "development"

# Linux/Mac
export FLASK_ENV=development
```

---

## Database Considerations

### Current Setup (SQLite)
- ✅ Works out of the box
- ❌ Data lost on restart
- ❌ Not suitable for production

### For Production
- Use **PostgreSQL** (Render offers free tier)
- Or **MongoDB** (Atlas free tier)
- Or **Firebase** (Google Cloud)

---

## Monitoring & Logs

### Render
- Dashboard: https://dashboard.render.com
- Logs: Service → Logs tab
- Metrics: Service → Metrics tab

### Vercel
- Dashboard: https://vercel.com/dashboard
- Logs: Deployments → Logs
- Analytics: Analytics tab

### Local
- Console output in terminal
- Check `database/exam_logs.db` for logs

---

## Troubleshooting

### App Won't Start
1. Check logs in platform dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure `backend/app.py` exists
4. Check Python version (3.9+)

### Static Files Not Loading
1. Verify `static/` folder exists
2. Check Flask static folder configuration
3. Ensure files are committed to Git

### Database Errors
1. Check `database/` directory exists
2. Verify write permissions
3. Consider using PostgreSQL

### API Endpoints Not Working
1. Check backend routes in `backend/app.py`
2. Verify CORS is enabled
3. Check environment variables

---

## Next Steps

1. **Choose a platform** (Render recommended)
2. **Follow the quick start guide** for your platform
3. **Test the deployment** with demo credentials
4. **Monitor logs** for any issues
5. **Upgrade to paid tier** if needed for production

---

## Demo Credentials

```
Student Login:
  ID: STU001
  Password: pass123

Admin Login:
  ID: ADMIN
  Password: admin123
```

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **Gunicorn Docs**: https://gunicorn.org

---

**Ready to deploy? Start with Render!** 🚀
