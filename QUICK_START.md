# Quick Start - Deploy to Render

## Fastest Way to Deploy (5 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select this repository

3. **Configure Service**
   - **Name**: `incident-response-system`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (root of repo)
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/static/
     ```
   - **Start Command**: 
     ```bash
     cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 app:app
     ```

4. **Create Database**
   - Click "New +" → "PostgreSQL"
   - Name: `incident-db`
   - Plan: Free
   - Click "Create Database"
   - Copy the **Internal Database URL** (you'll need it)

5. **Set Environment Variables**
   In your web service, go to "Environment" tab and add:
   
   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | Generate one: `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DATABASE_URL` | Paste the Internal Database URL from step 4 |
   | `ADMIN_USERNAME` | `admin` |
   | `ADMIN_PASSWORD` | Choose a strong password |
   | `SOCKETIO_ASYNC_MODE` | `eventlet` |

6. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build to complete
   - Your app will be live at `https://your-service-name.onrender.com`

### Step 3: Access Your App

- **Public Site**: `https://your-service-name.onrender.com`
- **Admin Login**: `https://your-service-name.onrender.com/admin/login`
  - Username: `admin`
  - Password: (the one you set)

## That's It! 🎉

Your app is now live. The first deployment takes a few minutes, but subsequent updates are faster.

## Troubleshooting

**Build fails?**
- Check the build logs in Render dashboard
- Make sure all files are committed to Git
- Verify Node.js and Python versions

**Database connection error?**
- Make sure you used the **Internal Database URL** (not External)
- Verify DATABASE_URL environment variable is set correctly

**App not loading?**
- Check the service logs in Render dashboard
- Make sure the service is "Live" (not "Sleeping")
- Free tier services sleep after 15 min of inactivity (first request will be slow)

## Next Steps

- Customize admin credentials
- Set up a custom domain (Render supports this)
- Monitor logs and metrics in Render dashboard
- Consider upgrading from free tier for production use

