import requests

session = requests.Session()
url = "https://tennis-academy-six.vercel.app/login"
response = session.post(url, data={"email": "test_b777689e@test.com", "password": "password123"})
print("Login status:", response.status_code)
if response.status_code == 200 and "Internal Server Error" in response.text:
    print("Found 500 in login response text")

if response.status_code == 500:
    print(response.text)

dashboard_url = "https://tennis-academy-six.vercel.app/dashboard"
dash_response = session.get(dashboard_url)
print("Dashboard status:", dash_response.status_code)
if dash_response.status_code == 500:
    print(dash_response.text)

