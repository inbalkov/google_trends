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
# OpenAI model configuration
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 100

# Google Trends configuration
TIMEFRAME = "2023-01-01 2023-12-31"
GEO_CODE = "US"


# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


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
        pytrends.build_payload(kw_list=[keyword], timeframe=TIMEFRAME, geo=GEO_CODE)
        
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
        f"{date.strftime('%Y-%m-%d')} in {get_geo_display_name(GEO_CODE)}. Give a concise 2-3 sentence hypothesis."
    )


@st.cache_resource(show_spinner=False)
def get_openai_client(api_key: Optional[str]):
    """Create and cache an OpenAI client.

    Returns None if the client cannot be created (e.g., missing dependency or API key).
    """
    if not api_key or api_key.strip() == "YOUR_OPENAI_API_KEY_HERE":
        return None
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        return client
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def get_openai_explanation(keyword: str, date: dt.date, direction: str, api_key: Optional[str]) -> str:
    """Call OpenAI API to get an explanation. Falls back to a dummy string if unavailable."""
    prompt = build_explanation_prompt(keyword, date, direction)

    # Fallback if API key is not provided or left as placeholder
    if not api_key or api_key.strip() == "YOUR_OPENAI_API_KEY_HERE":
        return f"(Demo) Possible reason it {direction}: seasonal events, news cycles, or viral content around {date:%Y-%m-%d}."

    # Use OpenAI API
    client = get_openai_client(api_key)
    if client is not None:
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content.strip()
            
            return "No response generated."
        except Exception as e:
            return f"(OpenAI) Generation failed: {e}"
    return "(OpenAI) Client unavailable. Ensure openai library is installed and API key is valid."


def format_timeframe_display(timeframe: str) -> str:
    """Convert timeframe from 'YYYY-MM-DD YYYY-MM-DD' to readable format."""
    try:
        start_date, end_date = timeframe.split(" ")
        start_dt = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")
        
        start_formatted = start_dt.strftime("%B %d, %Y")
        end_formatted = end_dt.strftime("%B %d, %Y")
        
        return f"{start_formatted} - {end_formatted}"
    except:
        return timeframe  # fallback to original if parsing fails

def get_geo_display_name(geo_code: str) -> str:
    """Convert geo code to display name using pycountry."""
    try:
        import pycountry
        
        # Convert 2-letter country code to country name
        country = pycountry.countries.get(alpha_2=geo_code)
        if country:
            return country.name
        else:
            return geo_code  # fallback to code if not found
            
    except Exception as e:
        # Fallback to original code if pycountry fails
        return geo_code


# -----------------------------
# UI
# -----------------------------
st.title(APP_TITLE)

with st.sidebar:
    st.caption("Settings")
    
    # Show API key status
    if OPENAI_API_KEY:
        st.success("✅ API key loaded from environment")
    else:
        st.warning("⚠️ No API key found")
        st.info("💡 **Setup**: Copy `env_template.txt` to `.env` and add your OpenAI API key")
    
    st.text_input(
        "OpenAI API Key",
        type="password",
        help="Optional. Set via .env file or environment variable OPENAI_API_KEY.",
        key="openai_key_input",
        value=OPENAI_API_KEY or "",
    )
    st.caption("Uses model: " + OPENAI_MODEL)

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

        # Create separate point layers for different types
        # Normal points (not anomalies)
        normal_points = base.transform_filter(
            alt.datum.is_anomaly == False
        ).mark_point(size=70, color="#4e79a7", shape="circle").encode(
            y="interest:Q",
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("interest:Q", title="Interest"),
                alt.Tooltip("pct_change:Q", title="WoW %", format=".1%"),
                alt.Tooltip("direction:N", title="Direction"),
            ],
        )
        
        # Anomaly spikes (green upward triangles)
        spike_points = base.transform_filter(
            (alt.datum.is_anomaly == True) & (alt.datum.direction == "spiked")
        ).mark_point(size=100, color="#22c55e", shape="triangle-up").encode(
            y="interest:Q",
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("interest:Q", title="Interest"),
                alt.Tooltip("pct_change:Q", title="WoW %", format=".1%"),
                alt.Tooltip("direction:N", title="Direction"),
            ],
        )
        
        # Anomaly drops (red downward triangles)
        drop_points = base.transform_filter(
            (alt.datum.is_anomaly == True) & (alt.datum.direction == "dropped")
        ).mark_point(size=100, color="#ef4444", shape="triangle-down").encode(
            y="interest:Q",
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("interest:Q", title="Interest"),
                alt.Tooltip("pct_change:Q", title="WoW %", format=".1%"),
                alt.Tooltip("direction:N", title="Direction"),
            ],
        )

        st.altair_chart((line + normal_points + spike_points + drop_points).properties(height=360), use_container_width=True)
    except Exception:
        # Fallback to simple Streamlit chart if Altair isn't available for some reason
        st.line_chart(trends_an.set_index("date")["interest"], height=360)

    # Display search parameters
    st.caption(f"🗓️ **Time period**: {format_timeframe_display(TIMEFRAME)} • 🌍 **Geographic region**: {get_geo_display_name(GEO_CODE)}")

    # List anomalies
    anomalies = trends_an[trends_an["is_anomaly"]].copy()

    st.subheader("Anomalies")
    if anomalies.empty:
        st.info("No anomalies detected (±30% WoW).")
    else:
        # Display each anomaly with on-demand explanation
        api_key_in_use = st.session_state.get("openai_key_input") or OPENAI_API_KEY
        for idx, row in anomalies.iterrows():
            date_val = pd.to_datetime(row["date"]).date()
            direction = row["direction"] or "changed"
            wow_str = format_pct(row["pct_change"])  # human-friendly
            
            # Create unique keys for each anomaly button and explanation
            button_key = f"explain_{keyword}_{date_val}_{idx}"
            explanation_key = f"explanation_{keyword}_{date_val}_{idx}"

            with st.expander(f"{date_val} • {direction} • WoW: {wow_str}"):
                st.write(f"Interest: {int(row['interest'])}")
                
                # Button to trigger explanation
                if st.button("🤖 Get AI Explanation", key=button_key):
                    with st.spinner("Getting explanation from OpenAI..."):
                        explanation = get_openai_explanation(keyword, date_val, direction, api_key_in_use)
                        # Store the explanation in session state
                        st.session_state[explanation_key] = explanation
                
                # Display explanation if it exists in session state
                if explanation_key in st.session_state:
                    st.write("**AI Explanation:**")
                    st.write(st.session_state[explanation_key])

else:
    st.write("Enter a keyword to explore its trend.")


# Footer / Help
st.caption(
    "Data source: Google Trends (pytrends). Anomalies = weeks with ≥±30% WoW change."
)
