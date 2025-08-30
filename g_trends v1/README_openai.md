# Keyword Trend Explorer - OpenAI Version

A Streamlit web application that analyzes Google Trends data and uses OpenAI's GPT-4o-mini to provide intelligent explanations for search interest anomalies.

## Features

- **Google Trends Analysis**: Fetches weekly search interest data for keywords in the US during 2023
- **Anomaly Detection**: Automatically identifies significant week-over-week changes (±30% threshold)
- **Interactive Visualization**: Charts with highlighted anomalies using Altair
- **AI-Powered Explanations**: Uses OpenAI's GPT-4o-mini model to generate contextual explanations for trend spikes and drops
- **Rate Limit Handling**: Built-in protection against Google Trends API rate limits

## What's New in the OpenAI Version

This version replaces the original Hugging Face integration with OpenAI's API:

- **Model**: Uses `gpt-4o-mini` instead of local transformers models
- **Performance**: Cloud-based inference with faster response times
- **Quality**: More coherent and contextually aware explanations
- **Simplicity**: No need to download or manage local models
- **Configuration**: 100 token limit for concise, focused explanations

## Requirements

### Python Dependencies
```bash
pip install streamlit pandas pytrends python-dotenv altair openai
```

### API Key
You'll need an OpenAI API key to generate explanations:
1. Get your API key from [OpenAI's website](https://platform.openai.com/api-keys)
2. Set it as an environment variable: `OPENAI_API_KEY=your_key_here`
3. Or enter it directly in the app's sidebar

## Installation & Setup

1. **Clone or download** the files to your local machine

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas pytrends python-dotenv altair openai
   ```

3. **Set up your OpenAI API key** (choose one method):
   
   **Option A: Environment Variable**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```
   
   **Option B: .env file**
   ```bash
   # Create a .env file in the same directory
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```
   
   **Option C: Enter in the app**
   - You can enter your API key directly in the sidebar when running the app

4. **Run the application**:
   ```bash
   streamlit run app_openai.py
   ```

## Usage

1. **Enter a keyword** in the text input (e.g., "electric cars", "cryptocurrency", "taylor swift")

2. **View the trends chart** showing search interest over time with anomalies highlighted in red triangles

3. **Explore anomalies** by clicking on the expandable sections below the chart to see:
   - Date and percentage change
   - AI-generated explanation for why the trend might have changed

4. **Configure settings** in the sidebar:
   - View API key status
   - Enter/update your OpenAI API key
   - See which model is being used

## Example Use Cases

- **Marketing Research**: Understand when and why interest in your product category spiked
- **Content Planning**: Identify trending topics and their causes for content creation
- **Market Analysis**: Analyze consumer behavior patterns and external factors
- **Academic Research**: Study public interest correlation with real-world events

## Technical Details

### Model Configuration
- **Model**: `gpt-4o-mini`
- **Max Tokens**: 100 (for concise explanations)
- **Temperature**: 0.7 (balanced creativity and consistency)

### Data Sources
- **Google Trends**: Weekly search interest data for 2023 in the US
- **Anomaly Threshold**: ±30% week-over-week change

### Caching
- Streamlit caching is used for both Google Trends data and OpenAI client initialization
- This improves performance and reduces API calls

## Rate Limits & Costs

### Google Trends
- Built-in delays (1-3 seconds) between requests
- Automatic retry logic for rate limit errors
- Tip: Wait 2-3 minutes between searches if you encounter rate limits

### OpenAI API
- Uses GPT-4o-mini which is cost-effective for this use case
- Each explanation uses ~100 tokens
- Monitor your usage on the [OpenAI dashboard](https://platform.openai.com/usage)

## Troubleshooting

### Common Issues

1. **"No API key found"**
   - Set your `OPENAI_API_KEY` environment variable
   - Or enter it in the sidebar input field

2. **"Rate limit exceeded"**
   - Wait 2-3 minutes before trying another search
   - This is a Google Trends limitation, not OpenAI

3. **"Generation failed"**
   - Check your OpenAI API key is valid
   - Ensure you have sufficient credits in your OpenAI account
   - Check your internet connection

4. **"No trend data found"**
   - Try a different keyword
   - Some very niche terms may not have sufficient search volume

### Demo Mode
If no API key is provided, the app runs in demo mode with placeholder explanations.

## File Structure
```
g_trends v1/
├── app_openai.py          # Main OpenAI-powered application
├── app.py                 # Original Hugging Face version
├── README_openai.md       # This file
└── .env                   # Your API keys (create this file)
```

## Differences from Original Version

| Feature | Original (HF) | OpenAI Version |
|---------|---------------|----------------|
| Model | distilgpt2 (local) | gpt-4o-mini (cloud) |
| Setup | Download model weights | Just API key |
| Performance | Slower, local inference | Faster, cloud inference |
| Quality | Basic text generation | Advanced chat completion |
| Dependencies | transformers, torch | openai |
| Cost | Free (after model download) | Pay-per-use |

## Contributing

Feel free to submit issues or pull requests to improve the application. Some ideas for enhancements:

- Support for different time ranges
- Multiple keyword comparison
- Export functionality
- Different explanation styles/lengths
- Integration with other trend data sources

## License

This project is open source. Please check the license file for details.

---

**Note**: This application is for educational and research purposes. Always respect the terms of service for Google Trends and OpenAI APIs.
