import pandas as pd
import sqlite3

df = pd.read_csv("game_data.csv")

conn = sqlite3.connect("game_data.db")

df.to_sql("game_sessions", conn, if_exists="replace", index=False)

print("Database created!")

conn.close()