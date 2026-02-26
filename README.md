# Enterprise AI Dashboard - HR & AutoSphere Motors

A Streamlit-based enterprise AI dashboard with two main applications:
1. **HR AI Platform** - CV evaluation, policy management, and technical assessments
2. **AutoSphere Motors AI** - AI assistant for automotive services and bookings

## Features

### HR AI Platform
- **CV Evaluation**: Upload candidate CVs and match them against job descriptions
- **Policy Management**: Upload and manage HR policy documents
- **Technical Evaluation**: Generate and evaluate technical interview questions
- **Employee Portal**: Ask questions about HR policies

### AutoSphere Motors AI
- **AI Assistant**: Chat-based assistant for automotive queries
- **Service Booking**: Book vehicle services through chat or form
- **Test Drive Booking**: Schedule test drives
- **Booking Search**: Search existing bookings by ID, phone, or type

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd hr_demo_muneeb
```

2. Install dependencies:
```bash
# For local development, rename requirements-full.txt to requirements.txt first
mv requirements-full.txt requirements.txt
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
streamlit run main.py
```

The app will be available at `http://localhost:8501`

## Deployment

### ⚠️ Important: Streamlit and Vercel Compatibility

**Streamlit applications require a persistent server process**, which doesn't align well with Vercel's serverless architecture. Vercel is optimized for static sites and serverless functions, not long-running Python applications.

### Recommended: Streamlit Cloud (Free & Easy)

**Best option for this Streamlit app:**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file to `main.py`
7. Add environment variables:
   - `OPENAI_API_KEY` - Your OpenAI API key

### Alternative Platforms

- **Railway**: [railway.app](https://railway.app) - Good for Python apps, free tier available
- **Render**: [render.com](https://render.com) - Free tier with limitations
- **Heroku**: Requires credit card but has free tier options

### Vercel Deployment (Limited)

This repository includes Vercel configuration files, but **full Streamlit functionality won't work on Vercel** without significant refactoring. The current setup provides a basic serverless function that can redirect or display information.

To deploy on Vercel:

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables in Vercel dashboard:
   - `OPENAI_API_KEY`

**Note**: For full functionality, consider converting the app to Next.js/React or using Streamlit Cloud.

## Project Structure

```
├── main.py                 # Main Streamlit application entry point
├── pages/                  # Streamlit pages
│   ├── hr_ai.py           # HR AI Platform implementation
│   └── autosphere_ai.py   # AutoSphere Motors AI implementation
├── utils/                  # Utility modules
│   └── openai_client.py   # OpenAI client configuration
├── requirements-full.txt   # Full Python dependencies (rename to requirements.txt for local dev)
├── vercel.json            # Vercel configuration (for serverless deployment)
├── api/                   # Serverless functions (for Vercel)
│   └── index.py
├── users.xlsx             # User authentication data
├── bookings.xlsx          # AutoSphere bookings data
├── autosphere_policy.docx # AutoSphere policy document
└── vectorstore/           # FAISS vector store for embeddings
```

## Environment Variables

- `OPENAI_API_KEY` (Required): Your OpenAI API key for GPT models

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- streamlit
- openai
- langchain
- faiss-cpu
- pandas
- openpyxl
- PyPDF2
- python-docx

## Usage

1. Start the app: `streamlit run main.py`
2. Login with credentials from `users.xlsx`
3. Select between "HR AI Platform" or "AutoSphere Motors AI"
4. Use the respective features based on your role/needs

## License

This project is for demonstration purposes.
