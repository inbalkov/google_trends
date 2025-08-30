# Keyword Trend Explorer

A Streamlit app that analyzes Google Trends data and uses AI to explain anomalies in search interest.

## Features

- Fetch Google Trends data for any keyword
- Detect anomalies (weeks with ≥30% week-over-week change)
- AI-powered explanations for trend anomalies using Hugging Face models
- Interactive visualizations with Altair

## Setup

### 1. Install Dependencies

```bash
pip install streamlit pandas pytrends transformers torch python-dotenv altair
```

### 2. Configure API Key

The app uses Hugging Face models for generating explanations. To set up your API key:

1. Get a Hugging Face API token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

2. Copy the template file:
   ```bash
   cp env_template.txt .env
   ```

3. Edit `.env` and replace `your_huggingface_token_here` with your actual token:
   ```
   HUGGINGFACE_API_TOKEN=hf_your_actual_token_here
   ```

### 3. Run the App

```bash
streamlit run app.py
```

## Security

- The `.env` file is automatically ignored by git (see `.gitignore`)
- API keys are never hardcoded in the source code
- The app will show a warning if no API key is found

## Usage

1. Enter a keyword or phrase in the search box
2. View the trend chart with anomalies highlighted
3. Click on anomaly expanders to see AI-generated explanations

## Troubleshooting

- **Rate limiting**: If you get rate limit errors, wait 2-3 minutes between searches
- **No API key**: The app will work without an API key but won't generate explanations
- **Model loading**: The app uses a small model (distilgpt2) by default for faster loading
