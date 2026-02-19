import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px # Added for interactive bubble chart

st.set_page_config(page_title="Executive Pricing Dashboard", layout="wide")

st.title("🚀 Master Pricing & Volume Strategy")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("Unit Economics")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0)

st.sidebar.header("Variable Ranges")
vol_min, vol_max = st.sidebar.slider("Volume Range (Units)", 1000, 100000, (10000, 75000))
disc_min, disc_max = st.sidebar.slider("Discount Range %", 0, 50, (5, 35))

# --- DATA GENERATION ---
# Create a dataframe of random scenarios within your ranges to populate the chart
np.random.seed(42)
n_scenarios = 200
vols = np.random.uniform(vol_min, vol_max, n_scenarios)
discs = np.random.uniform(disc_min/100, disc_max/100, n_scenarios)

df = pd.DataFrame({'Volume': vols, 'Discount_Pct': discs})

# Core Calculations
df['Dead_Net'] = base_price * (1 - df['Discount_Pct'])
df['Margin_Pct'] = (df['Dead_Net'] - cogs_unit) / df['Dead_Net']
df['Total_Margin_M'] = ((df['Dead_Net'] - cogs_unit) * df['Volume']) / 1_000_000
df['Volume_K'] = df['Volume'] / 1000

# --- THE MASTER CHART ---
st.subheader("The 'Profit Frontier' Analysis")
st.write("This chart combines all four metrics. Look for the **large green bubbles** in the top right—these represent high-volume, high-profit deals with healthy margins.")

fig = px.scatter(
    df,
    x="Volume_K",
    y="Total_Margin_M",
    size="Discount_Pct",
    color="Margin_Pct",
    hover_name="Volume",
    hover_data={
        'Volume_K': ':.1fk',
        'Total_Margin_M': ':$.2fM',
        'Margin_Pct': ':.1%',
        'Discount_Pct': ':.1%'
    },
    color_continuous_scale="RdYlGn",
    labels={
        "Volume_K": "Volume (Thousands)",
        "Total_Margin_M": "Total Margin ($ Millions)",
        "Margin_Pct": "Gross Margin %",
        "Discount_Pct": "Discount Depth"
    }
)

fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# --- KEY INSIGHTS ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**X-Axis / Y-Axis**\n\nShows the correlation between sales volume and cash flow.")
with col2:
    st.info("**Color (Red to Green)**\n\nShows unit profitability. Red bubbles are 'buying volume' at the expense of margin.")
with col3:
    st.info("**Bubble Size**\n\nRepresents Discount %. Larger bubbles mean you are giving away more value to get the deal.")