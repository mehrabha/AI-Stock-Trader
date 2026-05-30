import json
import matplotlib.pyplot as plt


with open("validation_results.json", "r") as f:
    data = json.load(f)

labels = list(data["actions"].keys())
counts = list(data["actions"].values())
portfolio_trend = data["portfolio_trend"]
baseline_trend = data["baseline_trend"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# -----------------------------------------------------------------------
# CHART 1. Bar Plot showing the counts: BUY=GREEN, SELL=RED, HOLD=Gray
# -----------------------------------------------------------------------
colors = ['#cccccc' if label == 'HOLD' else '#2ca02c' if label == 'BUY' else '#d62728' for label in labels]

bars = ax1.bar(labels, counts, color=colors, edgecolor="black", zorder=3)

ax1.set_title("AI Agent Action Distribution (2025)", fontsize=16, fontweight='bold', pad=15)
ax1.set_xlabel("Action Type", fontsize=12, fontweight='bold')
ax1.set_ylabel("Frequency", fontsize=12, fontweight='bold')
ax1.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)


# ------------------------------
# CHART 2. Portfolio vs Baseline
# ------------------------------

# Plot both lines
ax2.plot(portfolio_trend, label='AI Portfolio', color='#2ca02c', linewidth=2.5)
ax2.plot(baseline_trend, label='Baseline w/ DCA', color='#1f77b4', linewidth=2.5, linestyle='--')

ax2.set_title("Portfolio Value Over Time (2025)", fontsize=14, fontweight='bold', pad=10)
ax2.set_xlabel("Actions Executed", fontsize=12, fontweight='bold')
ax2.set_ylabel("Account Value ($)", fontsize=12, fontweight='bold')
ax2.grid(linestyle='--', alpha=0.7)
ax2.legend(fontsize=11, loc='upper left')



import matplotlib.ticker as ticker
ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

plt.tight_layout()
plt.savefig("final_trading_dashboard.png", dpi=300)
plt.show()

