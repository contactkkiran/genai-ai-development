"""
OpenAI Agent -> Tool Calling -> PostgreSQL Workflow

Description:
    This module demonstrates an Agentic AI workflow where an
    OpenAI Agent retrieves user information from PostgreSQL
    using a database function tool.
"""

import asyncio

import asyncpg

from agents import Agent, Runner, function_tool

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "postgre",
    "database": "testdb",
}


@function_tool
async def get_user_from_database(user_id: int):
    """
    Retrieves user details from PostgreSQL database.

    Args:
        user_id: Unique user identifier.

    Returns:
        User information dictionary or message.
    """

    connection = await asyncpg.connect(**DB_CONFIG)

    try:
        query = """
            SELECT
                id,
                name,
                username,
                email
            FROM users
            WHERE id = $1
        """

        user_record = await connection.fetchrow(
            query,
            user_id,
        )

        if not user_record:
            return {"message": "No user found"}

        return dict(user_record)

    finally:
        await connection.close()


qa_agent = Agent(
    name="QA Data Validation Agent",
    instructions="""
    You are a QA Data Validation Agent.

    Responsibilities:
    - Retrieve user information from database
    - Use available tools when data access is required
    - Validate and summarize user information clearly
    """,
    tools=[get_user_from_database],
)


async def main():
    """
    Application entry point.
    Executes the AI agent workflow.
    """

    response = await Runner.run(
        qa_agent,
        "Get user id 1 details from database",
    )

    print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
