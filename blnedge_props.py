import pandas as pd

def generate_prop_edges(props_df, projections_df):
    # Ensure both have 'Player' and 'Projected'
    merged = props_df.merge(projections_df[['Player', 'Projected']], on='Player', how='left')
    merged['Projected'] = pd.to_numeric(merged['Projected'], errors='coerce')
    merged['Line'] = pd.to_numeric(merged['Line'], errors='coerce')

    # Calculate edge
    merged['Edge'] = merged['Projected'] - merged['Line']
    merged = merged.dropna(subset=['Edge'])
    merged = merged.sort_values(by='Edge', ascending=False)
    return merged

# Example CLI run (optional):
if __name__ == '__main__':
    props = pd.read_csv("Mock_FanDuel_Props.csv")
    salary = pd.read_csv("FanDuel-Sample.csv")
    salary['Player'] = salary['First Name'].fillna('') + ' ' + salary['Last Name'].fillna('')
    from custom_projector import apply_projections
    salary = apply_projections(salary)
    top_props = generate_prop_edges(props, salary)
    top_props.to_csv("Top_Prop_Picks.csv", index=False)
    print("✅ Saved Top_Prop_Picks.csv")
