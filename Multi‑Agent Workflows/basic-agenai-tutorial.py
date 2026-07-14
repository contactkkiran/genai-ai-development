# 🟢 Step 1: Basic Agent Program


print("Hello, I am your Agentic AI reasoning engine!")

# 🟢 Step 2: Add Simple Decision-Making
user_input = "order_status"
if user_input == "order_status":
    print("I can help you check your order status.")
else:
    print("I will search the FAQ database.")

# 🟢 Step 3: Think → Act → Respond

goal = "track_order"
print("Thinking about the goal:", goal)
if goal == "track_order":
    action = "Tracking order in the system"
else:
    goal = "search_faq"
print("Action:", action)
print("Responding to user: Your order is being tracked!")

# 🟢 Step 4: Next Steps
# In real Agentic AI, the reasoning engine often calls
# external tools (like an Order API). Since we don’t have a real API here, we’ll simulate one with a Python function.

# Step 5: Self-Reflection

def check_order_status(order_id):
    # Simulated API response

    fake_database = {
        "12345": "In transit, expected tomorrow",
        "67890": "Delivered yesterday",
        "11111": "Processing at warehouse",
    }

    return fake_database.get(order_id, "Order ID not found")

goal = "track_order"
ordered_id = "12345"
if goal == "track_order":
    action = "Call Order API"# please note that this is a simulated action, not an actual API call
    
    print("Action choosen:", action)
    result = check_order_status(ordered_id)
if "Not found" in result.lower():
    print("Self-reflection: Hmm, this answer may not be helpful.")
    print(
        f"Responding to user: Sorry, I couldn’t find your {ordered_id}. Please double-check the ID."
    )
else:
    print("Self-reflection: This answer seems helpful.")
    print(f"Responding to user: Your order {ordered_id} status is: {result}")

