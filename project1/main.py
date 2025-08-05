from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import re

load_dotenv()

@tool
def calculator(expression: str) -> str:
    """Useful for performing basic arithmetic calculations. Pass mathematical expressions like '1+1', '2*3', '10-5', etc."""
    print(f"Calculator tool called with: {expression}")
    try:
        # Simple evaluation for basic arithmetic (be careful with eval in production)
        # This is a simplified version - consider using a proper math parser for production
        allowed_chars = set('0123456789+-*/.()')
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return f"Error: Invalid characters in expression '{expression}'"
        
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

@tool
def add_numbers(a: float, b: float) -> str:
    """Useful for adding two specific numbers together"""
    print(f"Add numbers tool called with: {a} + {b}")
    return f"The sum of {a} and {b} is {a + b}"
    
@tool
def say_hello(name: str) -> str:
    """Useful for greeting a user by name"""
    print(f"Hello tool called for: {name}")
    return f"Hello {name}, I hope you are well today!"

def main():
    # Use Ollama Chat Model with better parameters for tool use
    model = ChatOllama(
        model="llama3.2:3b",  # Try this larger model for better tool selection
        base_url="http://localhost:11434",
        temperature=0,
    )
    
    tools = [calculator, add_numbers, say_hello]
    
    agent_executor = create_react_agent(
        model=model,
        tools=tools,
        debug=False  # Turn off debug to remove all the verbose output
    )
    
    print("Welcome! I'm your AI assistant running locally with Ollama.")
    print("Type 'quit' to exit. You can ask me to:")
    print("- Calculate math expressions (e.g., '1+1', '2*3+4')")
    print("- Add two numbers (e.g., 'add 5 and 10')")
    print("- Say hello (e.g., 'say hello to John')")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        print("Assistant:", end=" ")
        try:
            # Add system message as part of the conversation
            system_prompt = """You are a helpful assistant with access to tools. 
            - Use the calculator tool for mathematical expressions like '1+1', '2*3+4'
            - Use the add_numbers tool when asked to add two specific numbers
            - Use the say_hello tool when asked to greet someone or say hello
            - Always provide the exact result from the tool, nothing more
            - Don't add extra phrases or ask follow-up questions"""
            
            # Create message list with system context
            from langchain_core.messages import SystemMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = agent_executor.invoke({"messages": messages})
            
            # Find the tool result in the messages
            tool_result = None
            for message in response["messages"]:
                if hasattr(message, 'name') and message.name in ['calculator', 'add_numbers', 'say_hello']:
                    tool_result = message.content
                    break
            
            # If we found a tool result, use it directly
            if tool_result:
                # Clean up the tool result
                if "The result of" in tool_result and "is" in tool_result:
                    # Extract just the number from calculator results
                    import re
                    number_match = re.search(r'is (\d+)', tool_result)
                    if number_match:
                        print(number_match.group(1))
                    else:
                        print(tool_result)
                elif "Hello" in tool_result:
                    # For greetings, use the tool result directly
                    print(tool_result)
                else:
                    print(tool_result)
            else:
                # Fallback to the final AI message if no tool result found
                final_message = response["messages"][-1]
                content = final_message.content
                
                # Clean up the final message
                if content and content != "How can I assist you further?":
                    print(content)
                else:
                    print("No response generated")
                    
        except Exception as e:
            print(f"Error: {e}")
            print("Please check if Ollama is running and the model is available.")
                
        except Exception as e:
            print(f"Error: {e}")
            print("Please check if Ollama is running and the model is available.")
            print("You might also try a larger model like 'llama3.2:3b' for better tool usage.")

if __name__ == "__main__":
    main()