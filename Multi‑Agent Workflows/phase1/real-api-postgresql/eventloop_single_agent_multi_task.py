"""
Multi Agent Async Workflow

Order Agent    -> PostgreSQL
Payment Agent  -> Payment System
Shipping Agent -> Shipping System

Customer Agent combines all results.
"""

import asyncio
import asyncpg

from agents import Agent, Runner, function_tool

# ----------------------------------
# Database Configuration
# ----------------------------------

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_postgres_password",
    "database": "testdb",
}


# ----------------------------------
# Tool 1: Order Database
# ----------------------------------


@function_tool
async def get_order_from_database(order_id: str):

    connection = await asyncpg.connect(**DB_CONFIG)

    try:

        query = """
            SELECT
                order_id,
                customer_name,
                product,
                status
            FROM orders
            WHERE order_id=$1
        """

        order = await connection.fetchrow(query, order_id)

        if order:

            return dict(order)

        return {"message": "Order not found"}

    finally:

        await connection.close()


# ----------------------------------
# Tool 2: Payment Service
# ----------------------------------


@function_tool
async def check_payment_status(order_id: str):

    return {
        "order_id": order_id,
        "payment_status": "SUCCESS",
        "amount": 90000,
    }


# ----------------------------------
# Tool 3: Shipping Service
# ----------------------------------


@function_tool
async def track_shipping(order_id: str):

    return {
        "order_id": order_id,
        "location": "Hyderabad Hub",
        "delivery_status": "Out For Delivery",
    }


# ----------------------------------
# Agents
# ----------------------------------

order_agent = Agent(
    name="Order Agent",
    instructions="""

    You handle order information.

    Use order database tool.

    """,
    tools=[get_order_from_database],
)


payment_agent = Agent(
    name="Payment Agent",
    instructions="""

    You validate payment information.

    Use payment tool.

    """,
    tools=[check_payment_status],
)


shipping_agent = Agent(
    name="Shipping Agent",
    instructions="""

    You track shipment information.

    Use shipping tool.

    """,
    tools=[track_shipping],
)


customer_agent = Agent(
    name="Customer Response Agent",
    instructions="""

    You prepare customer friendly
    order status summaries.

    """,
)


# ----------------------------------
# Multi Task Agent Workflow
# ----------------------------------


async def main():

    order_task = asyncio.create_task(
        Runner.run(order_agent, "Get order ORD1001 from database")
    )

    payment_task = asyncio.create_task(
        Runner.run(payment_agent, "Check payment for ORD1001")
    )

    shipping_task = asyncio.create_task(
        Runner.run(shipping_agent, "Track shipment for ORD1001")
    )

    order, payment, shipping = await asyncio.gather(
        order_task, payment_task, shipping_task
    )

    final_response = await Runner.run(
        customer_agent,
        f"""

        Prepare customer update.

        Order Details:
        {order.final_output}


        Payment Details:
        {payment.final_output}


        Shipping Details:
        {shipping.final_output}

        """,
    )

    print(final_response.final_output)


# ----------------------------------
# Start Event Loop
# ----------------------------------

if __name__ == "__main__":

    asyncio.run(main())
