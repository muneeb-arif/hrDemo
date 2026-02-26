# Vercel Deployment Guide

## ⚠️ Important Note

**Streamlit applications require a persistent server process**, which doesn't align well with Vercel's serverless architecture. Vercel is optimized for:
- Static sites
- Serverless functions (short-lived, stateless)
- Next.js/React applications

## Current Setup for Vercel

To work around Vercel's 500MB Lambda limit, the repository has been configured as follows:

1. **Root `requirements.txt` renamed to `requirements-full.txt`** - Contains all dependencies for local development
2. **`api/requirements.txt`** - Empty/minimal file for the serverless function (no dependencies needed)
3. **`api/index.py`** - Minimal serverless function using only Python standard library
4. **`.vercelignore`** - Excludes heavy files and directories

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
   - `OPENAI_API_KEY` - Your OpenAI API key (if needed for the serverless function)

### After Deployment:

The Vercel deployment will show a simple redirect page. **Full Streamlit functionality won't work on Vercel** without significant refactoring.

### For Local Development:

Rename `requirements-full.txt` back to `requirements.txt`:
```bash
mv requirements-full.txt requirements.txt
pip install -r requirements.txt
```

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

**Note:** Rename `requirements-full.txt` back to `requirements.txt` before deploying to Streamlit Cloud.

### 2. **Railway** (Easy & Free tier available)
- Simple deployment
- Good for Python apps
- Free tier with $5 credit/month

**Steps:**
1. Create account at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Rename `requirements-full.txt` to `requirements.txt`
4. Add `Procfile` (already included)
5. Set environment variables

### 3. **Render** (Free tier available)
- Good for Python/Streamlit apps
- Free tier with limitations

**Steps:**
1. Create account at [render.com](https://render.com)
2. New Web Service → Connect GitHub
3. Rename `requirements-full.txt` to `requirements.txt`
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

## Environment Variables

Set these in your deployment platform:

- `OPENAI_API_KEY` - Required for OpenAI API calls

## Files Structure

```
├── main.py                 # Main Streamlit app
├── requirements-full.txt   # Full dependencies (rename to requirements.txt for local/dev)
├── pages/                  # Streamlit pages
│   ├── hr_ai.py
│   └── autosphere_ai.py
├── utils/                  # Utility functions
├── vercel.json            # Vercel configuration
├── .vercelignore          # Files to ignore for Vercel
└── api/                   # Serverless functions (for Vercel)
    ├── index.py
    └── requirements.txt   # Minimal (empty) requirements for Vercel
```

## Recommendation

**For this Streamlit application, I strongly recommend using Streamlit Cloud** as it's:
- Free
- Designed specifically for Streamlit
- Easy to set up
- No code changes required
- Handles all dependencies automatically
