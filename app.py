import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Volume vs Discount Strategy", layout="wide")

st.title("📈 Strategic Margin & Volume Analysis")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("Current Economics")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0)
current_volume = st.sidebar.number_input("Current Volume (Units)", value=50000)

st.sidebar.header("🎯 Target Thresholds")
target_mg_pct = st.sidebar.slider("Target Margin %", 5, 60, 25) / 100
target_profit_goal_m = st.sidebar.number_input("Target Profit Goal ($ Millions)", value=2.0)

st.sidebar.header("Variable Ranges")
max_total_disc = st.sidebar.slider("Max Total Discount %", 0, 50, 30) / 100

# --- CALCULATIONS ---
volume_range = np.linspace(current_volume * 0.5, current_volume * 1.5, 10)
discount_range = np.linspace(0, max_total_disc, 10)

margin_pct_matrix = np.zeros((10, 10))
total_profit_matrix_m = np.zeros((10, 10))

for i, d in enumerate(discount_range):
    for j, v in enumerate(volume_range):
        dead_net = base_price * (1 - d)
        unit_margin = dead_net - cogs_unit
        margin_pct_matrix[i, j] = unit_margin / dead_net if dead_net > 0 else 0
        total_profit_matrix_m[i, j] = (unit_margin * v) / 1_000_000

# --- VISUALS ---
HEATMAP_FONT_SIZE = 7 
col1, col2 = st.columns(2)

x_labels_k = [f"{x/1000:.1f}k" for x in volume_range]
y_labels_pct = [f"{x:.0%}" for x in discount_range]

# Create coordinate grid for contour lines (centered on heatmap cells)
X, Y = np.meshgrid(np.arange(10) + 0.5, np.arange(10) + 0.5)

with col1:
    st.subheader("Gross Margin %")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.heatmap(margin_pct_matrix, annot=True, fmt=".1%", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=x_labels_k, yticklabels=y_labels_pct, ax=ax1)
    
    # Draw Target Line for Margin %
    if margin_pct_matrix.min() <= target_mg_pct <= margin_pct_matrix.max():
        ax1.contour(X, Y, margin_pct_matrix, levels=[target_mg_pct], colors='blue', linewidths=4)
    
    ax1.set_xlabel("Volume (Units in Thousands)")
    ax1.set_ylabel("Total Discount %")
    st.pyplot(fig1)

with col2:
    st.subheader(f"Total Margin $ (Millions)")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    annot_labels_m = np.array([[f"{val:.2f}M" for val in row] for row in total_profit_matrix_m])
    
    sns.heatmap(total_profit_matrix_m, annot=annot_labels_m, fmt="", cmap="RdYlGn",
                annot_kws={"size": HEATMAP_FONT_SIZE},
                xticklabels=x_labels_k, yticklabels=y_labels_pct, ax=ax2)
    
    # Draw Target Line for Total Profit
    # Check if target is actually within the simulated range
    if total_profit_matrix_m.min() <= target_profit_goal_m <= total_profit_matrix_m.max():
        ax2.contour(X, Y, total_profit_matrix_m, levels=[target_profit_goal_m], colors='blue', linewidths=4)
    else:
        st.warning(f"Target of {target_profit_goal_m}M is outside the current simulation range ({total_profit_matrix_m.min():.2f}M to {total_profit_matrix_m.max():.2f}M).")
    
    ax2.set_xlabel("Volume (Units in Thousands)")
    ax2.set_ylabel("Total Discount %")
    st.pyplot(fig2)

# --- SUMMARY TABLE ---
st.divider()
st.subheader("📋 Sensitivity Summary")
tradeoff_data = []
for d in [0, 0.05, 0.10, 0.15, 0.20, 0.25]:
    dead_net = base_price * (1 - d)
    unit_margin = dead_net - cogs_unit
    if unit_margin > 0:
        req_v = (target_profit_goal_m * 1_000_000) / unit_margin
        v_diff_pct = (req_v - current_volume) / current_volume
        req_v_str = f"{req_v/1000:.1f}k units"
        growth_str = f"{v_diff_pct:+.1%}"
    else:
        req_v_str = "N/A"
        growth_str = "Unprofitable"
    
    tradeoff_data.append({
        "Total Discount %": f"{d:.0%}", 
        "Required Volume": req_v_str, 
        "Volume Growth Needed": growth_str
    })

st.table(pd.DataFrame(tradeoff_data))