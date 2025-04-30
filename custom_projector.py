def custom_pitcher_projection(row):
    k9 = row.get('K/9', 0)
    opp_k_pct = row.get('Opponent K%', 0)
    era = row.get('ERA', 0)
    opp_wrc_plus = row.get('Opponent wRC+', 100)
    ballpark = row.get('Ballpark Factor', 0)
    recent = row.get('Recent Form', 0)

    return (
        (k9 * opp_k_pct * 0.2)
        - (era * 1.25)
        - (opp_wrc_plus * 0.05)
        + ballpark
        + recent
    )

def custom_hitter_projection(row):
    avg = row.get('AVG', 0)
    iso = row.get('ISO', 0)
    wrc_plus = row.get('wRC+', 100)
    lineup_pos = row.get('Lineup Pos', 6)
    ballpark = row.get('Ballpark Factor', 0)
    recent = row.get('Recent Form', 0)
    opp_pitch_grade = row.get('Opp Pitcher Grade', 3)

    lineup_bonus = {1: 1.5, 2: 1.2, 3: 1.8, 4: 1.8, 5: 1.5}.get(lineup_pos, 1.0)

    return (
        (avg * 10)
        + (iso * 15)
        + (wrc_plus / 100 * ballpark)
        + recent
        + lineup_bonus
        - (opp_pitch_grade * 1.25)
    )

def apply_projections(df):
    projections = []
    for _, row in df.iterrows():
        if row['Roster Position'] == 'P':
            proj = custom_pitcher_projection(row)
        else:
            proj = custom_hitter_projection(row)
        projections.append(proj)
    df['Projected'] = projections
    return df
