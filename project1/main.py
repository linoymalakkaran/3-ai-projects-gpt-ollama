from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

@tool
def calculator(a: float, b: float) -> str:
    """Useful for performing basic arithmeric calculations with numbers"""
    print("Tool has been called.")
    return f"The sum of {a} and {b} is {a + b}"
    
@tool
def say_hello(name: str) -> str:
    """Useful for greeting a user"""
    print("Tool has been called.")
    return f"Hello {name}, I hope you are well today"

def main():
    # Use Ollama Chat Model for LangGraph compatibility
    model = ChatOllama(
        model="llama3.2:1b",
        base_url="http://localhost:11434",
        temperature=0
    )
    
    tools = [calculator, say_hello]
    agent_execution = create_react_agent(
        model=model,
        tools=tools
    )
    
    print("Welcome! I'm your AI assistant running locally with Ollama.")
    print("Type 'quit' to exit. You can ask me anything!")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        print("\nAssistant: ", end="")
        try:
            for chunk in agent_execution.stream(
                    {"messages": [HumanMessage(content=user_input)]}):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        print(message.content, end="")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print("Please check if Ollama is running and model is available.")

if __name__ == "__main__":
    main()