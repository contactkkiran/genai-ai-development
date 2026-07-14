import psycopg2

# ==========================================================
# PostgreSQL Database Connection
# ==========================================================

conn = psycopg2.connect(
    dbname="ragdb",
    user="raguser",
    password="Kiran@143",
    host="localhost",
    port="5432",
)

cur = conn.cursor()


# ==========================================================
# Create Queries Table
# ==========================================================

cur.execute("""
    CREATE TABLE IF NOT EXISTS queries
    (
        id SERIAL PRIMARY KEY,
        question TEXT,
        answer TEXT
    );
    """)

conn.commit()


# ==========================================================
# Save User Query And AI Response
# ==========================================================


def log_query(question: str, answer: str):

    cur.execute(
        """
        INSERT INTO queries
        (
            question,
            answer
        )
        VALUES
        (
            %s,
            %s
        )
        """,
        (question, answer),
    )

    conn.commit()


# def log_query(question: str, answer: str):
#     print(f"Logged: {question} -> {answer}")
