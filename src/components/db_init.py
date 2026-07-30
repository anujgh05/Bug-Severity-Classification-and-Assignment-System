import hashlib
import sys
import psycopg2
from src.exception import CustomException
from src.logger import logging

conn_info = "host = localhost dbname='Minor Project' user=postgres password=2005 port=5432"


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a fixed salt."""
    salt = "bug_triage_salt_2026"
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()


def initialize_database():
    try:
        logging.info("Connecting to PostgreSQL to initialize tables")
        with psycopg2.connect(conn_info) as conn:
            with conn.cursor() as cur:
                logging.info("Executing Table Creation Queries")
                cur.execute(
                    """
                        CREATE TABLE IF NOT EXISTS developer_profiles(
                            developer_id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            email VARCHAR(100) UNIQUE NOT NULL,
                            expertise_profile TEXT NOT NULL,
                            current_workload INT DEFAULT 0,
                            is_active BOOLEAN DEFAULT TRUE
                        );

                        CREATE TABLE IF NOT EXISTS users(
                            user_id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            email VARCHAR(100) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'admin', 'developer')),
                            developer_id INT REFERENCES developer_profiles(developer_id) ON DELETE SET NULL,
                            created_at TIMESTAMP DEFAULT NOW()
                        );

                        CREATE TABLE IF NOT EXISTS bug_reports(
                            bug_id SERIAL PRIMARY KEY,
                            summary VARCHAR(255) NOT NULL,
                            description TEXT NOT NULL,
                            reporter_user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
                            predicted_severity TEXT,
                            final_severity TEXT,
                            confidence_score NUMERIC(5,2),
                            routing_status VARCHAR(30) DEFAULT 'automated',
                            bug_status VARCHAR(30) DEFAULT 'pending',
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
                    """
                )

                # Ensure reporter_user_id and bug_status columns exist for existing databases
                try:
                    cur.execute(
                        """
                        ALTER TABLE bug_reports
                        ALTER COLUMN predicted_severity TYPE TEXT,
                        ALTER COLUMN final_severity TYPE TEXT;
                        """
                    )
                    cur.execute(
                        """
                        ALTER TABLE bug_reports
                        ADD COLUMN IF NOT EXISTS reporter_user_id INT REFERENCES users(user_id) ON DELETE SET NULL;
                        """
                    )
                    cur.execute(
                        """
                        ALTER TABLE bug_reports
                        ADD COLUMN IF NOT EXISTS bug_status VARCHAR(30) DEFAULT 'pending';
                        """
                    )
                except Exception:
                    # If bug_reports does not yet exist this will be a no-op because
                    # the CREATE TABLE above ensures its presence; swallow errors here
                    pass

                # Seed developer profiles if empty
                cur.execute("SELECT COUNT(*) FROM developer_profiles;")
                if cur.fetchone()[0] == 0:
                    logging.info("Inserting developer profiles")
                    dummy_developers = [
                        (
                            "Anish Sharma",
                            "anish@company.com",
                            "frontend react javascript html css UI component design rendering layout responsive web app",
                        ),
                        (
                            "Sita Thapa",
                            "sita@company.com",
                            "backend python flask postgresql database query optimization authentication api rest token fastpi",
                        ),
                        (
                            "Rohan Shrestha",
                            "rohan@company.com",
                            "memory leak exception segmentation fault c pointers assembly compiler kernel crash buffer overflow",
                        ),
                        (
                            "Deepa Joshi",
                            "deepa@company.com",
                            "machine learning pipeline training model trainer svm processing tf-idf vectorizer parsing logic numpy pandas",
                        ),
                    ]
                    insert_query = """
                    INSERT INTO developer_profiles (name, email, expertise_profile) VALUES (%s, %s, %s);
                    """
                    cur.executemany(insert_query, dummy_developers)
                    logging.info("Successfully inserted 4 developer profiles.")

                # Seed initial users if empty
                cur.execute("SELECT COUNT(*) FROM users;")
                if cur.fetchone()[0] == 0:
                    logging.info("Inserting initial users into users table")
                    default_users = [
                        ("user1", "user1@triage.com", hash_password("user123"), "user", None),
                        ("admin", "admin@triage.com", hash_password("admin123"), "admin", None),
                        ("anish", "anish@company.com", hash_password("dev123"), "developer", 1),
                        ("sita", "sita@company.com", hash_password("dev123"), "developer", 2),
                        ("rohan", "rohan@company.com", hash_password("dev123"), "developer", 3),
                        ("deepa", "deepa@company.com", hash_password("dev123"), "developer", 4),
                    ]
                    insert_user_query = """
                    INSERT INTO users (username, email, password_hash, role, developer_id)
                    VALUES (%s, %s, %s, %s, %s);
                    """
                    cur.executemany(insert_user_query, default_users)
                    logging.info("Successfully inserted initial user accounts.")

    except Exception as e:
        logging.info("Database Initialization Failed!")
        raise CustomException(e, sys) from e


if __name__ == "__main__":
    initialize_database()