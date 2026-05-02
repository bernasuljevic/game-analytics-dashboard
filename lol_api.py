import requests

API_KEY = "BURAYA_API_KEY_YAPIŞTIR"

def get_lol_data(player_name="faker"):
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{player_name}"
    
    headers = {
        "X-Riot-Token": API_KEY
    }

    response = requests.get(url, headers=headers)
    return response.json()