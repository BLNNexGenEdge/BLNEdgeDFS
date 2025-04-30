import pulp

def optimize_lineup(df):
    print("🔍 Player pool size:", len(df))
    print("📊 Sample projections:")
    print(df[['Player', 'Roster Position', 'Team', 'Salary', 'Projected']].sort_values(by='Projected', ascending=False).head(10))

    prob = pulp.LpProblem("DFS_Lineup", pulp.LpMaximize)

    player_vars = {
        i: pulp.LpVariable(f"x_{i}", cat='Binary')
        for i in df.index
    }

    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Projected']
        for i in df.index
    ]), "TotalProjectedPoints"

    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Salary']
        for i in df.index
    ]) <= 35000, "SalaryCap"

    # Positional constraints
    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == 'P'
    ]) == 1, "Pitcher"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == 'C/1B'
    ]) == 1, "C1B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == '2B'
    ]) == 1, "2B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == '3B'
    ]) == 1, "3B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == 'SS'
    ]) == 1, "SS"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] == 'OF'
    ]) == 3, "OF"

    # UTIL: any non-pitcher, allow >= 2 to ensure lineup can complete
    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index if df.loc[i, 'Roster Position'] != 'P'
    ]) >= 2, "UTIL_Loosened"

    # Max 4 players per team
    for team in df['Team'].unique():
        prob += pulp.lpSum([
            player_vars[i]
            for i in df.index if df.loc[i, 'Team'] == team
        ]) <= 4, f"Max4_{team}"

    # At least 3 different teams
    team_vars = {
        team: pulp.LpVariable(f"team_used_{team}", cat='Binary')
        for team in df['Team'].unique()
    }

    for team in df['Team'].unique():
        prob += team_vars[team] <= pulp.lpSum([
            player_vars[i]
            for i in df.index if df.loc[i, 'Team'] == team
        ]), f"TeamUsed_{team}"

    prob += pulp.lpSum([
        team_vars[team] for team in team_vars
    ]) >= 3, "Min3Teams"

    # Solve
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        print("❌ Solver Status:", pulp.LpStatus[prob.status])
        return None

    selected = [i for i in df.index if player_vars[i].varValue == 1.0]
    result = df.loc[selected].copy()
    result['Total Salary'] = result['Salary'].sum()
    result['Total Projected'] = result['Projected'].sum()
    return result
