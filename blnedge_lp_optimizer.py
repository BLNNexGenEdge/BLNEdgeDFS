import pulp

def optimize_lineup(df):
    print("🔍 Player pool size:", len(df))
    print("📊 Top Projections:")
    print(df[['Player', 'Roster Position', 'Projected']].sort_values(by='Projected', ascending=False).head(10))

    prob = pulp.LpProblem("DFS_Lineup", pulp.LpMaximize)

    player_vars = {
        i: pulp.LpVariable(f"x_{i}", cat='Binary')
        for i in df.index
    }

    # Objective: Maximize total projected points
    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Projected']
        for i in df.index
    ]), "TotalProjectedPoints"

    # Salary constraint
    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Salary']
        for i in df.index
    ]) <= 35000, "SalaryCap"

    # Positional constraints using multi-slot matching
    def slot_constraint(pos_label, count):
        prob += pulp.lpSum([
            player_vars[i]
            for i in df.index
            if pos_label in str(df.loc[i, 'Roster Position'])
        ]) == count, f"{pos_label}_Slot"

    slot_constraint('P', 1)
    slot_constraint('C/1B', 1)
    slot_constraint('2B', 1)
    slot_constraint('3B', 1)
    slot_constraint('SS', 1)
    slot_constraint('OF', 3)

    # UTIL: any non-pitcher — at least 1 additional hitter
    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if 'P' not in str(df.loc[i, 'Roster Position'])
    ]) >= 2, "UTIL_Loosened"

    # Max 4 players per team
    for team in df['Team'].unique():
        prob += pulp.lpSum([
            player_vars[i]
            for i in df.index
            if df.loc[i, 'Team'] == team
        ]) <= 4, f"Max4_{team}"

    # At least 3 teams represented
    team_vars = {
        team: pulp.LpVariable(f"team_used_{team}", cat='Binary')
        for team in df['Team'].unique()
    }

    for team in df['Team'].unique():
        prob += team_vars[team] <= pulp.lpSum([
            player_vars[i]
            for i in df.index
            if df.loc[i, 'Team'] == team
        ]), f"TeamUsed_{team}"

    prob += pulp.lpSum([
        team_vars[team] for team in team_vars
    ]) >= 3, "Min3Teams"

    # Solve it
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        print("❌ LP Status:", pulp.LpStatus[prob.status])
        return None

    selected = [i for i in df.index if player_vars[i].varValue == 1.0]
    result = df.loc[selected].copy()
    result['Total Salary'] = result['Salary'].sum()
    result['Total Projected'] = result['Projected'].sum()
    return result
