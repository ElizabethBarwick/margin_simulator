import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pricing & Margin Explorer", layout="wide")

st.title("📊 Pricing & Margin Strategy Tool")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Unit Economics")
price_unit = st.sidebar.number_input("Base Price/Unit ($)", value=100.0, step=1.0)
cogs_unit = st.sidebar.number_input("COGS/Unit ($)", value=60.0, step=1.0)

st.sidebar.header("Discount Structure")
on_inv_pct = st.sidebar.slider("On-Invoice Discount (%)", 0.0, 50.0, 10.0) / 100
after_inv_pct = st.sidebar.slider("After-Invoice (Rebate) (%)", 0.0, 50.0, 5.0) / 100

st.sidebar.header("Target Goals")
target_gm = st.sidebar.slider("Desired Gross Margin %", 10, 80, 30) / 100

# --- CALCULATIONS ---
net_price = price_unit * (1 - on_inv_pct)
dead_net_price = net_price * (1 - after_inv_pct)
current_gm_dollars = dead_net_price - cogs_unit
current_gm_pct = current_gm_dollars / dead_net_price if dead_net_price > 0 else 0

# --- METRICS DISPLAY ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Price (On-Inv)", f"${net_price:.2f}")
col2.metric("Dead Net Price", f"${dead_net_price:.2f}")
col3.metric("Current GM %", f"{current_gm_pct:.1%}")
col4.metric("GM $ / Unit", f"${current_gm_dollars:.2f}")

# --- REQUIRED VOLUME CALCULATION ---
st.divider()
st.subheader("Volume Requirements")
target_profit = st.number_input("Enter Total Target Gross Profit ($)", value=10000, step=1000)

if current_gm_dollars > 0:
    req_vol = target_profit / current_gm_dollars
    st.info(f"To achieve **${target_profit:,}** in profit at a **{current_gm_pct:.1%}** margin, you must sell **{int(req_vol):,}** units.")
else:
    st.error("Current pricing is below COGS. Increase price or reduce discounts to calculate volume.")

# --- HEATMAP ANALYSIS ---
st.divider()
st.subheader("Sensitivity Analysis: Total Discount % vs. Volume")
st.write("This heatmap shows how **Gross Margin %** changes as you vary Total Discount and Volume.")

# Create ranges for the heatmap
discount_range = np.linspace(0, 0.4, 10) # 0% to 40% total discount
volume_range = np.linspace(int(req_vol*0.5), int(req_vol*1.5), 10) if current_gm_dollars > 0 else np.linspace(100, 1000, 10)

# Generate Matrix
heatmap_data = []
for d in discount_range:
    row = []
    for v in volume_range:
        # Simplified: Price * (1 - Total Discount) - COGS
        temp_dead_net = price_unit * (1 - d)
        temp_gm = (temp_dead_net - cogs_unit) / temp_dead_net if temp_dead_net > 0 else 0
        row.append(temp_gm)
    heatmap_data.append(row)

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(
    heatmap_data, 
    annot=True, 
    fmt=".1%", 
    xticklabels=[f"{int(x)}" for x in volume_range],
    yticklabels=[f"{x:.0%}" for x in discount_range],
    cmap="RdYlGn",
    ax=ax
)
plt.xlabel("Volume (Units)")
plt.ylabel("Total Discount % (Combined)")
st.pyplot(fig)