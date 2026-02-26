# Vercel Deployment Guide

## ⚠️ Important Note

**Streamlit applications require a persistent server process**, which doesn't align well with Vercel's serverless architecture. Vercel is optimized for:
- Static sites
- Serverless functions (short-lived, stateless)
- Next.js/React applications

## Recommended Deployment Options for Streamlit

### 1. **Streamlit Cloud** (Recommended - Free)
- **Best option for Streamlit apps**
- Free tier available
- Direct GitHub integration
- Automatic deployments

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file to `main.py`
7. Add environment variables (OPENAI_API_KEY)

### 2. **Railway** (Easy & Free tier available)
- Simple deployment
- Good for Python apps
- Free tier with $5 credit/month

**Steps:**
1. Create account at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Add `railway.json` or use Procfile
4. Set environment variables

### 3. **Render** (Free tier available)
- Good for Python/Streamlit apps
- Free tier with limitations

**Steps:**
1. Create account at [render.com](https://render.com)
2. New Web Service → Connect GitHub
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

## Vercel Deployment (Limited Functionality)

If you still want to deploy on Vercel, note that:

1. **Streamlit won't work natively** - You'll need to convert the app to use Vercel's serverless functions
2. **Major refactoring required** - Convert Streamlit UI to React/Next.js
3. **Limited functionality** - Some Streamlit features may not translate well

### Current Vercel Setup

The repository now includes:
- `vercel.json` - Vercel configuration
- `api/index.py` - Basic serverless function (placeholder)
- `.vercelignore` - Files to exclude from deployment

### To Deploy on Vercel:

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Set environment variables in Vercel dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key

## Environment Variables

Set these in your deployment platform:

- `OPENAI_API_KEY` - Required for OpenAI API calls

## Files Structure

```
├── main.py                 # Main Streamlit app
├── pages/                  # Streamlit pages
│   ├── hr_ai.py
│   └── autosphere_ai.py
├── utils/                  # Utility functions
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel configuration
├── .vercelignore          # Files to ignore
└── api/                   # Serverless functions (for Vercel)
    └── index.py
```

## Recommendation

**For this Streamlit application, I strongly recommend using Streamlit Cloud** as it's:
- Free
- Designed specifically for Streamlit
- Easy to set up
- No code changes required

Would you like me to help you set up deployment on Streamlit Cloud instead?
