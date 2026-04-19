from app import app
from database import get_db

app.testing = True
app.debug = False # Simulate production
client = app.test_client()

response = client.post("/login", data={"email": "test_b777689e@test.com", "password": "password123"})
print("Local status:", response.status_code)

dashboard_resp = client.get("/dashboard")
print("Dashboard status:", dashboard_resp.status_code)

if dashboard_resp.status_code == 500:
    print(dashboard_resp.data.decode())
