import os
import datetime as dt
from typing import List, Dict, Optional

import pandas as pd
import streamlit as st
from pytrends.request import TrendReq

# -----------------------------
# Config / Constants
# -----------------------------
APP_TITLE = "Keyword Trend Explorer"
# MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2" # Large model, 7B params 
MODEL_ID = "distilgpt2" # Small model, 124M params


# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Get Hugging Face token from environment variable
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")


# Streamlit page config
st.set_page_config(page_title=APP_TITLE, layout="centered")

# -----------------------------
# Utility Functions
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_trends_2023_us(keyword: str) -> pd.DataFrame:
    """Fetch weekly Google Trends data for 2023 in the US for a keyword.

    Returns a DataFrame with columns: [date, interest]
    """
    import time
    import random
    
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(kw_list=[keyword], timeframe="2023-01-01 2023-12-31", geo="US")
        
        # Add a small random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        df = pytrends.interest_over_time()
        
        if df is None or df.empty:
            return pd.DataFrame(columns=["date", "interest"])  # empty frame

        # df index is datetime; column is the keyword, plus 'isPartial'
        series = df[keyword].copy()
        series = series.asfreq("W-SUN") if series.index.freq is None else series

        out = pd.DataFrame({
            "date": series.index.tz_localize(None),
            "interest": series.values,
        })
        return out.reset_index(drop=True)
        
    except Exception as e:
        if "429" in str(e) or "TooManyRequests" in str(e):
            st.error("⚠️ Rate limit exceeded. Please wait a few minutes before trying again.")
            return pd.DataFrame(columns=["date", "interest"])
        else:
            st.error(f"Error fetching trends data: {e}")
            return pd.DataFrame(columns=["date", "interest"])


def compute_anomalies(df: pd.DataFrame, change_threshold: float = 0.30) -> pd.DataFrame:
    """Compute week-over-week percentage change anomalies.

    An anomaly is when abs(pct_change) >= change_threshold (default 30%).
    Adds columns: pct_change, is_anomaly, direction ('spiked'/'dropped'/None)
    """
    if df.empty:
        return df.assign(pct_change=pd.Series(dtype=float), is_anomaly=False, direction=None)

    out = df.copy()

    # Avoid division by zero by replacing zero previous interest with NaN during pct_change
    interest = out["interest"].astype(float)
    pct = interest.pct_change()

    out["pct_change"] = pct
    out["is_anomaly"] = pct.abs() >= change_threshold
    out["direction"] = out["pct_change"].apply(lambda x: "spiked" if pd.notna(x) and x > 0 else ("dropped" if pd.notna(x) and x < 0 else None))

    return out


def format_pct(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{x * 100:.1f}%"


def build_explanation_prompt(keyword: str, date: dt.date, direction: str) -> str:
    return (
        f"Explain why search interest in '{keyword}' might have {direction} on "
        f"{date.strftime('%Y-%m-%d')} in the US. Give a concise 2-3 sentence hypothesis."
    )


@st.cache_resource(show_spinner=False)
def get_textgen_pipeline(token: Optional[str]):
    """Create and cache a local transformers text-generation pipeline for the configured model.

    Returns None if the pipeline cannot be created (e.g., missing dependency or token).
    """
    if not token or token.strip() == "YOUR_HF_API_TOKEN_HERE":
        return None
    try:
        from transformers import pipeline  # type: ignore

        # Pass token for private/gated models if needed.
        # Some models require trust_remote_code; keep off by default for safety.
        pipe = pipeline(
            task="text-generation",
            model=MODEL_ID,
            token=token,  # Needed if model is gated/private
            trust_remote_code=True,
            device="cpu"  # Force CPU usage
            # device_map="auto"  # Uncomment if GPU/accelerate available
        )
        return pipe
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def get_hf_explanation(keyword: str, date: dt.date, direction: str, token: Optional[str]) -> str:
    """Call Hugging Face Inference API to get an explanation. Falls back to a dummy string if unavailable."""
    prompt = build_explanation_prompt(keyword, date, direction)

    # Fallback if token is not provided or left as placeholder
    if not token or token.strip() == "YOUR_HF_API_TOKEN_HERE":
        return f"(Demo) Possible reason it {direction}: seasonal events, news cycles, or viral content around {date:%Y-%m-%d}."

    # Use local transformers pipeline
    textgen = get_textgen_pipeline(token)
    if textgen is not None:
        try:
            outputs = textgen(
                prompt,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                return_full_text=False,
            )
            # transformers returns list of dicts with 'generated_text'
            if isinstance(outputs, list) and outputs:
                text = outputs[0].get("generated_text")
                if isinstance(text, str):
                    return text.strip()
            # Some pipelines may return a string directly
            if isinstance(outputs, str):
                return outputs.strip()
            return str(outputs)
        except Exception as e:
            return f"(Pipeline) Generation failed: {e}"
    return "(Pipeline) Text-generation pipeline unavailable. Ensure transformers is installed and model is accessible."


# -----------------------------
# UI
# -----------------------------
st.title(APP_TITLE)

with st.sidebar:
    st.caption("Settings")
    
    # Show API key status
    if HUGGINGFACE_API_TOKEN:
        st.success("✅ API key loaded from environment")
    else:
        st.warning("⚠️ No API key found")
        st.info("💡 **Setup**: Copy `env_template.txt` to `.env` and add your Hugging Face token")
    
    st.text_input(
        "Hugging Face API Token",
        type="password",
        help="Optional. Set via .env file or environment variable HUGGINGFACE_API_TOKEN.",
        key="hf_token_input",
        value=HUGGINGFACE_API_TOKEN or "",
    )
    st.caption("Uses model: " + MODEL_ID)

keyword = st.text_input("Enter a keyword or phrase", placeholder="e.g., electric cars", key="keyword_input")

if keyword:
    with st.spinner("Fetching Google Trends data..."):
        trends_df = fetch_trends_2023_us(keyword)
    
    # Add helpful information about rate limiting
    st.info("💡 **Tip**: If you get rate limit errors, wait 2-3 minutes between searches.")

    if trends_df.empty:
        st.warning("No trend data found. Try another keyword.")
        st.stop()

    # Compute anomalies
    trends_an = compute_anomalies(trends_df, change_threshold=0.30)

    # Chart with anomalies highlighted using Altair
    try:
        import altair as alt

        base = alt.Chart(trends_an).encode(x=alt.X("date:T", title="Week"))

        line = base.mark_line(color="#4e79a7").encode(y=alt.Y("interest:Q", title="Search interest"))

        points = base.mark_point(size=70).encode(
            y="interest:Q",
            color=alt.condition(alt.datum.is_anomaly, alt.value("#e15759"), alt.value("#4e79a7")),
            shape=alt.condition(alt.datum.is_anomaly, alt.value("triangle"), alt.value("circle")),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("interest:Q", title="Interest"),
                alt.Tooltip("pct_change:Q", title="WoW %", format=".1%"),
                alt.Tooltip("direction:N", title="Direction"),
            ],
        )

        st.altair_chart((line + points).properties(height=360), use_container_width=True)
    except Exception:
        # Fallback to simple Streamlit chart if Altair isn't available for some reason
        st.line_chart(trends_an.set_index("date")["interest"], height=360)

    # List anomalies
    anomalies = trends_an[trends_an["is_anomaly"]].copy()

    st.subheader("Anomalies")
    if anomalies.empty:
        st.info("No anomalies detected (±30% WoW).")
    else:
        # Display each anomaly with explanation
        token_in_use = st.session_state.get("hf_token_input") or HUGGINGFACE_API_TOKEN
        for _, row in anomalies.iterrows():
            date_val = pd.to_datetime(row["date"]).date()
            direction = row["direction"] or "changed"
            wow_str = format_pct(row["pct_change"])  # human-friendly

            with st.expander(f"{date_val} • {direction} • WoW: {wow_str}"):
                st.write(f"Interest: {int(row['interest'])}")
                with st.spinner("Getting explanation..."):
                    explanation = get_hf_explanation(keyword, date_val, direction, token_in_use)
                st.write(explanation)

else:
    st.write("Enter a keyword to explore its trend.")


# Footer / Help
st.caption(
    "Data source: Google Trends (pytrends). Anomalies = weeks with ≥±30% WoW change."
)
