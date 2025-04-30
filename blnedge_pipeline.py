import pandas as pd
from custom_projector import apply_projections
from blnedge_lp_optimizer import optimize_lineup

# Load salary file (update filename if needed)
df = pd.read_csv("FanDuel-Sample.csv")

# Combine names
df['Player'] = df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')
df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
df = df[df['Injury Indicator'].isna()]
df = df[(df['Roster Position'] != 'P') | (df['Probable Pitcher'] == 'Yes')]

# Add mock stats
df['K/9'] = 9.5
df['Opponent K%'] = 0.23
df['ERA'] = 3.80
df['Opponent wRC+'] = 100
df['Ballpark Factor'] = 0
df['Recent Form'] = 0.5
df['AVG'] = 0.265
df['ISO'] = 0.180
df['wRC+'] = 110
df['Lineup Pos'] = 3
df['Opp Pitcher Grade'] = 3

# Apply projections
df = apply_projections(df)

# Run optimizer
result = optimize_lineup(df)

# Output
if result is not None:
    result.to_csv("Optimized_Lineup.csv", index=False)
    print("✅ Optimized lineup saved to Optimized_Lineup.csv")
else:
    print("❌ No valid lineup found. Check constraints.")
