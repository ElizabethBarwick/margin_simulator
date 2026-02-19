import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pricing Strategy Matrix", layout="wide")

st.title("🎯 Strategic Pricing & Volume Mapper")
st.write("Determine the **Base Price** and **Volume** required to hit your specific Margin targets.")

# --- INPUTS ---
col_a, col_b = st.columns(2)

with col_a:
    st.header("Financial Targets")
    target_profit_dollars = st.number_input("Total Margin Dollars Needed ($)", value=50000, step=5000)
    target_margin_pct = st.slider("Desired Gross Margin %", 5, 75, 25) / 100
    cogs_unit = st.number_input("COGS per Unit ($)", value=60.0, step=1.0)

with col_b:
    st.header("Discount Variables")
    st.info("The heatmap will show how your **Base (List) Price** must change to accommodate these discounts while maintaining your target margin.")
    max_discount = st.slider("Max Total Discount % to Model", 0, 60, 40) / 100

# --- CALCULATIONS ---
# 1. Calculate the Fixed Net Price required to hit the Margin %
# Formula: Net = COGS / (1 - Margin%)
req_net_price = cogs_unit / (1 - target_margin_pct)
margin_per_unit = req_net_price - cogs_unit
req_volume = target_profit_dollars / margin_per_unit

# --- DATA GENERATION FOR HEATMAP ---
# We vary Total Discount and see what the BASE PRICE needs to be
discounts = np.linspace(0, max_discount, 10)
# We can also vary the Profit Goal to see how Volume scales
profit_goals = np.linspace(target_profit_dollars * 0.5, target_profit_dollars * 1.5, 10)

price_matrix = np.zeros((len(discounts), len(profit_goals)))

for i, d in enumerate(discounts):
    for j, g in enumerate(profit_goals):
        # Base Price needed to reach req_net_price after discount d
        # Formula: Base = Net / (1 - d)
        if d < 1:
            price_matrix[i, j] = req_net_price / (1 - d)
        else:
            price_matrix[i, j] = np.nan

df_heatmap = pd.DataFrame(
    price_matrix,
    index=[f"{d:.0%}" for d in discounts],
    columns=[f"${g/1000:.0f}k" for g in profit_goals]
)

# --- DISPLAY METRICS ---
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Required Net Price", f"${req_net_price:.2f}")
m2.metric("Required Volume (Units)", f"{int(req_volume):,}")
m3.metric("Profit per Unit", f"${margin_per_unit:.2f}")

# --- HEATMAP ---
st.subheader("Required Base Price vs. Profit Goal")
st.write(f"To maintain a **{target_margin_pct:.0%} margin**, find your required **Base Price** based on discount depth and profit goals:")

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(
    df_heatmap, 
    annot=True, 
    fmt=".2f", 
    cmap="YlGnBu", 
    cbar_kws={'label': 'Required Base Price ($)'},
    ax=ax
)
plt.xlabel("Total Profit Goal ($)")
plt.ylabel("Total Discount % Offered")
st.pyplot(fig)

st.caption("Note: Since Margin % is fixed by your input, the Volume Required remains constant for a specific Profit Goal, but the Base Price must increase as you offer deeper discounts.")