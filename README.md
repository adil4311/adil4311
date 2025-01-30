from flask import Flask
import threading
import requests
import time

app = Flask(__name__)

# Aternos ka wake-up URL (Tumhare Aternos server ka address aur port)
ATERNOS_PING_URL = "https://Dream_World_12.aternos.me:12833/panel/ajax/start.php?server=YOUR_SERVER_ID"

def ping_aternos():
    while True:
        response = requests.get(ATERNOS_PING_URL)
        if response.status_code == 200:
            print("Aternos ping bheja! Server Active Rahega.")
        else:
            print(f"Ping failed with status code: {response.status_code}")
        time.sleep(600)  # Har 10 min me ping karega

@app.route("/")
def home():
    return "Aternos Ping Server Running!"

if __name__ == "__main__":
    # Flask server ko run karo
    app.run(host="0.0.0.0", port=8080)
