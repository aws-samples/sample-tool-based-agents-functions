# Extending AI Agents with Custom Tools and Functions

*Give your agents the ability to interact with the real world*

---

This is the second post in our series on [AWS Prescriptive Guidance for Agentic AI Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/). Each post focuses on the concepts and patterns behind a single agent type, paired with a [hands-on sample on GitHub](README.md).

## Introduction

In the [previous post](https://github.com/aws-samples/sample-basic-reasoning-agents/blob/main/Building%20Basic%20Reasoning%20Agents%20with%20Amazon%20Bedrock%20and%20Strands%20SDK.md), we built basic reasoning agents that answer questions using an LLM's built-in knowledge. They're useful, but limited. An LLM is text in, text out. It can reason about a problem, but it has no I/O, no network, no database, no clock. To know today's weather or guarantee a calculation is correct, the agent needs to step outside the model and call systems built for that.

The solution is to give your agent tools.

By the end of this post, you'll understand:
- How tool calling became a first-class LLM capability
- Why tools transform what agents can do
- How the agent decides when and which tools to use
- What makes a tool description effective

---

## The Road to Tool Use: A Brief History

### The Text-Only Barrier (2020-2022)

When [GPT-3 launched in June 2020](https://en.wikipedia.org/wiki/GPT-3), the model was strong at generating text but couldn't act on the world. Ask it to summarize a document and it would. Ask it to fetch the latest stock price and it would either hallucinate one or admit it didn't know. The early workaround was prompt engineering: developers wrote system prompts that asked the model to *describe* what it wanted to do (e.g., "respond with JSON that includes a `tool_call` field"), then parsed the output and ran the tool themselves.

### ReAct: Reasoning and Acting (2022)

The first concrete framework for tool-using LLMs was [ReAct](https://arxiv.org/abs/2210.03629), introduced by Yao et al. in October 2022. ReAct showed that an LLM could interleave thought ("I need the population of Toronto") and action ("Search('population of Toronto')") in a single structured trace. The model wrote out its reasoning, picked an action, observed the result, and decided what to do next. ReAct established that tool use was a tractable pattern rather than a clever prompt hack.

### Toolformer: Teaching the Model When to Call (2023)

In February 2023, Meta published [Toolformer](https://arxiv.org/abs/2302.04761), which took a different angle. Instead of relying on the model to *infer* when to call tools at runtime, Toolformer trained the model on examples of tool calls inserted into the data, so the model learned to issue them on its own. This was the first signal that tool calling could become a built-in model capability rather than a prompt-engineering trick.

### Native Function Calling (2023-2024)

By mid-2023, providers started exposing tool calling as a first-class API feature. [OpenAI introduced function calling](https://openai.com/index/function-calling-and-other-api-updates/) in June 2023, letting developers describe tool schemas in JSON and receive structured tool calls back. [Anthropic's tool use](https://claude.com/blog/tool-use-ga) followed in May 2024, and Amazon Bedrock's [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) brought a unified tool-calling interface across the models it hosts. Schemas varied across providers, but the idea converged: describe your tools, the model picks one, you run it, you pass the result back.

### Standardization with MCP (2024)

The remaining friction was that every provider had its own format and every framework wrapped it differently. Anthropic's [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol), released in November 2024, standardized how tools (and other context like resources and prompts) get described to any model. You write a Python function with type hints, decorate it with `@tool`, and the SDK handles schema generation, dispatch, and result handling against whatever model provider you've configured.

---

## Why Tools Matter

Basic reasoning agents are limited to what the model learned from training. That knowledge has a cutoff date, doesn't include your proprietary data, and can't perform precise calculations.

Tools break these barriers. With defined functions and the `@tool` decorator, your agent can:

- **Perform calculations** with mathematical precision
- **Fetch real-time data** from APIs and databases
- **Execute code** in controlled environments
- **Interact with external systems** like CRMs, ERPs, or custom services

---

## How Tool Calling Works

<img src="images/tool-based-agents.png" width="600" alt="Diagram of a tool-based agent: a query and tool metadata go to the LLM, which selects a tool, the tool runner executes it, and the result is folded back into the response." />

When you give an agent tools, it gets to decide when and how to use them. The flow looks like this:

1. **Analysis**: The model analyzes the query to determine if any tool is needed
2. **Selection**: If needed, the model selects the appropriate tool (or tools)
3. **Invocation**: The agent calls the tool with parameters extracted from the query
4. **Integration**: The tool's results are incorporated into the final response

Nothing in that flow is coded routing. You describe each tool well with the proper parameters, and the model handles selection. The quality of the doc-string is what determines whether the right tool gets called.

---

## What Makes a Good Tool

In the Strands SDK, a tool is just a function with a clear description. The model never sees your implementation. That description is effectively a prompt, so the quality of your tool definitions determines how reliably the agent uses them.

### Write Descriptions for the Model, Not the Reader

The model uses a tool's description to decide when to call it. Good descriptions:

- **State the purpose clearly**: "Calculate compound interest," not "Do financial stuff"
- **List specific use cases**: "Use for weather forecasts, temperature checks, and climate queries"
- **Define parameters precisely**: Include valid values, defaults, and constraints
- **Mention what it returns**: "Returns temperature in the specified units and current conditions"

### Keep Each Tool Focused

Each tool should do one thing well. A single tool that branches on an `action` parameter to do weather *and* math *and* search is harder for the model to select correctly than three separate, focused tools. Narrow tools with descriptive names are easier for the LLM to reason about.

### Handle Errors and Return Useful Output

Tools should never crash the agent. Return an error message the model can work with ("Cannot divide by zero. Please provide a non-zero denominator") rather than raising an exception. And give the model context in the result: "Product 'Widget' (ID: 123) has 42 units in stock" is far more useful than a bare "42," because the agent uses that text to compose its answer.

### Debugging Tool Selection

If the agent isn't using a tool when you expect it to, the fix is usually in the description. Check that the docstring clearly states *when* to use the tool, confirm the parameter types match what the model would infer, and start with a single tool before adding more. You can even ask the agent "What tools do you have?" to see how it interprets your definitions.

---

## When to Use Tool Supported Agents

Tool based agents should be used anytime you need current information, deterministic results, or you need your agent to be able to integrate and connect with something else

| Use Case | Tool Example |
|----------|-------------|
| **Calculations** | Calculator, unit converter, financial formulas |
| **Data retrieval** | Weather API, stock prices, exchange rates |
| **Database queries** | Customer lookup, order history, inventory check |
| **AWS operations** | Amazon EC2 status, Amazon S3 operations, AWS Lambda invocation |
| **External integrations** | CRM lookup, ticket creation, notification sending |

For connecting tools to AWS services, the [AWS SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) is the usual starting point.

---

## What's Next

You now understand how tools transform an agent from a conversationalist into an actor, how the model decides which tool to call, and what makes a tool description effective. The natural next step is to see it run. The **[companion sample](README.md)** walks through a multi-tool agent with the Strands SDK.

But what happens when your tools become complex, or live in their own process, or need to be shared across many agents? That's where tool servers come in. In the [next post](https://github.com/aws-samples/sample-tool-based-agents-servers/blob/main/Delegating%20Work%20-%20Tool%20Servers%20and%20the%20Model%20Context%20Protocol.md), we'll explore the Model Context Protocol (MCP) and agents that delegate to external tool servers.

---

## Resources

- [Companion sample: Tool-Based Agents](README.md)
- [AWS Prescriptive Guidance - Tool-based agents for calling functions](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/tool-based-agents-for-calling-functions.html)
- [Strands Agents Documentation](https://strandsagents.com/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)

---

**Tim Sitze** is a Solutions Architect at Amazon Web Services, where he works with cybersecurity ISVs to design and scale their products on AWS. He specializes in security, AI/ML, IoT and data platform architectures, and has partnered on workloads spanning identity threat intelligence, agentic AI, and cloud-native security operations. Tim is based in the Washington, D.C. area.  
