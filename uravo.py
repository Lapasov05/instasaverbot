import os

import requests
import json


def get_weather(latitude,longitude):
    API_KEY = "3346d0041a0aeb4ec8d0dcdc626d62f9"
    url=f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}"

    response = requests.get(url)
    print(response.json())
    return response.json()


# result = get_weather(41.314450, 69.268451)
# print(result)
# print("Namlik: ",result["main"]["humidity"])
# print("Harorat: ",result["main"]["temp"])


import requests

def post_data(latitude,longitude):
    weather_data = get_weather(latitude,longitude)
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    token = "pat-na1-023c63e0-60cf-4702-96e9-900204c90bc5"

    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "properties": {
            "firstname": f"{humidity}",
            "lastname": f"{temperature}",
            "email": "dummy_email@example.com"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code)
    print(response.json())
    return response.json()


post_data(41.323056, 69.302181)