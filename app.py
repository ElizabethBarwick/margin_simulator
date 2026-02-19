import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pricing Strategy Matrix", layout="wide")

st.title("📊 Pricing Strategy with Target Boundaries")

# --- SIDEBAR ---
st.sidebar.header("Fixed Costs & Goals")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0)
volume_input = st.sidebar.number_input("Projected Volume (Units)", value=5000)

st.sidebar.header("🎯 Target Thresholds")
target_mg_pct = st.sidebar.slider("Target Margin % Line", 5, 60, 25) / 100
target_profit_k = st.sidebar.number_input("Target Profit Line ($'000s)", value=100.0)

st.sidebar.header("Variable Ranges")
max_disc = st.sidebar.slider("Max On-Invoice Discount %", 0, 50, 30) / 100
max_rebate = st.sidebar.slider("Max After-Invoice Rebate %", 0, 50, 30) / 100

# --- CALCULATIONS ---
discounts = np.linspace(0, max_disc, 10)
rebates = np.linspace(0, max_rebate, 10)

margin_pct_matrix = np.zeros((10, 10))
profit_dollars_matrix = np.zeros((10, 10))

for i, d in enumerate(discounts):
    for j, r in enumerate(rebates):
        net_price = base_price * (1 - d)
        dead_net = net_price * (1 - r)
        unit_margin = dead_net - cogs_unit
        
        margin_pct_matrix[i, j] = unit_margin / dead_net if dead_net > 0 else 0
        profit_dollars_matrix[i, j] = (unit_margin * volume_input) / 1000 

# --- VISUALS ---
HEATMAP_FONT_SIZE = 8
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Margin % (Target: {target_mg_pct:.0%})")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.heatmap(margin_pct_matrix, annot=True, fmt=".1%", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=[f"{x:.0%}" for x in rebates],
                yticklabels=[f"{x:.0%}" for x in discounts], ax=ax1)
    ax1.contour(np.arange(10)+0.5, np.arange(10)+0.5, margin_pct_matrix, 
                levels=[target_mg_pct], colors='blue', linewidths=3)
    st.pyplot(fig1)

with col2:
    st.subheader(f"Total Margin $ (Target: {target_profit_k}k)")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    annot_labels = np.array([[f"{val:.1f}k" for val in row] for row in profit_dollars_matrix])
    sns.heatmap(profit_dollars_matrix, annot=annot_labels, fmt="", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=[f"{x:.0%}" for x in rebates],
                yticklabels=[f"{x:.0%}" for x in discounts], ax=ax2)
    ax2.contour(np.arange(10)+0.5, np.arange(10)+0.5, profit_dollars_matrix, 
                levels=[target_profit_k], colors='blue', linewidths=3)
    st.pyplot(fig2)

# --- SUMMARY TABLE LOGIC ---
st.divider()
st.subheader("📋 Negotiation Cheat Sheet")
st.write(f"Maximum allowable **After-Invoice Rebate** to maintain a **{target_mg_pct:.1%}+** Gross Margin:")

summary_data = []
# Calculate required dead net for the target margin
# Dead Net = COGS / (1 - target_margin)
req_dead_net = cogs_unit / (1 - target_mg_pct)

for d in [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
    net_price = base_price * (1 - d)
    # Solve for r: req_dead_net = net_price * (1 - r) -> r = 1 - (req_dead_net / net_price)
    if net_price > req_dead_net:
        max_r = 1 - (req_dead_net / net_price)
        status = "✅ Viable"
    else:
        max_r = 0
        status = "❌ Impossible (Base too low)"
    
    summary_data.append({
        "On-Invoice Discount": f"{d:.0%}",
        "Max Rebate Allowed": f"{max_r:.1%}",
        "Dead Net Price ($)": f"${req_dead_net:.2f}",
        "Status": status
    })

df_summary = pd.DataFrame(summary_data)
st.table(df_summary)

st.info("The table above assumes you want to keep the Margin % fixed. If the status is 'Impossible', the on-invoice discount alone has already pushed you below your target margin.")