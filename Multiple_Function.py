import os
from dotenv import load_dotenv
import warnings
import requests
from langchain import hub  # Import the hub for prompts
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Ignore specific warnings for a cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# ------------------ Helper Functions for Key Management ------------------

def load_api_keys(prefix: str) -> list[str]:
    keys = []
    i = 1
    while True:
        key = os.getenv(f"{prefix}_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break
    return keys

def initialize_llm_with_fallback(google_keys: list[str]):
    if not google_keys: return None
    print("🔑 Validating Google API Keys...")
    for i, key in enumerate(google_keys):
        print(f"--- Attempting with Google Key #{i + 1}...")
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=key)
            llm.invoke("test")
            print(f"✅ Success! Google Key #{i + 1} is active.")
            return llm
        except Exception:
            print(f"❌ Failed. This key is likely invalid or disabled.")
    return None

# ------------------ Tool Functions ------------------

def get_name():
    return "My name is Gursharan Kaur."

def get_quote():
    return "Success is not final, failure is not fatal: It is the courage to continue that counts. — Winston Churchill"

def get_health_tips():
    return "Stay hydrated, exercise regularly, get 7-8 hours of sleep, and avoid junk food."

def get_weather(city: str, weather_keys: list[str]):
    # (Your get_weather function remains the same as before)
    if not weather_keys: return "❌ Error: No OpenWeatherMap API keys configured."
    for i, key in enumerate(weather_keys):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 401:
                print(f"--- OpenWeather Key #{i+1} is invalid. Trying next...")
                continue
            data = response.json()
            if response.status_code != 200 or "main" not in data:
                return f"❌ Error: {data.get('message', 'Failed to get weather for ' + city)}"
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            condition = data["weather"][0]["description"].capitalize()
            wind_speed = data["wind"]["speed"]
            return (f"🌤 Weather in {city}:\n"
                    f"🌡 Temperature: {temp}°C\n"
                    f"📋 Condition: {condition}\n"
                    f"💧 Humidity: {humidity}%\n"
                    f"🍃 Wind Speed: {wind_speed} m/s")
        except requests.exceptions.RequestException:
            print(f"--- Network error with OpenWeather Key #{i+1}. Trying next...")
            continue
    return f"❌ All OpenWeatherMap API keys failed for city: {city}"

# ------------------ Main Application Logic ------------------

if __name__ == "__main__":
    GOOGLE_API_KEYS = load_api_keys("GOOGLE_API_KEY")
    OPENWEATHER_API_KEYS = load_api_keys("OPENWEATHER_API_KEY")

    if not GOOGLE_API_KEYS:
        print("🚨 Critical Error: No Google API keys found in .env file. Exiting.")
        exit()

    llm = initialize_llm_with_fallback(GOOGLE_API_KEYS)
    if not llm:
        print("🚨 Critical Error: All Google API keys failed. Cannot start the agent. Exiting.")
        exit()

    tools = [
        # (Your tools list remains the same as before)
        Tool(name="NameTool", func=lambda _: get_name(), description="Tells the name of the user."),
        Tool(name="QuotesTool", func=lambda _: get_quote(), description="Provides inspirational quotes."),
        Tool(name="HealthTipsTool", func=lambda _: get_health_tips(), description="Gives useful health tips."),
        Tool(name="WeatherTool", func=lambda city: get_weather(city, OPENWEATHER_API_KEYS), description="Gives real-time weather. Input should be a city name like 'Delhi'."),
    ]
    
    # --- MODERN AGENT CREATION ---
    # 1. Pull the ReAct prompt template from the hub
    prompt = hub.pull("hwchase17/react")

    # 2. Create the agent using the new function
    agent = create_react_agent(llm, tools, prompt)

    # 3. Create the AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    # --- END OF MODERN AGENT CREATION ---

    print("\n🤖 Ask me:\n- 'What's your name?'\n- 'Give me a quote'\n- 'Weather Delhi'\n- 'Health tip'\nType 'exit' to quit.\n")

    while True:
        user_input = input("📝 You: ")
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        # Use the agent_executor.invoke method instead of agent.run
        result = agent_executor.invoke({"input": user_input})
        
        # The output is now in a dictionary under the 'output' key
        print("📩", result['output'])