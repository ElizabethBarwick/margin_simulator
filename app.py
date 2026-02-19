import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pricing Strategy Matrix", layout="wide")

st.title("📊 Pricing & Margin Explorer")

# --- SIDEBAR ---
st.sidebar.header("Fixed Costs & Goals")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0)
target_profit_goal = st.sidebar.number_input("Total Margin Goal ($)", value=100000, step=10000)

st.sidebar.header("Variable Ranges")
max_disc = st.sidebar.slider("Max On-Invoice Discount %", 0, 50, 25) / 100
max_rebate = st.sidebar.slider("Max After-Invoice Rebate %", 0, 50, 25) / 100

# --- CALCULATIONS ---
discounts = np.linspace(0, max_disc, 10)
rebates = np.linspace(0, max_rebate, 10)

margin_pct_matrix = np.zeros((10, 10))
profit_dollars_matrix = np.zeros((10, 10))

# Arbitrary volume for the "Total Margin $" view 
# (You could also make this a slider)
volume_input = 5000 

for i, d in enumerate(discounts):
    for j, r in enumerate(rebates):
        net_price = base_price * (1 - d)
        dead_net = net_price * (1 - r)
        unit_margin = dead_net - cogs_unit
        
        margin_pct_matrix[i, j] = unit_margin / dead_net if dead_net > 0 else 0
        profit_dollars_matrix[i, j] = (unit_margin * volume_input) / 1000 # Scaling to thousands

# --- VISUALS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gross Margin %")
    fig1, ax1 = plt.subplots()
    sns.heatmap(margin_pct_matrix, annot=True, fmt=".1%", cmap="RdYlGn",
                xticklabels=[f"{x:.0%}" for x in rebates],
                yticklabels=[f"{x:.0%}" for x in discounts], ax=ax1)
    ax1.set_xlabel("Rebate %")
    ax1.set_ylabel("Discount %")
    st.pyplot(fig1)

with col2:
    st.subheader(f"Total Margin $ (in '000s) @ {volume_input:,} units")
    fig2, ax2 = plt.subplots()
    
    # Custom annotation: adding 'k' suffix manually for clarity
    annot_labels = np.array([[f"{val:.1f}k" for val in row] for row in profit_dollars_matrix])
    
    sns.heatmap(profit_dollars_matrix, 
                annot=annot_labels, 
                fmt="", # Must be empty when using custom annot labels
                cmap="RdYlGn",
                xticklabels=[f"{x:.0%}" for x in rebates],
                yticklabels=[f"{x:.0%}" for x in discounts], 
                ax=ax2)
    ax2.set_xlabel("Rebate %")
    ax2.set_ylabel("Discount %")
    st.pyplot(fig2)

st.caption("Values in the right chart represent thousands of dollars (e.g., 50.0k = $50,000).")