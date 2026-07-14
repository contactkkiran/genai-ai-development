# https://openai.github.io/openai-agents-python/
# pip install openai-agents
# Example of using the OpenAI Agents library to create an agent and run a task
from email import message
from time import asctime
from urllib import response

from agents import Agent, Runner
from gradio import Info
from griffe import Logger
from langsmith import expect
from openai import timeout
from param import INFO

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)


agent = Agent(name="Assistant", instructions="You are a helpful assistant")


# Example of using the OpenAI Agents library to create an agent and
# run a task asynchronously

# Why Async Is Used in Real Projects
# Performance → Handle thousands of requests per second.
# Non-blocking I/O → Don’t freeze while waiting for external services (DB, APIs).
# Scalability → Essential for microservices, chat apps, and real-time dashboards.
import asyncio


async def main2():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")
    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)


# Runner is not required for async usage,
# but it is a convenient way to run agents in an async context.
asyncio.run(main2())

# Example of using the OpenAI Agents library to create an agent and run a task with a custom model
agent = Agent(
    name="Assistant", instructions="You are a helpful assistant", model="gpt-4o"
)
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)


# Example usin asyncio to run an agent
async def main1():
    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)


asyncio.run(main1())


# Example with custom timeout
async def main3():
    try:
        result = await asyncio.wait_for(
            Runner.run(agent, "Write a haiku about recursion in programming."),
            timeout=5,
        )
        print(result.final_output)
    except asyncio.TimeoutError:
        print("The agent took too long to respond.")


asyncio.run(main3())

# Please print one production ready code snippet that uses the OpenAI Agents library
#  to create an agent, run a task asynchronously,
# and handle potential timeouts gracefully.
# The agent should be instructed to write a haiku about recursion in programming,
#  and the code should include error handling for timeouts.

from agents import Agent, Runner

# import asyncio
# import logging

# # Configure logging
# logging.basicConfig(level=INFO, format="%(asctime)s-%(levelname)s-%(message)s")

# # Create Agent
# haiku_agent = Agent(
#     name="PoetryAssistant",
#     instructions="""
#         You are a creative writing assistant.

#         Task :
#         - Write high-quality haiku poems
#         - Follow traditional haiku structure
#         - Keep responses concise and creative
#     """,
# )


# async def generate_haiku():
#     """
#     Runs AI agent asyncronously with timeout handling.
#     """
#     prompt = "Write a haiku about recursion in programming "
#     try:
#         result = await asyncio.wait_for(Runner.run(haiku_agent, prompt), timeout=5)
#         return result.final_output
#     except asyncio.TimeoutError:
#         logging.error("Agent Execution timed out")
#         return "Request Timed out" f"Agent failed"


# async def main():
#     response = await generate_haiku()


# if __name__ == "__main__":

#     asyncio.run(main())

# pip install openai-agents

import asyncio
import logging

from agents import Agent, Runner

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Create Agent
haiku_agent = Agent(
    name="PoetryAssistant",
    instructions="""
    You are a creative writing assistant.

    Task:
    - Write high-quality haiku poems
    - Follow traditional haiku structure
    - Keep responses concise and creative
    """,
)


async def generate_haiku():
    """
    Runs the AI agent asynchronously with timeout handling.
    """

    prompt = "Write a haiku about recursion in programming."

    try:
        logging.info("Starting agent execution...")

        # Run agent asynchronously with timeout
        result = await asyncio.wait_for(
            Runner.run(haiku_agent, prompt), timeout=10  # seconds
        )

        logging.info("Agent completed successfully")

        return result.final_output

    except asyncio.TimeoutError:
        logging.error("Agent execution timed out")

        return "Request timed out. " "Please try again later."

    except Exception as error:
        logging.exception("Unexpected error occurred")

        return f"Agent failed: {error}"


async def main():

    response = await generate_haiku()

    print("\nAI Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
