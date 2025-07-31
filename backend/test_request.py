import requests
import json

register_url = 'http://localhost:5000/register'
register_data = {
    'username': 'test_user',
    'password': 'test_password'
}

session = requests.Session()

try:
   
    response = session.post(register_url, json=register_data)
    print("Registration response:", response.json())

    
    login_url = 'http://localhost:5000/login'
    login_data = {
        'username': 'test_user',
        'password': 'test_password'
    }
    response = session.post(login_url, json=login_data)
    print("Login response:", response.json())

   
    predict_url = 'http://localhost:5000/predict'
    predict_data = {
        'text': 'Breaking news: The president was replaced by a robot.'
    }
    
    response = session.post(predict_url, json=predict_data)
    print("Prediction response:", response.json())

except requests.exceptions.RequestException as e:
    print("Error:", e)