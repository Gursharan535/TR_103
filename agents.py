import os
from dotenv import load_dotenv
import warnings

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain_community.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

# --- PHASE 1: CONFIGURATION AND SETUP ---

# Ignore deprecation warnings for a cleaner terminal output
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Define the model name as a constant for easy modification
MODEL_NAME = "models/gemini-2.5-flash"

# Load environment variables from the .env file
load_dotenv()

# --- PHASE 2: LOAD AND VALIDATE API KEYS ---

def initialize_llm_with_fallback(keys: list[str]):
    """
    Tries to initialize and validate the LangChain LLM with a list of keys,
    returning the first one that successfully makes an API call.
    """
    print("🔑 Validating Google API Keys using LangChain...")
    if not keys:
        return None

    for i, key in enumerate(keys):
        print(f"\n--- Attempting with Key #{i + 1}...")
        try:
            # Initialize the LangChain LLM object with the current key
            llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7, google_api_key=key)
            # Make a small, real call to fully validate the key and permissions
            llm.invoke("test")
            print(f"✅ Success! Key #{i + 1} is active and working with LangChain.")
            return llm
        except Exception as e:
            # If the key is leaked, invalid, or lacks permissions, this will fail
            print(f"❌ Failed. Reason: {e}")
    
    return None # Return None if all keys in the loop failed

# Load all GOOGLE_API_KEY_n from the .env file
api_keys = []
i = 1
while True:
    key = os.getenv(f"GOOGLE_API_KEY_{i}")
    if key:
        api_keys.append(key)
        i += 1
    else:
        break

if not api_keys:
    print("❌ Critical Error: No API keys found in the .env file.")
    exit()

# Initialize the LLM by trying the keys one by one
llm = initialize_llm_with_fallback(api_keys)

if not llm:
    print("\n🚨 Critical Error: All API keys failed validation. Cannot start the agent.")
    exit()

# --- PHASE 3: DEFINE TOOLS ---

print("\n🛠️ Setting up tools...")
# Wikipedia tool setup is already modern and correct
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# Combine tools into a list for the agent
tools = [wiki_tool]

# --- PHASE 4: CREATE AND RUN THE AGENT (MODERN SYNTAX) ---

print("🤖 Creating the agent...")

# Pull the standard ReAct prompt template from the LangChain Hub
prompt = hub.pull("hwchase17/react")

# Create the agent using the modern function
agent = create_react_agent(llm, tools, prompt)

# Create the AgentExecutor, which is the runtime for the agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Define the question for the agent
question = "What is the history of the Eiffel Tower?"
print(f"\n❓ Question: {question}")

# Invoke the agent using the modern method
response = agent_executor.invoke({"input": question})

# Print the final, clean output
print("\n" + "="*50)
print("📘 Gemini Agent Final Response:")
print(response['output'])
print("="*50)