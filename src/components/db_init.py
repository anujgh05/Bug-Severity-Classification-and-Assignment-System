import psycopg2
from src.logger import logging
import sys
from src.exception import CustomException
conn_info  = "host = localhost dbname='Minor Project' user=postgres password=2005 port=5432"

def initialize_database():
    try:
        logging.info("Connecting to PostgreSQL to initialize tables")
        with psycopg2.connect(conn_info) as conn:
            with conn.cursor() as cur:
                logging.info("Executing Table Creation Queries")
                cur.execute(
                    '''
                        CREATE TABLE IF NOT EXISTS developer_profiles(
                        developer_id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        expertise_profile TEXT NOT NULL,
                        current_workload INT DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE
                        );

                        CREATE TABLE IF NOT EXISTS bug_reports(
                        bug_id SERIAL PRIMARY KEY,
                        summary VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        predicted_severity VARCHAR(20),
                        final_severity VARCHAR(20),
                        confidence_score NUMERIC(5,2),
                        routing_status VARCHAR(30) DEFAULT 'automated',
                        assigned_dev_id INT REFERENCES developer_profiles(developer_id),
                        similarity_score NUMERIC(5,4),
                        created_at TIMESTAMP DEFAULT NOW()   
                        );

                        CREATE TABLE IF NOT EXISTS assignment_history(
                        history_id SERIAL PRIMARY KEY,
                        bug_id INT REFERENCES bug_reports(bug_id),
                        developer_id INT REFERENCES developer_profiles(developer_id),
                        assignment_mode VARCHAR(20)
                        );
                    '''
                )

                cur.execute("SELECT COUNT(*) FROM developer_profiles;")
                if cur.fetchone()[0] == 0:
                    logging.info("Inserting developers profiles")
                    dummy_developers = [
                        ("Anish Sharma", "anish@company.com", "frontend react javascript html css UI component design rendering layout responsive web app"),
                        ("Sita Thapa", "sita@company.com", "backend python flask postgresql database query optimization authentication api rest token fastpi"),
                        ("Rohan Shrestha", "rohan@company.com", "memory leak exception segmentation fault c pointers assembly compiler kernel crash buffer overflow"),
                        ("Deepa Joshi", "deepa@company.com", "machine learning pipeline training model trainer svm processing tf-idf vectorizer parsing logic numpy pandas")
                    ]
                    insert_query = """
                    INSERT INTO developer_profiles (name,email, expertise_profile) VALUES (%s, %s, %s);
                    """
                    cur.executemany(insert_query, dummy_developers)
                    logging.info("Successfully inserted 4 developer profiles.")
                else:
                    logging.info("Developer profiles already inserted. Skipping entry")
    except Exception as e:
        logging.info("Database Initialization Failed!")
        raise CustomException(e, sys)

if __name__ == "__main__":
    initialize_database()