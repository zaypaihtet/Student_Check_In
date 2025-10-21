import requests

def get_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        return data.get("city", "Unknown") + ", " + data.get("country", "")
    except:
        return "Unknown"
