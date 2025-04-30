import pulp

def optimize_lineup(df):
    prob = pulp.LpProblem("DFS Lineup", pulp.LpMaximize)
    player_vars = {i: pulp.LpVariable(f"x_{i}", cat='Binary') for i in df.index}

    # Maximize total projected points
    prob += pulp.lpSum([player_vars[i] * df.loc[i, 'Projected'] for i in df.index]), "TotalProjectedPoints"

    # Salary cap
    prob += pulp.lpSum([player_vars[i] * df.loc[i, 'Salary'] for i in df.index]) <= 35000, "SalaryCap"

    def slot_constraint(label, count):
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'Roster Position'] == label]) == count

    slot_constraint('P', 1)
    slot_constraint('C/1B', 1)
    slot_constraint('2B', 1)
    slot_constraint('3B', 1)
    slot_constraint('SS', 1)
    slot_constraint('OF', 3)
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'Roster Position'] != 'P']) >= 1, "UTIL_count"

    # Max 4 players per team
    for team in df['Team'].unique():
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'Team'] == team]) <= 4

    # At least 3 teams
    team_vars = {team: pulp.LpVariable(f"team_used_{team}", cat='Binary') for team in df['Team'].unique()}
    for team in df['Team'].unique():
        prob += team_vars[team] <= pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'Team'] == team])
    prob += pulp.lpSum([team_vars[team] for team in df['Team'].unique()]) >= 3

    # Solve
    prob.solve()
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None

    selected = [i for i in df.index if player_vars[i].varValue == 1.0]
    result = df.loc[selected].copy()
    result['Total Salary'] = result['Salary'].sum()
    result['Total Projected'] = result['Projected'].sum()
    return result
