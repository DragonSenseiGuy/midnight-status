from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

SERVICES = [
    {
        "name": "Midnight Website",
        "url": "https://midnight.hackclub.com",
        "method": "GET",
        "interval": 60
    },
    {
        "name": "Hack Club",
        "url": "https://hackclub.com",
        "method": "GET",
        "interval": 60
    },
    {
        "name": "Midnight Login API",
        "url": "https://midnight.hackclub.com/api/user/auth/login",
        "method": "POST",
        "json": {"email": "example@example.com", "referralCode": ""},
        "interval": 300
    }
]

def check_service(service):
    """
    Checks if a service is up by making a request according to its config.
    Returns True if status code is 200, False otherwise.
    """
    url = service["url"]
    method = service.get("method", "GET")
    json_data = service.get("json")
    
    try:
        if method == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        else:
            response = requests.get(url, timeout=5)

        if response.status_code == 429:
            app.logger.warning(f"429 Rate Limit Hit: {service['name']}")

        return response.ok or response.status_code == 429
    except requests.RequestException:
        return False

@app.route("/")
def status():
    services_data = []
    now = datetime.now()
    
    for service in SERVICES:
        last_checked = service.get("last_checked")
        interval = service.get("interval", 60)
        
        if last_checked is None or (now - last_checked).total_seconds() > interval:
            is_up = check_service(service)
            service["last_status"] = is_up
            service["last_checked"] = now
        
        services_data.append({
            "name": service["name"],
            "url": service["url"],
            "status": service["last_status"]
        })

    return render_template(
        "index.html",
        services=services_data,
        current_time=now.strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    app.run(debug=True)