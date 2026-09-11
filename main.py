import requests;
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException;
from groq import Groq;

import os;
from dotenv import load_dotenv;
from openai import OpenAI;

from fastapi import FastAPI;

app = FastAPI();

@app.get("/");
def home():
    return {"status": "live"};

messageHistory : list = [];
load_dotenv();

def getWeather(c : str) -> tuple:
    tries : int = 0;
    weather : tuple = (0,""); #tuple[0] = error status, 1 = success, 0 = error; tuple[1] = weather report or error description based on tuple[0]
    while (tries < 3):
        try:
            cityName : str = c;
            baseURL : str = "http://api.openweathermap.org/data/2.5/weather?";
            appID : str = "f6495aa2227a8e4ed0be0af8c6bf93c5";
            
            finalURL : str = f"{baseURL}appid={appID}&q={cityName}";
            
            response : str = requests.get(finalURL, timeout=8);
            response.raise_for_status();
            weather = (1, response.json());
        
        except HTTPError as httpErr:
            weather = (0, f"Sorry. An HTTP error occurred: {httpErr}.");
        except Timeout as timeoutErr:
            weather = (0, "Sorry. The request timed out: {timeoutErr}.");
        except ConnectionError as connErr:
            weather = (0, f"Sorry. A connection error occured: {connErr}.");
        except RequestException as reqExcpt:
            weather = (0, "Sorry. A request exception occured: {reqExcpt}.");

        if (weather[0] == 0):
            tries = tries + 1;
        else:
            tries = 3;
    return weather;

def generateResponse(w : tuple) -> str: #w[0] = 0 means caught error, 1 = successful weather report, 3 = continued chat input
    messageList : list = [];
    if (w[0] == 1):
        messageList = [{
            "role": "user",
            "content": f"Generate an accurate weather analysis and report based on this json data : {w[1]}\n\nUse language that is easily understandable so that the response is accessible to a common person. Try to be accurate and to include simple, readable paragraphical descriptions or explanations along with tables and analysis."
          }];
    else:
        messageHistory.append({"role": "user", "content": w[1]});
        messageList = messageHistory;
    
    client = Groq(api_key=os.getenv("groqApiKey")); #gets groq api key from .env file
    completion = client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        messages = messageList,
        temperature = 0.6,
        max_completion_tokens = 2048,
        top_p = 1,
        reasoning_effort = "medium",
        stream = False,
        stop = None
    );

    response : str = (completion.choices[0].message.content or "");
    messageHistory.append({"role": "assistant", "content": response});
    print(response);


def generateWeatherReport(w : tuple) -> str:
    if (w[0] == 0):
        return w[1];
    else:
        generateResponse(w);

#generateWeatherReport(getWeather("Delhi"));
#generateWeatherReport((3, "Hi. How are you?"));
generateWeatherReport(getWeather("Kerala"));
generateWeatherReport((3,"What does this weather mean for me?"));
print("\n");
#print(messageHistory);
