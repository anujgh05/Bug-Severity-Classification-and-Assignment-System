import hashlib
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor
import psycopg2

from src.pipeline.prediction_pipeline import PredictPipeline
from src.pipeline.assignment_pipeline import AssignmentPipeline

app = FastAPI(title="Bug Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONN_INFO = "host=localhost dbname='Minor Project' user=postgres password=2005 port=5432"

predict_pipeline = PredictPipeline()
assignment_pipeline = AssignmentPipeline()

SEVERITY_MAP = {
    "Low": "Low Priority",
    "Medium": "Medium Priority",
    "High": "High Priority",
}


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a fixed salt."""
    salt = "bug_triage_salt_2026"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Optional[str] = None
    developer_id: Optional[int] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=4)
    role: str = Field("user", pattern="^(user|admin|developer)$")
    developer_id: Optional[int] = None


class BugSubmitRequest(BaseModel):
    summary: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    reporter_user_id: Optional[int] = None


class OverrideRequest(BaseModel):
    severity: str = Field(..., pattern="^(Low|Medium|High)$")


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest):
    try:
        pass_hash = hash_password(payload.password)
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Query user by username or email and hashed password
                cur.execute(
                    """
                    SELECT user_id, username, email, role, developer_id
                    FROM users
                    WHERE (username = %s OR email = %s) AND password_hash = %s;
                    """,
                    (payload.username_or_email, payload.username_or_email, pass_hash),
                )
                user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username/email or password")

        # If a specific role was requested by the login form, verify role match
        if payload.role and user["role"] != payload.role:
            raise HTTPException(
                status_code=403,
                detail=f"Account is registered as '{user['role']}', not '{payload.role}'",
            )

        # Handle developer_id override or binding
        dev_id = user["developer_id"]
        if user["role"] == "developer" and payload.developer_id:
            dev_id = payload.developer_id

        return {
            "message": "Login successful",
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "developer_id": dev_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/auth/register")
def register(payload: RegisterRequest):
    try:
        pass_hash = hash_password(payload.password)
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash, role, developer_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING user_id, username, email, role, developer_id;
                    """,
                    (
                        payload.username,
                        payload.email,
                        pass_hash,
                        payload.role,
                        payload.developer_id,
                    ),
                )
                user = cur.fetchone()

        return {"message": "User registered successfully", "user": user}
    except psycopg2.IntegrityError:
        raise HTTPException(
            status_code=400, detail="Username or email already exists"
        ) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/bugs/submit")
def submit_bug(payload: BugSubmitRequest):
    try:
        result = predict_pipeline.predict(payload.summary, payload.description, payload.reporter_user_id)
        confidence_pct = float(result["confidence"].replace("%", ""))

        response = {
            "bug_id": result["bug_id"],
            "predicted_class": result["severity"],
            "max_confidence": confidence_pct,
            "routing_status": result["status"],
        }

        # If the request included a reporter_user_id (i.e. end-user submitted),
        # do not return the numeric confidence to the client to avoid exposing
        # model assignment percentages to end users.
        if getattr(payload, 'reporter_user_id', None) is not None:
            response.pop('max_confidence', None)

        if result["status"] == "automated":
            dev_id, sim_score = assignment_pipeline.assign_developer(
                result["bug_id"], result["cleaned_text"]
            )
            response["assigned_developer_id"] = dev_id
            response["similarity_score"] = round(sim_score * 100, 1)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/user/{user_id}/bugs")
def get_user_bugs(user_id: int):
    try:
        query = """
            SELECT b.bug_id,
                   b.summary,
                   b.description,
                   b.predicted_severity,
                   b.final_severity,
                   b.confidence_score,
                   b.routing_status,
                   b.bug_status,
                   b.assigned_dev_id,
                   d.name AS assigned_developer_name,
                   b.created_at
            FROM bug_reports b
            LEFT JOIN developer_profiles d ON b.assigned_dev_id = d.developer_id
            WHERE b.reporter_user_id = %s
            ORDER BY b.created_at DESC;
        """
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (user_id,))
                rows = cur.fetchall()

        return [
            {
                "bug_id": row["bug_id"],
                "summary": row["summary"],
                "description": row["description"],
                "severity": row["final_severity"] or row["predicted_severity"],
                "max_confidence": float(row["confidence_score"]) if row["confidence_score"] else None,
                "routing_status": row["routing_status"],
                "bug_status": row["bug_status"],
                "assigned_developer_id": row["assigned_dev_id"],
                "assigned_developer_name": row["assigned_developer_name"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(resolved|pending)$")


@app.put("/api/v1/developer/{developer_id}/bugs/{bug_id}/status")
def developer_update_bug_status(developer_id: int, bug_id: int, payload: StatusUpdateRequest):
    try:
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT assigned_dev_id, bug_status FROM bug_reports WHERE bug_id = %s;",
                    (bug_id,),
                )
                bug = cur.fetchone()
                if not bug:
                    raise HTTPException(status_code=404, detail="Bug not found")

                if bug["assigned_dev_id"] != developer_id:
                    raise HTTPException(status_code=403, detail="Developer not authorized to update this bug")

                new_status = payload.status
                current_status = bug["bug_status"]

                cur.execute(
                    "UPDATE bug_reports SET bug_status = %s WHERE bug_id = %s RETURNING bug_id, bug_status, assigned_dev_id;",
                    (new_status, bug_id),
                )
                updated = cur.fetchone()

                if current_status != "resolved" and new_status == "resolved":
                    cur.execute(
                        "UPDATE developer_profiles SET current_workload = GREATEST(current_workload - 1, 0) WHERE developer_id = %s RETURNING current_workload;",
                        (developer_id,),
                    )
                    workload = cur.fetchone()["current_workload"]
                elif current_status == "resolved" and new_status != "resolved":
                    cur.execute(
                        "UPDATE developer_profiles SET current_workload = current_workload + 1 WHERE developer_id = %s RETURNING current_workload;",
                        (developer_id,),
                    )
                    workload = cur.fetchone()["current_workload"]
                else:
                    workload = None

        response = {
            "bug_id": updated["bug_id"],
            "bug_status": updated["bug_status"],
        }
        if workload is not None:
            response["current_workload"] = workload

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/admin/pending")
def get_pending_bugs():
    try:
        query = """
            SELECT bug_id, summary, description, predicted_severity,
                   confidence_score, routing_status, created_at
            FROM bug_reports
            WHERE routing_status = 'pending_review'
            ORDER BY created_at DESC;
        """
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()

        return [
            {
                "bug_id": row["bug_id"],
                "summary": row["summary"],
                "description": row["description"],
                "predicted_severity": row["predicted_severity"],
                "max_confidence": float(row["confidence_score"]),
                "routing_status": row["routing_status"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.put("/api/v1/admin/override/{bug_id}")
def override_bug(bug_id: int, payload: OverrideRequest):
    try:
        final_severity = SEVERITY_MAP[payload.severity]

        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT summary, description, routing_status FROM bug_reports WHERE bug_id = %s;",
                    (bug_id,),
                )
                bug = cur.fetchone()
                if not bug:
                    raise HTTPException(status_code=404, detail="Bug not found")
                if bug["routing_status"] != "pending_review":
                    raise HTTPException(status_code=400, detail="Bug is not pending review")

                cur.execute(
                    """
                    UPDATE bug_reports
                    SET final_severity = %s, predicted_severity = %s, routing_status = 'automated'
                    WHERE bug_id = %s;
                    """,
                    (final_severity, final_severity, bug_id),
                )

        combined_text = f"{bug['summary']} {bug['description']}"
        cleaned_text = predict_pipeline.clean_text(combined_text)
        dev_id, sim_score = assignment_pipeline.assign_developer(bug_id, cleaned_text)

        return {
            "bug_id": bug_id,
            "final_severity": final_severity,
            "routing_status": "automated",
            "assigned_developer_id": dev_id,
            "similarity_score": round(sim_score * 100, 1),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/developer/{developer_id}/tasks")
def get_developer_tasks(developer_id: int):
    try:
        query = """
            SELECT b.bug_id, b.summary, b.description, b.final_severity,
                   b.predicted_severity, b.confidence_score, b.routing_status,
                   b.bug_status, b.similarity_score, b.created_at, d.name AS developer_name
            FROM bug_reports b
            LEFT JOIN developer_profiles d ON b.assigned_dev_id = d.developer_id
            WHERE b.assigned_dev_id = %s
            ORDER BY b.created_at DESC;
        """
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (developer_id,))
                rows = cur.fetchall()

        return [
            {
                "bug_id": row["bug_id"],
                "summary": row["summary"],
                "description": row["description"],
                "severity": row["final_severity"] or row["predicted_severity"],
                "max_confidence": float(row["confidence_score"]) if row["confidence_score"] else None,
                "routing_status": row["routing_status"],
                "bug_status": row["bug_status"],
                "similarity_score": float(row["similarity_score"]) * 100 if row["similarity_score"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/developers")
def list_developers():
    try:
        with psycopg2.connect(CONN_INFO) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT developer_id, name, email, current_workload FROM developer_profiles WHERE is_active = TRUE;"
                )
                return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
