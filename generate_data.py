import pandas as pd
import random
from datetime import datetime, timedelta

num_users = 500
data = []

agents = ["Jett", "Sova", "Reyna", "Phoenix", "Sage"]

for user_id in range(1, num_users + 1):
    sessions = random.randint(5, 30)

    for _ in range(sessions):
        level = random.randint(1, 50)
        session_time = random.randint(5, 120)
        date = datetime.now() - timedelta(days=random.randint(0, 30))

        kills = random.randint(0, 30)
        deaths = random.randint(0, 30)
        agent = random.choice(agents)

        data.append({
            "user_id": user_id,
            "level": level,
            "session_time": session_time,
            "date": date,
            "kills": kills,
            "deaths": deaths,
            "agent": agent
        })

df = pd.DataFrame(data)
df.to_csv("game_data.csv", index=False)

print("Data created!")