def custom_pitcher_projection(row):
    try:
        k9 = float(row.get('K/9', 8.0))                   # Strikeouts per 9 innings
        opp_k_pct = float(row.get('Opponent K%', 0.22))  # Opponent K rate
        era = float(row.get('ERA', 4.00))                # ERA
        wrc_plus = float(row.get('Opponent wRC+', 100))  # Opponent offense quality
        ballpark = float(row.get('Ballpark Factor', 0))  # Park effect
        recent = float(row.get('Recent Form', 0.5))       # Hot/cold form

        strikeout_score = k9 * opp_k_pct * 10             # High K = big upside
        run_suppression = max(0, 35 - era * 5)            # Lower ERA = better
        difficulty_penalty = (wrc_plus - 100) * 0.05      # Penalize strong offenses

        projection = (
            strikeout_score +
            run_suppression -
            difficulty_penalty +
            ballpark +
            recent
        )

        return round(projection, 2)
    except Exception as e:
        print(f"⚠️ Error projecting pitcher {row.get('Player')}: {e}")
        return 0.0


def custom_hitter_projection(row):
    try:
        avg = float(row.get('AVG', 0.265))                    # Batting average
        iso = float(row.get('ISO', 0.160))                    # Power
        wrc_plus = float(row.get('wRC+', 100))                # Hitter quality
        lineup_pos = int(row.get('Lineup Pos', 5))            # Batting order
        ballpark = float(row.get('Ballpark Factor', 0))       # Park factor
        recent = float(row.get('Recent Form', 0.5))           # Momentum
        opp_pitch = float(row.get('Opp Pitcher Grade', 3))    # Pitcher difficulty

        lineup_bonus = {1: 1.5, 2: 1.3, 3: 1.8, 4: 1.7, 5: 1.4}.get(lineup_pos, 1.0)

        projection = (
            avg * 50 +        # ~12.5 for .250 hitter
            iso * 30 +        # ~6 for .200 ISO
            wrc_plus * 0.05 + # +5 for a 200 wRC+ guy
            lineup_bonus +    # Leadoff/top 4 = extra plate appearances
            ballpark +
            recent -
            opp_pitch * 1.25
        )

        return round(projection, 2)
    except Exception as e:
        print(f"⚠️ Error projecting hitter {row.get('Player')}: {e}")
        return 0.0


def apply_projections(df):
    projections = []
    for _, row in df.iterrows():
        if 'P' in str(row['Roster Position']):
            proj = custom_pitcher_projection(row)
        else:
            proj = custom_hitter_projection(row)
        projections.append(proj)
    df['Projected'] = projections
    return df
