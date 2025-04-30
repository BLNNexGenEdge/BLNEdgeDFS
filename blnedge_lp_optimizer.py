import pulp

def optimize_lineup(df):
    # Define the optimization problem
    prob = pulp.LpProblem("DFS_Lineup", pulp.LpMaximize)

    # Create a binary variable for each player
    player_vars = {
        i: pulp.LpVariable(f"x_{i}", cat='Binary')
        for i in df.index
    }

    # Objective: Maximize total projected points
    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Projected']
        for i in df.index
    ]), "TotalProjectedPoints"

    # Constraint: Salary cap
    prob += pulp.lpSum([
        player_vars[i] * df.loc[i, 'Salary']
        for i in df.index
    ]) <= 35000, "SalaryCap"

    # Positional constraints
    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == 'P'
    ]) == 1, "Pitcher"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == 'C/1B'
    ]) == 1, "C1B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == '2B'
    ]) == 1, "2B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == '3B'
    ]) == 1, "3B"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == 'SS'
    ]) == 1, "SS"

    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] == 'OF'
    ]) == 3, "OF"

    # UTIL: at least 1 extra hitter
    prob += pulp.lpSum([
        player_vars[i]
        for i in df.index
        if df.loc[i, 'Roster Position'] != 'P'
    ]) >= 1, "UTIL_Min"

    # Max 4 players per team
    for team in df['Team'].unique():
        prob += pulp.lpSum([
            player_vars[i]
            for i in df.index
            if df.loc[i, 'Team'] == team
        ]) <= 4, f"Max4_{team}"

    # At least 3 unique teams
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

    # Solve the problem
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        return None

    # Return the selected lineup
    selected = [i for i in df.index if player_vars[i].varValue == 1.0]
    result = df.loc[selected].copy()
    result['Total Salary'] = result['Salary'].sum()
    result['Total Projected'] = result['Projected'].sum()
    return result
