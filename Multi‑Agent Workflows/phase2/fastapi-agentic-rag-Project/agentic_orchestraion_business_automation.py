# Step 1: Import required libraries
from fastapi import FastAPI
import uvicorn
import psycopg2

# Step 2: Connect to HR Database
# --------------------------------
# This connection is dedicated to HR Agent
hr_conn = psycopg2.connect(
    dbname="hr_db",  # Step 2a: HR database name
    user="postgres",  # Step 2b: Replace with your PostgreSQL username
    password="postgre",  # Step 2c: Replace with your PostgreSQL password
    host="localhost",  # Step 2d: Host (local machine)
    port="5432",  # Step 2e: Default PostgreSQL port
)
hr_conn.autocommit = True
hr_cursor = hr_conn.cursor()

# Step 3: Connect to IT Database
# --------------------------------
# This connection is dedicated to IT Agent
it_conn = psycopg2.connect(
    dbname="it_db",  # Step 3a: IT database name
    user="postgres",  # Step 3b: Replace with your PostgreSQL username
    password="postgre",  # Step 3c: Replace with your PostgreSQL password
    host="localhost",  # Step 3d: Host (local machine)
    port="5432",  # Step 3e: Default PostgreSQL port
)
it_conn.autocommit = True
it_cursor = it_conn.cursor()


# Step 4: Define HR Agent
# --------------------------------
class HRAgent:
    def handle(self, employee_name: str):
        # Step 4a: Insert record into HR DB
        hr_cursor.execute(
            "INSERT INTO hr_records (employee_name, status) VALUES (%s, %s)",
            (employee_name, "HR record created"),
        )
        return f"HR Agent: HR record stored for {employee_name}"


# Step 5: Define IT Agent
# --------------------------------
class ITAgent:
    def handle(self, employee_name: str):
        # Step 5a: Insert record into IT DB
        it_cursor.execute(
            "INSERT INTO it_records (employee_name, resources) VALUES (%s, %s)",
            (employee_name, "Email + Laptop provisioned"),
        )
        return f"IT Agent: IT resources stored for {employee_name}"


# Step 6: Define Orchestrator Agent
# --------------------------------
class Orchestrator:
    def __init__(self):
        self.hr = HRAgent()
        self.it = ITAgent()

    def run_workflow(self, employee_name: str):
        # Step 6a: Call HR Agent
        hr_result = self.hr.handle(employee_name)
        # Step 6b: Call IT Agent
        it_result = self.it.handle(employee_name)
        # Step 6c: Return combined results
        return {"workflow": "Employee Onboarding", "results": [hr_result, it_result]}


# Step 7: Setup FastAPI Application
# --------------------------------
app = FastAPI()
orchestrator = Orchestrator()


# Step 8: Define API Endpoint
# --------------------------------
@app.get("/onboard/{employee_name}")
def onboard_employee(employee_name: str):
    # Step 8a: Run workflow for given employee
    return orchestrator.run_workflow(employee_name)


# Step 9: Run FastAPI Server
# --------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
