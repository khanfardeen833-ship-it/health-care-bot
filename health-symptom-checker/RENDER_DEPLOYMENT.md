# Deploy to Render (Free Alternative to Railway)

## Backend Deployment on Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Click "New +" → "Web Service"

### Step 2: Connect Repository
1. Select your GitHub repository
2. Choose "Build and deploy from a Git repository"

### Step 3: Configure Service
- **Name**: `health-symptom-checker-backend`
- **Root Directory**: `health-symptom-checker/backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Environment Variables
Add these in the Render dashboard:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: `gpt-4o`

### Step 5: Deploy
Click "Create Web Service" and wait for deployment.

## Frontend Deployment on Vercel

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account
3. Click "New Project"

### Step 2: Import Repository
1. Select your GitHub repository
2. Set Root Directory to `health-symptom-checker/frontend`

### Step 3: Environment Variables
Add this environment variable:
- `REACT_APP_API_URL`: Your Render backend URL (e.g., `https://health-symptom-checker-backend.onrender.com`)

### Step 4: Deploy
Click "Deploy" and wait for completion.

## Free Tier Limits

### Render (Backend)
- 750 hours/month free
- Automatic sleep after 15 minutes of inactivity
- Wakes up automatically on request

### Vercel (Frontend)
- Unlimited static deployments
- 100GB bandwidth/month
- Automatic HTTPS

## Cost: $0/month (completely free!)

## Result
You'll get URLs like:
- Frontend: `https://your-app-name.vercel.app`
- Backend: `https://health-symptom-checker-backend.onrender.com`

Your health chatbot will be live and accessible worldwide!
