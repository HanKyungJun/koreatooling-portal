import threading, webbrowser, time
from app import app

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

threading.Thread(target=open_browser, daemon=True).start()
app.run(host='127.0.0.1', port=5000, debug=False)
