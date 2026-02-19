import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Volume vs Discount Strategy", layout="wide")

st.title("📈 Volume & Discount Sensitivity Analysis")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("Current Economics")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0)
current_volume = st.sidebar.number_input("Current Volume (Units)", value=5000)

st.sidebar.header("🎯 Target Thresholds")
target_mg_pct = st.sidebar.slider("Target Margin %", 5, 60, 25) / 100
target_profit_goal_k = st.sidebar.number_input("Target Profit Goal ($'000s)", value=150.0)

st.sidebar.header("Variable Ranges")
max_total_disc = st.sidebar.slider("Max Total Discount %", 0, 50, 30) / 100

# --- CALCULATIONS ---
# Range: 50% to 150% of current volume
volume_range = np.linspace(current_volume * 0.5, current_volume * 1.5, 10)
discount_range = np.linspace(0, max_total_disc, 10)

margin_pct_matrix = np.zeros((10, 10))
total_profit_matrix_k = np.zeros((10, 10))

for i, d in enumerate(discount_range):
    for j, v in enumerate(volume_range):
        dead_net = base_price * (1 - d)
        unit_margin = dead_net - cogs_unit
        
        margin_pct_matrix[i, j] = unit_margin / dead_net if dead_net > 0 else 0
        # Scaling to thousands for the display
        total_profit_matrix_k[i, j] = (unit_margin * v) / 1000

# --- VISUALS ---
HEATMAP_FONT_SIZE = 7 # Small enough for 10x10 grids
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gross Margin %")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.heatmap(margin_pct_matrix, annot=True, fmt=".1%", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=[f"{int(x)}" for x in volume_range],
                yticklabels=[f"{x:.0%}" for x in discount_range], ax=ax1)
    
    # Target Line for Margin %
    ax1.contour(np.arange(10)+0.5, np.arange(10)+0.5, margin_pct_matrix, 
                levels=[target_mg_pct], colors='blue', linewidths=3)
    
    ax1.set_xlabel("Volume (Units)")
    ax1.set_ylabel("Total Discount %")
    st.pyplot(fig1)

with col2:
    st.subheader(f"Total Margin $ (in '000s)")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    
    # Custom labels to append 'k' to the thousands
    annot_labels = np.array([[f"{val:.1f}k" for val in row] for row in total_profit_matrix_k])
    
    sns.heatmap(total_profit_matrix_k, annot=annot_labels, fmt="", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=[f"{int(x)}" for x in volume_range],
                yticklabels=[f"{x:.0%}" for x in discount_range], ax=ax2)
    
    # Target Line for Total Profit Goal (in thousands)
    if total_profit_matrix_k.min() < target_profit_goal_k < total_profit_matrix_k.max():
        ax2.contour(np.arange(10)+0.5, np.arange(10)+0.5, total_profit_matrix_k, 
                    levels=[target_profit_goal_k], colors='blue', linewidths=3)
    
    ax2.set_xlabel("Volume (Units)")
    ax2.set_ylabel("Total Discount %")
    st.pyplot(fig2)

# --- SUMMARY TABLE ---
st.divider()
st.subheader("📋 Volume Required for Target Profit")
st.write(f"To hit your **${target_profit_goal_k}k** goal at different discount depths:")

tradeoff_data = []
for d in [0, 0.05, 0.10, 0.15, 0.20, 0.25]:
    dead_net = base_price * (1 - d)
    unit_margin = dead_net - cogs_unit
    
    if unit_margin > 0:
        req_v = (target_profit_goal_k * 1000) / unit_margin
        v_diff = req_v - current_volume
        v_pct = (v_diff / current_volume)
    else:
        req_v = 0
        v_pct = 0
    
    tradeoff_data.append({
        "Total Discount %": f"{d:.0%}",
        "Required Volume": f"{int(req_v):,}" if req_v > 0 else "N/A",
        "vs. Current Volume": f"{v_pct:+.1%}" if req_v > 0 else "N/A"
    })

st.table(pd.DataFrame(tradeoff_data))