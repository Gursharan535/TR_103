# advanced_search_tool.py 
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool

# --- CONFIGURATION ---
# Use the model name you have now confirmed is working for your account
MODEL_NAME = "gemini-2.5-flash"

# === Load and Validate API Keys ===
load_dotenv()
api_keys = []
for i in range(1, 7):
    key = os.getenv(f"GOOGLE_API_KEY_{i}")
    if key:
        api_keys.append(key)

if not api_keys:
    print("❌ Critical Error: No API keys found in the .env file.")
    exit()

print(f"🔑 Found {len(api_keys)} API keys. Now finding a working one...")

working_api_key = None
for i, key in enumerate(api_keys):
    print(f"\n--- Attempting with Key #{i + 1}...")
    try:
        genai.configure(api_key=key)
        # Validate using the CORRECT model name
        test_model = genai.GenerativeModel(MODEL_NAME)
        test_model.generate_content("test", generation_config={'max_output_tokens': 5})
        print(f"✅ Success! Key #{i + 1} is working.")
        working_api_key = key
        break
    except Exception as e:
        print(f"❌ Failed. This key is likely invalid or has been disabled.")

if not working_api_key:
    print("\n🚨 Critical Error: All API keys failed. Cannot proceed.")
    exit()

# === Initialize LLM with the working key ===
print("\n🤖 Initializing LangChain LLM with the validated API key...")
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME, # Use the correct model name here too
    google_api_key=working_api_key
)

# === Define Tools ===
search = DuckDuckGoSearchRun()

def calculator_tool_func(query: str) -> str:
    try:
        result = eval(query, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

calculator = Tool(
    name="Calculator",
    func=calculator_tool_func,
    description="Useful for solving basic math expressions."
)

tools = [search, calculator]

# === Create and Run the Agent ===
print("🛠️ Creating the agent...")
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

question = "What is the capital of India and what is 5 * (3 + 2)?"
print(f"\n❓ Question: {question}")

response = agent_executor.invoke({"input": question})

print("\n✅ Gemini Agent Final Response:\n", response['output'])