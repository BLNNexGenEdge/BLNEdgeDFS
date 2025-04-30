import streamlit as st
import pandas as pd
import numpy as np
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

        # FIXED: allow all hitters and only "Yes" pitchers
        df = df[
            (df['Roster Position'] != 'P') |
            ((df['Roster Position'] == 'P') & (df['Probable Pitcher'] == 'Yes'))
        ]

        # Inject varied testing stats
        df['K/9'] = np.random.uniform(7.0, 11.0, size=len(df))
        df['Opponent K%'] = np.random.uniform(0.20, 0.27, size=len(df))
        df['ERA'] = np.random.uniform(2.5, 5.0, size=len(df))
        df['Opponent wRC+'] = np.random.normal(100, 10, size=len(df))
        df['Ballpark Factor'] = np.random.uniform(-1.0, 1.0, size=len(df))
        df['Recent Form'] = np.random.uniform(-0.5, 1.0, size=len(df))
        df['AVG'] = np.random.uniform(0.220, 0.320, size=len(df))
        df['ISO'] = np.random.uniform(0.100, 0.250, size=len(df))
        df['wRC+'] = np.random.normal(100, 20, size=len(df))
        df['Lineup Pos'] = np.random.randint(1, 6, size=len(df))
        df['Opp Pitcher Grade'] = np.random.uniform(1, 5, size=len(df))

        if use_custom_proj:
            df = apply_projections(df)
        else:
            df['Projected'] = df['FPPG']

        df['Projected'] = df['Projected'].clip(lower=0, upper=50)

        st.write("🧪 Position breakdown:", df['Roster Position'].value_counts())
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
        sal = sal[
            (sal['Roster Position'] != 'P') |
            ((sal['Roster Position'] == 'P') & (sal['Probable Pitcher'] == 'Yes'))
        ]

        # Same varied stats for props
        sal['K/9'] = np.random.uniform(7.0, 11.0, size=len(sal))
        sal['Opponent K%'] = np.random.uniform(0.20, 0.27, size=len(sal))
        sal['ERA'] = np.random.uniform(2.5, 5.0, size=len(sal))
        sal['Opponent wRC+'] = np.random.normal(100, 10, size=len(sal))
        sal['Ballpark Factor'] = np.random.uniform(-1.0, 1.0, size=len(sal))
        sal['Recent Form'] = np.random.uniform(-0.5, 1.0, size=len(sal))
        sal['AVG'] = np.random.uniform(0.220, 0.320, size=len(sal))
        sal['ISO'] = np.random.uniform(0.100, 0.250, size=len(sal))
        sal['wRC+'] = np.random.normal(100, 20, size=len(sal))
        sal['Lineup Pos'] = np.random.randint(1, 6, size=len(sal))
        sal['Opp Pitcher Grade'] = np.random.uniform(1, 5, size=len(sal))

        sal = apply_projections(sal)
        sal['Projected'] = sal['Projected'].clip(lower=0, upper=50)
        merged = generate_prop_edges(props, sal)

        st.dataframe(merged)
        csv2 = merged.to_csv(index=False).encode('utf-8')
        st.download_button("Download Prop Picks CSV", csv2, "Top_Prop_Picks.csv")
