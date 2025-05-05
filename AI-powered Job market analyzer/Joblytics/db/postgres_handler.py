import psycopg2
from psycopg2 import sql
from datetime import datetime

def connect():
    return psycopg2.connect(
        dbname="jobdb",
        user="your_username",
        password="your_password",
        host="localhost",
        port="5432"
    )

def insert_jobs(job):
    conn = connect()
    cur = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO Jobs (title, company, location, job_type, salary_range, description,
                          requirements, posted_date, job_link, source, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_link) DO NOTHING;
    """)

    data = (
        job["title"], job["company"], job["location"], job["job_type"], job["salary_range"],
        job["description"], job["requirements"], job["posted_date"],
        job["job_link"], job["source"], datetime.now()
    )

    try:
        cur.execute(insert_query, data)
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Failed to insert job: {e}")
    finally:
        cur.close()
        conn.close()
