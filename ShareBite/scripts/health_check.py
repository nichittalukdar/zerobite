import json
from urllib.request import urlopen

URL = "http://127.0.0.1:8000/health/ready"
try:
    with urlopen(URL, timeout=5) as response:
        print(json.dumps(json.loads(response.read().decode("utf-8")), indent=2))
except Exception as exc:
    raise SystemExit(f"ShareBite health check failed: {exc}") from exc
