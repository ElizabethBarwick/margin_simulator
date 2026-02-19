import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Volume Strategy Planner", layout="wide")

st.title("📈 Volume Requirement Explorer")
st.write("Calculate the volume needed to hit your margin goals across different price and discount points.")

# --- SIDEBAR: FIXED TARGETS ---
st.sidebar.header("Fixed Targets")
cogs_unit = st.sidebar.number_input("COGS per Unit ($)", value=60.0, step=1.0)
target_profit_goal = st.sidebar.number_input("Total Gross Profit Goal ($)", value=50000, step=5000)

st.sidebar.header("Variable Ranges (for Heatmap)")
min_price = st.sidebar.number_input("Min Base Price ($)", value=80.0)
max_price = st.sidebar.number_input("Max Base Price ($)", value=150.0)
max_discount = st.sidebar.slider("Max Total Discount %", 0, 50, 30) / 100

# --- DATA GENERATION ---
# Create 10 steps for Price and 10 steps for Discount
prices = np.linspace(min_price, max_price, 10)
discounts = np.linspace(0, max_discount, 10)

# Calculate Volume Matrix
volume_matrix = np.zeros((len(discounts), len(prices)))

for i, d in enumerate(discounts):
    for j, p in enumerate(prices):
        net_price = p * (1 - d)
        margin_per_unit = net_price - cogs_unit
        
        if margin_per_unit > 0:
            volume_matrix[i, j] = target_profit_goal / margin_per_unit
        else:
            volume_matrix[i, j] = np.nan # Mark as unprofitable

# Convert to DataFrame for easier plotting
df_heatmap = pd.DataFrame(
    volume_matrix, 
    index=[f"{d:.0%}" for d in discounts], 
    columns=[f"${p:.2f}" for p in prices]
)

# --- VISUALIZATION ---
st.subheader(f"Heatmap: Units Needed to Net ${target_profit_goal:,} Profit")
st.caption("Grey cells indicate the 'Dead Zone' where price is below COGS.")

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(
    df_heatmap, 
    annot=True, 
    fmt=",.0f", # Format as whole numbers with commas
    cmap="YlOrRd_r", # Reverse YlOrRd so lower volume (better) is greener/lighter
    cbar_kws={'label': 'Units Required'},
    mask=df_heatmap.isnull(),
    ax=ax
)
plt.xlabel("Base Price ($)")
plt.ylabel("Total Discount (%)")
st.pyplot(fig)

# --- KEY INSIGHTS ---
st.divider()
best_case = np.nanmin(volume_matrix)
worst_case = np.nanmax(volume_matrix)

col1, col2 = st.columns(2)
with col1:
    st.success(f"**Best Case Scenario:** Sell **{int(best_case):,} units** (High Price / Low Discount)")
with col2:
    st.warning(f"**Worst Case Scenario:** Sell **{int(worst_case):,} units** (Low Price / High Discount)")