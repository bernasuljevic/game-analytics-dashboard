import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Game Analytics", page_icon="🎮", layout="wide")

# 🎨 STYLE
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 🎯 TITLE
st.markdown("<h1 style='text-align:center;'>🎮 Game Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>Multi-Game Comparison System</h4>", unsafe_allow_html=True)

# 🔗 DATA
@st.cache_data
def load_valorant():
    conn = sqlite3.connect("valorant.sqlite")
    df = pd.read_sql("SELECT * FROM Game_Scoreboard LIMIT 5000", conn)
    conn.close()
    df["game"] = "Valorant"
    return df

@st.cache_data
def load_lol():
    try:
        df = pd.read_csv("lol_data.csv")
        df["game"] = "LoL"
        return df
    except:
        return pd.DataFrame()

val_df = load_valorant()
lol_df = load_lol()

# 🧠 CLEAN FUNCTION
def clean(df):
    df.columns = df.columns.str.lower()
    kill = [c for c in df.columns if "kill" in c]
    death = [c for c in df.columns if "death" in c]
    agent = [c for c in df.columns if "agent" in c or "champion" in c]
    player = [c for c in df.columns if "player" in c or "name" in c]

    df["kills"] = df[kill[0]] if kill else 0
    df["deaths"] = df[death[0]] if death else 1
    df["agent"] = df[agent[0]] if agent else "Unknown"
    df["user_id"] = df[player[0]] if player else "Player"

    df["kills"] = pd.to_numeric(df["kills"], errors="coerce")
    df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")

    df["kda"] = df["kills"] / (df["deaths"] + 1)

    return df.dropna(subset=["kills", "deaths"])

val_df = clean(val_df)
lol_df = clean(lol_df)

df = pd.concat([val_df, lol_df])

# 🎮 FILTER
selected_games = st.multiselect(
    "🎮 Select Games",
    df["game"].unique(),
    default=df["game"].unique()
)

df = df[df["game"].isin(selected_games)]

# 📊 HEADER
st.markdown("## 🔥 Game Comparison Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Valorant Players", val_df["user_id"].nunique())
col2.metric("LoL Players", lol_df["user_id"].nunique())
col3.metric("Total Players", df["user_id"].nunique())

st.divider()

# 🎨 COLORS
colors = {
    "LoL": "#3498db",
    "Valorant": "#e74c3c"
}

# 📊 KDA
kda_data = df.groupby("game")["kda"].mean().reset_index()

fig1 = px.bar(
    kda_data,
    x="game",
    y="kda",
    color="game",
    text_auto=True,
    color_discrete_map=colors,
    title="Average KDA Comparison"
)

fig1.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>KDA: %{y:.2f}<extra></extra>"
)

fig1.update_layout(template="plotly_dark", title_x=0.5)

# 📊 KILLS
kill_data = df.groupby("game")["kills"].mean().reset_index()

fig2 = px.bar(
    kill_data,
    x="game",
    y="kills",
    color="game",
    text_auto=True,
    color_discrete_map=colors,
    title="Average Kills Comparison"
)

fig2.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Kills: %{y:.1f}<extra></extra>"
)

fig2.update_layout(template="plotly_dark", title_x=0.5)

# 📊 PIE
count_data = df["game"].value_counts().reset_index()
count_data.columns = ["game","count"]

fig3 = px.pie(
    count_data,
    names="game",
    values="count",
    color="game",
    color_discrete_map=colors,
    title="Player Distribution"
)

fig3.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Players: %{value}<extra></extra>"
)

fig3.update_layout(template="plotly_dark")

# 🎯 GRID
c1, c2, c3 = st.columns(3)

with c1:
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# 🎮 DETAIL
game = st.selectbox("🎯 Select Detailed Game", selected_games)

filtered_df = df[df["game"] == game]

st.markdown(f"## 🔍 {game} Detailed Analysis")

fig4 = px.bar(
    filtered_df.groupby("agent")["kills"].mean().reset_index(),
    x="agent",
    y="kills",
    color="agent",
    title=f"{game} Agent Performance"
)

fig4.update_layout(template="plotly_dark", title_x=0.5)

st.plotly_chart(fig4, use_container_width=True)