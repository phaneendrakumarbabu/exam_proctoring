# ExamGuard Deployment Guide - Render

This guide walks you through deploying the ExamGuard Flask application to Render.

## Prerequisites

- GitHub account with the exam_proctoring repository pushed
- Render account (free tier available at https://render.com)
- Git installed locally

## Step 1: Prepare Your Repository

The repository is already configured with:
- `Procfile` - Specifies the start command for Render
- `render.yaml` - Optional configuration file (alternative to Procfile)
- `requirements.txt` - Python dependencies

Ensure all files are committed and pushed to GitHub:

```bash
cd exam_proctoring
git add -A
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Create a Render Account

1. Go to https://render.com
2. Sign up with your GitHub account (recommended for easier integration)
3. Authorize Render to access your GitHub repositories

## Step 3: Create a New Web Service

1. Log in to your Render dashboard
2. Click **"New +"** button in the top right
3. Select **"Web Service"**
4. Choose **"Build and deploy from a Git repository"**

## Step 4: Connect Your Repository

1. Search for and select the `exam_proctoring` repository
2. Click **"Connect"**
3. Fill in the service details:

   | Field | Value |
   |-------|-------|
   | **Name** | examguard |
   | **Environment** | Python 3 |
   | **Region** | Choose closest to your users |
   | **Branch** | main |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app` |

## Step 5: Configure Environment Variables

In the Render dashboard, add these environment variables:

```
PYTHONUNBUFFERED=1
FLASK_ENV=production
```

Optional (for production):
```
SECRET_KEY=your-secure-random-key-here
```

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Build the application
   - Start the service with the Procfile command

3. Wait for the deployment to complete (usually 2-5 minutes)
4. Once deployed, you'll see a URL like: `https://examguard.onrender.com`

## Step 7: Verify Deployment

Test your deployment:

```bash
# Test the API
curl https://examguard.onrender.com/api/ping

# Expected response:
# {"status":"ok","time":"2024-...","message":"Server is reachable"}
```

Or visit in your browser:
- Login page: `https://examguard.onrender.com/`
- Dashboard: `https://examguard.onrender.com/dashboard`
- Exam page: `https://examguard.onrender.com/exam`

## Step 8: Update Frontend API Endpoints (if needed)

If your frontend is making API calls to `localhost:8000`, update them to use the Render URL:

In `static/js/examguard.js` or `static/js/proctor.js`, replace:
```javascript
// Old
const API_BASE = 'http://localhost:8000';

// New
const API_BASE = 'https://examguard.onrender.com';
```

Or use relative URLs (recommended):
```javascript
const API_BASE = '';  // Uses current domain
```

## Important Notes

### Database Persistence
- The SQLite database (`database/exam_logs.db`) is stored in the container's ephemeral filesystem
- **Data will be lost when the service restarts**
- For production, consider:
  - Using PostgreSQL (Render offers free tier)
  - Implementing cloud storage for logs
  - Regular backups

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- Limited to 0.5 GB RAM
- No custom domains (unless you upgrade)
- For production use, upgrade to a paid plan

### Performance Optimization
- The `gunicorn` command uses 4 workers: `-w 4`
- Adjust based on your needs: `-w 2` for free tier, `-w 8` for paid
- Monitor CPU/RAM usage in Render dashboard

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### Service Won't Start
- Check runtime logs in Render dashboard
- Ensure `backend/app.py` exists and is properly configured
- Verify the start command matches your project structure

### Database Errors
- Check if `database/` directory exists
- Ensure write permissions in the container
- Consider using PostgreSQL for persistence

### Static Files Not Loading
- Verify `static/` folder exists in repository
- Check Flask configuration in `backend/app.py`
- Ensure static routes are properly configured

## Monitoring and Logs

1. Go to your service in Render dashboard
2. Click **"Logs"** tab to view:
   - Build logs
   - Runtime logs
   - Error messages

3. Set up alerts for service failures (paid plans)

## Updating Your Deployment

To deploy new changes:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add -A
   git commit -m "Your message"
   git push origin main
   ```

3. Render automatically redeploys on push (if auto-deploy is enabled)
4. Or manually trigger a redeploy from the Render dashboard

## Next Steps

- Set up a custom domain (paid plans)
- Configure SSL/TLS (automatic on Render)
- Set up monitoring and alerts
- Consider upgrading to paid tier for production use
- Implement proper database solution (PostgreSQL)

## Support

- Render Documentation: https://render.com/docs
- Flask Documentation: https://flask.palletsprojects.com
- Gunicorn Documentation: https://gunicorn.org

---

**Your Render URL will be:** `https://examguard.onrender.com` (or similar)

Once deployed, share this URL with students to access the exam system!
