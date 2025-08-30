# Installation Guide - Keyword Trend Explorer (OpenAI Version)

## Quick Setup

### 1. Clone/Download the Project
```bash
# Download the files to your local machine
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Minimal Installation (Recommended)**
```bash
pip install -r requirements_minimal.txt
```

**Option B: Full Installation (Exact development environment)**
```bash
pip install -r requirements_full.txt
```

**Option C: Manual Installation**
```bash
pip install streamlit pandas pytrends openai altair python-dotenv
```

### 4. Set Up OpenAI API Key

**Option A: Environment Variable**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

**Option B: .env File (Recommended)**
Create a `.env` file in the project directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Option C: Enter in App**
Run the app and enter your API key in the sidebar.

### 5. Get Your OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### 6. Run the Application
```bash
streamlit run app_openai.py
```

The app will open in your browser at `http://localhost:8501`

## Requirements Files Explained

- **`requirements_minimal.txt`** - Essential packages only (recommended for production)
- **`requirements_full.txt`** - Exact development environment (includes all packages)
- **`requirements.txt`** - Complete pip freeze output (includes everything)

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 1GB+ RAM recommended
- **Internet**: Required for Google Trends API and OpenAI API

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements_minimal.txt
   ```

2. **"OpenAI client unavailable"**
   - Check your API key is set correctly
   - Ensure you have credits in your OpenAI account

3. **"Rate limit exceeded" (Google Trends)**
   - Wait 2-3 minutes between searches
   - This is a Google limitation, not an app issue

4. **Import errors with virtual environment**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

### Verification Commands

Check if packages are installed correctly:
```bash
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import pytrends; print('PyTrends: OK')"
```

## Development Environment

This app was developed with:
- Python 3.12
- Streamlit 1.48.1
- OpenAI 1.102.0
- pandas 2.2.2
- pytrends 4.9.2

## Support

If you encounter issues:
1. Check this installation guide
2. Verify all dependencies are installed
3. Ensure your OpenAI API key is valid and has credits
4. Check the README_openai.md for usage instructions
