import streamlit as st
import pandas as pd
from custom_projector import apply_projections
from blnedge_lp_optimizer import optimize_lineup
from blnedge_props import generate_prop_edges

st.set_page_config(page_title="BLNEdgeDFS", layout="wide")
st.title("⚾ BLNEdgeDFS: Fantasy Lineup & Prop Analyzer")

opt_tab, prop_tab = st.tabs(["🧠 DFS Optimizer", "🎯 Prop Picks"])

with opt_tab:
    st.header("DFS Lineup Optimizer")
    salary_file = st.file_uploader("Upload FanDuel Salary CSV", type="csv")
    use_custom_proj = st.checkbox("Use BLN Custom Projections", value=True)

    if salary_file:
        df = pd.read_csv(salary_file)
        df['Player'] = df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')
        df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
        df = df[df['Injury Indicator'].isna()]
        df = df[(df['Roster Position'] != 'P') | (df['Probable Pitcher'] == 'Yes')]

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

        if use_custom_proj:
            df = apply_projections(df)
        else:
            df['Projected'] = df['FPPG']

        st.write("📋 Filtered Player Pool:")
        st.dataframe(df[['Player', 'Roster Position', 'Salary', 'Team', 'Projected']])

        st.success("Projection data applied. Running optimizer...")
        result = optimize_lineup(df)

        if result is not None:
            st.dataframe(result)
            csv = result.to_csv(index=False).encode('utf-8')
            st.download_button("Download Optimized Lineup CSV", csv, "Optimized_Lineup.csv")
        else:
            st.error("No valid lineup found. Adjust constraints or player pool.")

with prop_tab:
    st.header("Prop Pick Evaluator")
    prop_file = st.file_uploader("Upload Player Props CSV", type="csv", key="props")
    salary_file_2 = st.file_uploader("Re-upload Salary CSV (for projections)", type="csv", key="salary2")

    if prop_file and salary_file_2:
        props = pd.read_csv(prop_file)
        sal = pd.read_csv(salary_file_2)
        sal['Player'] = sal['First Name'].fillna('') + ' ' + sal['Last Name'].fillna('')
        sal['Salary'] = pd.to_numeric(sal['Salary'], errors='coerce')
        sal = sal[sal['Injury Indicator'].isna()]
        sal = sal[(sal['Roster Position'] != 'P') | (sal['Probable Pitcher'] == 'Yes')]

        sal['K/9'] = 9.5
        sal['Opponent K%'] = 0.23
        sal['ERA'] = 3.80
        sal['Opponent wRC+'] = 100
        sal['Ballpark Factor'] = 0
        sal['Recent Form'] = 0.5
        sal['AVG'] = 0.265
        sal['ISO'] = 0.180
        sal['wRC+'] = 110
        sal['Lineup Pos'] = 3
        sal['Opp Pitcher Grade'] = 3

        sal = apply_projections(sal)
        merged = generate_prop_edges(props, sal)

        st.dataframe(merged)
        csv2 = merged.to_csv(index=False).encode('utf-8')
        st.download_button("Download Prop Picks CSV", csv2, "Top_Prop_Picks.csv")
