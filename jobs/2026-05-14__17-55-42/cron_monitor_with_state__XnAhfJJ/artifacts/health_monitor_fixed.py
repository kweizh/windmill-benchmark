import urllib.request
from wmill import get_state, set_state

def check_endpoint(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return 'healthy' if response.status == 200 else 'degraded'
    except Exception:
        return 'down'

def send_alert(service: str, status: str):
    print(f"ALERT: {service} is {status}")

def main(service_url: str = "https://httpbin.org/status/200", service_name: str = "MyService"):
    last_status = get_state() or 'unknown'
    current_status = check_endpoint(service_url)
    
    if current_status != last_status:
        send_alert(service_name, current_status)
    
    set_state(current_status)
    
    return {'status': current_status, 'changed': current_status != last_status, 'alerted': current_status != last_status}
