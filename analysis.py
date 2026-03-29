import sqlite3
import pandas as pd

conn = sqlite3.connect("game_data.db")

# 1. Toplam oyuncu
query1 = "SELECT COUNT(DISTINCT user_id) as total_users FROM game_sessions"
df1 = pd.read_sql(query1, conn)
print(df1)

# 2. Ortalama level
query2 = "SELECT AVG(level) as avg_level FROM game_sessions"
df2 = pd.read_sql(query2, conn)
print(df2)

# 3. En çok oynanan level
query3 = """
SELECT level, COUNT(*) as count
FROM game_sessions
GROUP BY level
ORDER BY count DESC
LIMIT 5
"""
df3 = pd.read_sql(query3, conn)
print(df3)

# 4. Günlük aktif kullanıcı
query4 = """
SELECT DATE(date) as day, COUNT(DISTINCT user_id) as active_users
FROM game_sessions
GROUP BY day
ORDER BY day
"""
df4 = pd.read_sql(query4, conn)
print(df4)

conn.close()