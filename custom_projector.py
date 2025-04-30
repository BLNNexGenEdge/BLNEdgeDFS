def custom_pitcher_projection(row):
    try:
        k9 = float(row.get('K/9', 8.0))
        opp_k_pct = float(row.get('Opponent K%', 0.22))
        era = float(row.get('ERA', 4.00))
        wrc_plus = float(row.get('Opponent wRC+', 100))
        ballpark = float(row.get('Ballpark Factor', 0))
        recent = float(row.get('Recent Form', 0.5))

        strikeout_score = k9 * opp_k_pct * 2.5
        efficiency_score = max(0, 10 - era)
        difficulty_penalty = (wrc_plus - 100) * 0.05

        projection = (
            strikeout_score +
            efficiency_score -
            difficulty_penalty +
            ballpark +
            recent
        )

        return round(projection, 2)
    except Exception as e:
        print(f"⚠️ Error projecting pitcher {row.get('Player')}: {e}")
        return 0.0


def custom_hitter_projection(row):
    avg = float(row.get('AVG', 0.265))
    iso = float(row.get('ISO', 0.160))
    wrc_plus = float(row.get('wRC+', 100))
    lineup_pos = int(row.get('Lineup Pos', 5))
    ballpark = float(row.get('Ballpark Factor', 0))
    recent = float(row.get('Recent Form', 0.5))
    opp_pitch = float(row.get('Opp Pitcher Grade', 3))

    lineup_bonus = {1: 1.6, 2: 1.4, 3: 1.8, 4: 1.7}.get(lineup_pos, 1.0)

    return round(
        avg * 12 +
        iso * 20 +
        wrc_plus * 0.1 +
        lineup_bonus +
        ballpark +
        recent -
        opp_pitch * 1.25,
        2
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
