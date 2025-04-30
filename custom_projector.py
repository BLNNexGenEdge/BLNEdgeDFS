def custom_pitcher_projection(row):
    try:
        k9 = float(row.get('K/9', 8.0))                   # Strikeouts per 9 innings
        opp_k_pct = float(row.get('Opponent K%', 0.22))  # How much opponent strikes out
        era = float(row.get('ERA', 4.00))                # Earned Run Average
        wrc_plus = float(row.get('Opponent wRC+', 100))  # Offensive quality of opponent
        ballpark = float(row.get('Ballpark Factor', 0))  # Park bonus/penalty
        recent = float(row.get('Recent Form', 0.5))       # Momentum

        # Scaling values to match reality:
        strikeout_score = k9 * opp_k_pct * 10             # Strikeout weighting (up to 25)
        run_suppression = max(0, 35 - era * 5)            # Better ERA = higher score (10–30)
        difficulty_penalty = (wrc_plus - 100) * 0.05      # Penalize facing strong offenses

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
