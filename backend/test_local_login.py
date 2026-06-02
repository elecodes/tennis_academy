from app import app

app.testing = True
client = app.test_client()

response = client.post(
    "/login", data={"email": "test_b777689e@test.com", "password": "password123"}
)
print("Local status:", response.status_code)
if response.status_code == 500:
    print(response.data.decode())
