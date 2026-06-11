from flask import Flask, request, jsonify, render_template
from src.pipeline.prediction_pipeline import PredictPipeline
from src.pipeline.assignment_pipeline import AssignmentPipeline 

app = Flask(__name__)

predict_pipeline = PredictPipeline()
assignment_pipeline = AssignmentPipeline()

@app.route('/')
def index():
    return """
    <html>
        <body style="font-family: Arial; margin: 50px; max-width: 600px;">
            <h2>Bug Reporting Triage System</h2>
            <form action="/predict" method="POST" style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                    <label style="font-weight: bold;">Bug Summary:</label><br>
                    <input type="text" name="summary" style="width: 100%; padding: 8px;" placeholder="e.g., Database connection timeout on login" required>
                </div>
                <div>
                    <label style="font-weight: bold;">Detailed Description:</label><br>
                    <textarea name="description" rows="6" style="width: 100%; padding: 8px;" placeholder="e.g., Driver throws connection refusion error after 30 seconds of inactivity..." required></textarea>
                </div>
                <button type="submit" style="padding: 10px; background-color: #007BFF; color: white; border: none; cursor: pointer; font-weight: bold;">
                    Analyze & Route Bug
                </button>
            </form>
        </body>
    </html>
    """

@app.route('/predict', methods=['POST'])
def predict_datapoint():
    try:
        summary = request.form.get('summary')
        description = request.form.get('description')

        if not summary or not description:
            return jsonify({"error": "Missing summary or description"}), 400

        # Step 1: Run classification and save initial bug log
        classification_result = predict_pipeline.predict(summary, description)
        
        bug_id = classification_result["bug_id"]
        cleaned_text = classification_result["cleaned_text"]
        routing_status = classification_result["status"]

        # Step 2: Run developer assignment conditional loop
        assigned_dev_message = ""
        if routing_status == "automated":
            # Pass the bug details directly to the assignment engine
            dev_id, sim_score = assignment_pipeline.assign_developer(bug_id, cleaned_text)
            assigned_dev_message = f"Automatically assigned to Developer ID {dev_id} (Similarity: {sim_score*100:.1f}%)"
        else:
            assigned_dev_message = "Assignment held back. Bug requires human verification first."

        # Step 3: Send responses to UI template
        return f"""
        <html>
            <body style="font-family: Arial; margin: 40px; line-height: 1.6;">
                <h2>System Routing Pipeline Logs</h2>
                <p><b>Database Bug ID:</b> {bug_id}</p>
                <p><b>Predicted Severity:</b> {classification_result["severity"]}</p>
                <p><b>Pipeline Confidence:</b> {classification_result["confidence"]}</p>
                <p><b>Routing Flag:</b> {routing_status.upper()}</p>
                <hr>
                <p style="color: blue; font-weight: bold;"><b>Resource Allocation:</b> {assigned_dev_message}</p>
                <br>
                <a href="/">File Another Bug</a>
            </body>
        </html>
        """
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)