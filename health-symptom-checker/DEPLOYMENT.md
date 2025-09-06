# Health Symptom Checker - Deployment Guide

This guide will help you deploy your Health Symptom Checker application for free using Railway (backend) and Vercel (frontend).

## Prerequisites

1. **GitHub Account** - You'll need to push your code to GitHub
2. **Railway Account** - For backend hosting (free tier available)
3. **Vercel Account** - For frontend hosting (free tier available)
4. **OpenAI API Key** - For the AI functionality

## Step 1: Prepare Your Code

### 1.1 Push to GitHub
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit - Health Symptom Checker"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/health-symptom-checker.git
git push -u origin main
```

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"

### 2.2 Deploy Backend
1. Select your repository
2. Choose the `backend` folder as the root directory
3. Railway will automatically detect it's a Python app
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_MODEL`: `gpt-4o`
   - `API_HOST`: `0.0.0.0`
   - `PORT`: Railway will set this automatically

### 2.3 Get Backend URL
After deployment, Railway will provide a URL like: `https://your-app-name.railway.app`

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account
3. Click "New Project" → "Import Git Repository"

### 3.2 Deploy Frontend
1. Select your repository
2. Set the root directory to `frontend`
3. Add environment variable:
   - `REACT_APP_API_URL`: Your Railway backend URL (e.g., `https://your-app-name.railway.app`)

### 3.3 Get Frontend URL
After deployment, Vercel will provide a URL like: `https://your-app-name.vercel.app`

## Step 4: Update CORS Settings

After getting your Vercel URL, update the backend CORS settings:

1. Go to your Railway dashboard
2. Add environment variable:
   - `FRONTEND_URL`: Your Vercel frontend URL

## Step 5: Test Your Deployment

1. Visit your Vercel frontend URL
2. Test the symptom checker functionality
3. Verify that the frontend can communicate with the backend

## Free Tier Limits

### Railway (Backend)
- 500 hours of usage per month
- $5 credit monthly
- Automatic sleep after inactivity

### Vercel (Frontend)
- Unlimited static deployments
- 100GB bandwidth per month
- Automatic HTTPS

## Troubleshooting

### Backend Issues
- Check Railway logs for errors
- Verify environment variables are set correctly
- Ensure OpenAI API key is valid

### Frontend Issues
- Check Vercel deployment logs
- Verify `REACT_APP_API_URL` environment variable
- Test API connectivity

### CORS Issues
- Update `ALLOWED_ORIGINS` in `config.py` with your Vercel URL
- Redeploy backend after changes

## Security Notes

- Never commit your OpenAI API key to GitHub
- Use environment variables for all sensitive data
- The current setup uses the API key from config.py as fallback - consider removing it for production

## Cost

This deployment is completely free within the limits of:
- Railway free tier (500 hours/month)
- Vercel free tier (unlimited static sites)
- OpenAI API usage (pay-per-use)

## Support

If you encounter issues:
1. Check the deployment logs
2. Verify all environment variables
3. Test locally first
4. Check GitHub issues for common problems
