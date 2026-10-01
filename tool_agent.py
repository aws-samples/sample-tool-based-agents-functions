"""
Tool-Based Agent - Function Tools

An agent that extends basic reasoning with custom tools/functions.
The agent decides when and which tools to call based on the user's query.

Learning objectives:
- Understand how to create custom tools with the @tool decorator
- See how agents decide when to use tools
- Learn tool parameter handling and return values
- Watch the agent stream its response and announce each tool it uses

Tools print their own inputs and results inline so the viewer can tell when
the agent reasoned through something on its own versus when it actually
delegated to a tool.
"""

import time
from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent, tool


# Define custom tools using the @tool decorator. Each tool prints its inputs
# and the value it's returning, so the trace lives next to the code that
# actually does the work.
@tool
def calculator(operation: str, a: float, b: float) -> str:
    """Perform basic arithmetic operations.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    """
    print(f"          calculator(operation={operation!r}, a={a}, b={b})")
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero",
    }
    result = operations.get(operation.lower(), "Unknown operation")
    output = f"{a} {operation} {b} = {result}"
    print(f"          -> {output}")
    return output


@tool
def get_weather(city: str, units: str = "celsius") -> str:
    """Get the current weather for a city (simulated).

    Args:
        city: The name of the city
        units: Temperature units (celsius or fahrenheit)
    """
    print(f"          get_weather(city={city!r}, units={units!r})")
    # Simulated weather data
    weather_data = {
        "new york": {"temp_c": 22, "condition": "Partly cloudy"},
        "london": {"temp_c": 15, "condition": "Rainy"},
        "tokyo": {"temp_c": 28, "condition": "Sunny"},
        "sydney": {"temp_c": 18, "condition": "Clear"},
    }

    city_lower = city.lower()
    if city_lower in weather_data:
        data = weather_data[city_lower]
        temp = data["temp_c"]
        if units.lower() == "fahrenheit":
            temp = (temp * 9 / 5) + 32
            unit_symbol = "°F"
        else:
            unit_symbol = "°C"
        output = f"Weather in {city}: {temp}{unit_symbol}, {data['condition']}"
    else:
        output = f"Weather data not available for {city}"
    print(f"          -> {output}")
    return output


@tool
def search_knowledge(query: str) -> str:
    """Search a knowledge base for information (simulated).

    Args:
        query: The search query
    """
    print(f"          search_knowledge(query={query!r})")
    knowledge = {
        "python": "Python is a high-level programming language known for readability.",
        "strands": "Strands Agents SDK is a framework for building AI agents.",
        "bedrock": "Amazon Bedrock provides access to foundation models via API.",
        "agent": "An AI agent is a system that can perceive, reason, and act autonomously.",
    }

    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            output = f"Found: {value}"
            print(f"          -> {output}")
            return output
    output = f"No results found for: {query}"
    print(f"          -> {output}")
    return output


# Streaming callback handler prints model tokens as they arrive and announces
# each tool the agent calls. Pass callback_handler=None to silence both.
stream_handler = StreamingCallbackHandler()

agent = Agent(
    model=get_model(),
    system_prompt="""You are a helpful assistant with access to tools.
    Use the calculator for math operations, get_weather for weather queries,
    and search_knowledge for information lookups. Always use the appropriate
    tool when the user's request matches its capabilities.""",
    tools=[calculator, get_weather, search_knowledge],
    callback_handler=stream_handler,
)


def main():
    """Run the tool-based agent interactively."""
    print("Tool-Based Agent (Functions)")
    print("=" * 40)
    print("Available tools: calculator, weather, knowledge search")
    print("Tool calls and results appear inline as the agent runs.")
    print("Type 'quit' to exit")
    print("Tip: You can paste multi-line prompts!\n")

    while True:
        user_input = get_multiline_input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        stream_handler.reset()
        print("\nAgent: ", end="", flush=True)

        start_time = time.time()
        agent(user_input)
        elapsed = time.time() - start_time

        print(f"\n({elapsed:.1f}s)\n")


if __name__ == "__main__":
    main()
