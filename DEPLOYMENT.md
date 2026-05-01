# Deployment Guide

This guide will help you deploy the Real-Time Incident Response System to Render.

## Prerequisites

1. A [Render](https://render.com) account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### Option 1: Deploy using Render Dashboard (Recommended)

1. **Sign in to Render**
   - Go to https://render.com and sign in with your GitHub/GitLab account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your repository
   - Select the repository containing this project

3. **Configure the Service**
   - **Name**: `incident-response-system` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/static/
     ```
   - **Start Command**: 
     ```bash
     cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 app:app
     ```

4. **Create a PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name it `incident-db`
   - Note the connection string

5. **Set Environment Variables**
   In your web service settings, add these environment variables:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a random secret key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_URL`: Use the connection string from your PostgreSQL database
   - `ADMIN_USERNAME`: `admin` (or your preferred admin username)
   - `ADMIN_PASSWORD`: Set a strong password for admin access
   - `SOCKETIO_ASYNC_MODE`: `eventlet`

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for the deployment to complete (usually 5-10 minutes)

### Option 2: Deploy using render.yaml (Blueprints)

1. **Push your code to Git**
   - Make sure `render.yaml` is in your repository root

2. **Create a Blueprint in Render**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**
   - Set `ADMIN_PASSWORD` in the Render dashboard (it's marked as `sync: false` in the yaml)
   - All other variables will be set automatically

4. **Deploy**
   - Click "Apply" to deploy all services

## Post-Deployment

1. **Access Your Application**
   - Your app will be available at `https://your-service-name.onrender.com`
   - The admin login is at `/admin/login`

2. **Update Frontend API URL (if needed)**
   - If you're deploying frontend and backend separately, update `VITE_API_BASE_URL` in your frontend build
   - For single deployment (backend serving frontend), no changes needed

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment | Yes | `production` |
| `SECRET_KEY` | Secret key for sessions | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `ADMIN_USERNAME` | Admin login username | No | `admin` |
| `ADMIN_PASSWORD` | Admin login password | Yes | - |
| `SOCKETIO_ASYNC_MODE` | SocketIO async mode | No | `eventlet` |
| `PORT` | Server port (set by Render) | Auto | - |

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt` and `package.json`
- Verify Node.js and Python versions are compatible
- Check build logs in Render dashboard

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL database is created and running
- Check database connection string format

### SocketIO Not Working
- Verify `eventlet` is installed
- Check `SOCKETIO_ASYNC_MODE` is set to `eventlet`
- Ensure WebSocket support is enabled (Render supports this by default)

### Frontend Not Loading
- Verify frontend build completed successfully
- Check that files are copied to `backend/static/`
- Ensure static file serving routes are correct

## Local Testing Before Deployment

1. **Build locally**:
   ```bash
   # On Windows
   build.bat
   
   # On Linux/Mac
   chmod +x build.sh
   ./build.sh
   ```

2. **Test the production build**:
   ```bash
   cd backend
   python app.py
   ```

3. **Verify**:
   - Frontend loads at http://localhost:5000
   - API endpoints work
   - WebSocket connections work

## Alternative Deployment Options

### Vercel (Frontend) + Render (Backend)

1. **Deploy Backend to Render** (as above)
2. **Deploy Frontend to Vercel**:
   - Set `VITE_API_BASE_URL` to your Render backend URL
   - Deploy using Vercel CLI or dashboard

### Railway

Railway is another good option that supports both frontend and backend:
- Similar setup to Render
- Can use `Procfile` or `railway.json`

## Notes

- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading for production use
- Database persists data even when web service spins down

