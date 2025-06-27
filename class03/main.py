from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool
from dotenv import load_dotenv
import os
import requests

# Load .env file
load_dotenv()

# Weather fetch karne ka tool
@function_tool
def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "❌ API key missing. Please check your .env file."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    print(f"URL: {url}")  # Debug ke liye

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and "main" in data and "weather" in data:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"The current weather in {city} is {desc} with temperature {temp}°C."
    else:
        return f"❌ Could not fetch weather data. Response: {data.get('message', 'Unknown error')}"

# Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")

# Agent setup
agent = Agent(
    name="Current Data",
    instructions=(
        "You are a helpful assistant. Always use tools to answer the user's questions. "
        "Do not try to answer using your own knowledge. If the tool is not available, say so."
    ),
    tools=[get_weather]
)

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# ✅ Get user input from terminal
city = input("Enter the city name to check weather: ")
query = f"What is the weather condition of {city}?"

# Run the agent
result = Runner.run_sync(agent, query, run_config=config)

# Print output
print(result.final_output)