from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import ssl
import certifi
import httpx
import os

load_dotenv()

def main():
    # Option 1: Use Zscaler certificate (recommended)
    # Certificate is in the same folder as main.py
    zscaler_cert_path = "zscaler-cert.pem"
    
    if os.path.exists(zscaler_cert_path):
        http_client = httpx.Client(verify=zscaler_cert_path)
        print("Using Zscaler certificate for SSL verification")
    else:
        # Option 2: Disable SSL verification (less secure but works)
        http_client = httpx.Client(verify=False)
        print("SSL verification disabled - Certificate not found, using for corporate environment")
    
    model = ChatOpenAI(
        model="gpt-4o", 
        temperature=0,
        http_client=http_client
    )
    
    tools = []
    agent_execution = create_react_agent(
        model=model,
        tools=tools)
    
    print("Welcome! I'm your AI assistant. Type 'quit' to exit.")
    print("You can ask me anything, and I'll do my best to assist you.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        print("\nAssistant: ", end="")
        try:
            for chunk in agent_execution.stream(
                    {"messages":  [HumanMessage(content=user_input)]}):
                if "agent" in chunk and  "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        print(message.content, end="")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print("Please check your API key and network connection.")

if __name__ == "__main__":
    main()