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


class BugSubmitRequest(BaseModel):
    summary: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class OverrideRequest(BaseModel):
    severity: str = Field(..., pattern="^(Low|Medium|High)$")


@app.post("/api/v1/bugs/submit")
def submit_bug(payload: BugSubmitRequest):
    try:
        result = predict_pipeline.predict(payload.summary, payload.description)
        confidence_pct = float(result["confidence"].replace("%", ""))

        response = {
            "bug_id": result["bug_id"],
            "predicted_class": result["severity"],
            "max_confidence": confidence_pct,
            "routing_status": result["status"],
        }

        if result["status"] == "automated":
            dev_id, sim_score = assignment_pipeline.assign_developer(
                result["bug_id"], result["cleaned_text"]
            )
            response["assigned_developer_id"] = dev_id
            response["similarity_score"] = round(sim_score * 100, 1)

        return response
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
                   b.similarity_score, b.created_at, d.name AS developer_name
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
