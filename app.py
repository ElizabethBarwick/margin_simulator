import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Discount & Rebate Impact", layout="wide")

st.title("📉 Discount vs. Rebate Margin Explorer")
st.write("Analyze how layering on-invoice discounts and after-invoice rebates impacts your final Gross Margin.")

# --- SIDEBAR: FIXED INPUTS ---
st.sidebar.header("Fixed Unit Economics")
base_price = st.sidebar.number_input("Base List Price ($)", value=100.0, step=1.0)
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0, step=1.0)
volume_input = st.sidebar.number_input("Projected Volume (Units)", value=1000, step=100)

st.sidebar.header("Analysis Ranges")
max_disc = st.sidebar.slider("Max On-Invoice Discount %", 0, 50, 30) / 100
max_rebate = st.sidebar.slider("Max After-Invoice Rebate %", 0, 50, 30) / 100

# --- CALCULATIONS ---
# 1. Create ranges for the axes
discount_range = np.linspace(0, max_disc, 10)
rebate_range = np.linspace(0, max_rebate, 10)

# 2. Initialize Matrices
margin_pct_matrix = np.zeros((len(discount_range), len(rebate_range)))
total_profit_matrix = np.zeros((len(discount_range), len(rebate_range)))

for i, d in enumerate(discount_range):
    for j, r in enumerate(rebate_range):
        # Calculation Logic:
        # Step 1: Apply On-Invoice Discount
        net_price = base_price * (1 - d)
        # Step 2: Apply After-Invoice Rebate (usually calculated off Net)
        dead_net_price = net_price * (1 - r)
        
        # Step 3: Margin Math
        margin_dollars = dead_net_price - cogs_unit
        margin_pct = margin_dollars / dead_net_price if dead_net_price > 0 else 0
        
        margin_pct_matrix[i, j] = margin_pct
        total_profit_matrix[i, j] = margin_dollars * volume_input

# --- UI LAYOUT ---
# Metric Cards
current_net = base_price - cogs_unit
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Max Possible Margin %", f"{(current_net/base_price):.1%}")
c2.metric("Breakeven Price (Dead Net)", f"${cogs_unit:.2f}")
c3.metric("Current COGS", f"${cogs_unit:.2f}")

# --- HEATMAPS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Impact on Gross Margin %")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        margin_pct_matrix,
        annot=True,
        fmt=".1%",
        cmap="RdYlGn",
        xticklabels=[f"{x:.0%}" for x in rebate_range],
        yticklabels=[f"{x:.0%}" for x in discount_range],
        ax=ax1
    )
    plt.xlabel("After-Invoice Rebate %")
    plt.ylabel("On-Invoice Discount %")
    st.pyplot(fig1)

with col_right:
    st.subheader(f"Impact on Total Margin $ (at {volume_input:,} units)")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        total_profit_matrix,
        annot=True,
        fmt="$,.0f",
        cmap="RdYlGn",
        xticklabels=[f"{x:.0%}" for x in rebate_range],
        yticklabels=[f"{x:.0%}" for x in discount_range],
        ax=ax2
    )
    plt.xlabel("After-Invoice Rebate %")
    plt.ylabel("On-Invoice Discount %")
    st.pyplot(fig2)

st.info("**Analysis Tip:** On-invoice discounts reduce the 'top line' immediately, while rebates are often paid later. This tool shows the combined 'Dead Net' effect on your bottom line.")