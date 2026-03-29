import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Game Analytics", page_icon="🎮", layout="wide")

# 🎨 BACKGROUND
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 🎯 TITLE
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(to right, #ff416c, #ff4b2b);
-webkit-background-clip: text;
color: transparent;'>
🎮 Valorant Analytics Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:gray;'>Real game data analytics</p>", unsafe_allow_html=True)

# 🔗 DATA
@st.cache_data
def load_data():
    conn = sqlite3.connect("valorant.sqlite")
    df = pd.read_sql("SELECT * FROM Game_Scoreboard LIMIT 5000", conn)
    conn.close()
    return df

df = load_data()

# 🔥 KOLON BULMA (garantili)
kill_cols = [col for col in df.columns if "kill" in col.lower()]
death_cols = [col for col in df.columns if "death" in col.lower()]
agent_cols = [col for col in df.columns if "agent" in col.lower() or "character" in col.lower()]
player_cols = [col for col in df.columns if "player" in col.lower() or "name" in col.lower()]
level_cols = [col for col in df.columns if "level" in col.lower()]

# kolonları ata
df["kills"] = df[kill_cols[0]] if kill_cols else 0
df["deaths"] = df[death_cols[0]] if death_cols else 1
df["agent"] = df[agent_cols[0]] if agent_cols else "Unknown"
df["user_id"] = df[player_cols[0]] if player_cols else "Player"

if level_cols:
    df["level"] = df[level_cols[0]]
else:
    df["level"] = 1

# 🧼 temizleme
df["kills"] = pd.to_numeric(df["kills"], errors="coerce")
df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")
df["level"] = pd.to_numeric(df["level"], errors="coerce")

df = df.dropna(subset=["kills", "deaths", "agent"])

# 🎮 SIDEBAR
with st.sidebar:
    st.markdown("## 🎮 Control Panel")

    selected_agent = st.multiselect(
        "Agent",
        df["agent"].unique(),
        default=df["agent"].unique()
    )

    min_level = int(df["level"].min())
    max_level = int(df["level"].max())

    if min_level == max_level:
        level_range = (min_level, max_level)
        st.info("Level filter disabled")
    else:
        level_range = st.slider(
            "Level",
            min_level,
            max_level,
            (min_level, max_level)
        )

# 🎯 FILTER
filtered_df = df[
    (df["agent"].isin(selected_agent)) &
    (df["level"].between(level_range[0], level_range[1]))
].copy()

if filtered_df.empty:
    st.warning("No data")
    st.stop()

# 🔥 FEATURES
filtered_df["kda"] = filtered_df["kills"] / (filtered_df["deaths"] + 1)

# 📊 OVERVIEW
st.markdown("## 📊 Overview")

def card(title, value, icon):
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.05);
    padding:20px;border-radius:15px;text-align:center;'>
    <h4>{icon} {title}</h4>
    <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    card("Players", filtered_df["user_id"].nunique(), "👥")

with c2:
    card("Avg Kills", int(filtered_df["kills"].mean()), "🔫")

with c3:
    card("Avg KDA", round(filtered_df["kda"].mean(), 2), "⚔️")

st.divider()

# 🎯 AGENT PERFORMANCE
agent_perf = filtered_df.groupby("agent")["kills"].mean().reset_index()

fig1 = px.bar(agent_perf, x="agent", y="kills", color="agent", title="Kills per Agent")
fig1.update_layout(template="plotly_dark", title_x=0.5)

st.plotly_chart(fig1, width="stretch")

st.divider()

# 🏆 RANK
filtered_df["rank"] = pd.cut(
    filtered_df["kda"],
    bins=[0,1,1.5,2,10],
    labels=["Gold","Diamond","Immortal","Radiant"]
)

rank_counts = filtered_df["rank"].value_counts().reset_index()
rank_counts.columns = ["rank","count"]

fig3 = px.bar(rank_counts, x="rank", y="count", color="rank", title="Rank Distribution")
fig3.update_layout(template="plotly_dark", title_x=0.5)

st.plotly_chart(fig3, width="stretch")

st.divider()

# 🆚 PLAYER COMPARISON
st.markdown("## 🆚 Player Comparison")

players = filtered_df["user_id"].unique()

p1, p2 = st.columns(2)

player1 = p1.selectbox("Player 1", players)
player2 = p2.selectbox("Player 2", players)

d1 = filtered_df[filtered_df["user_id"] == player1]
d2 = filtered_df[filtered_df["user_id"] == player2]

c1, c2 = st.columns(2)
c1.metric("Player 1 Kills", int(d1["kills"].mean()))
c2.metric("Player 2 Kills", int(d2["kills"].mean()))

c3, c4 = st.columns(2)
c3.metric("Player 1 KDA", round(d1["kda"].mean(),2))
c4.metric("Player 2 KDA", round(d2["kda"].mean(),2))