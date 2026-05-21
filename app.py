from flask import Flask, request, render_template, jsonify
from src.pipeline.prediction_pipeline import PredictPipeline

app = Flask(__name__)
pipeline = PredictPipeline()

@app.route('/')
def index():
    # Simple form interface (Create an index.html template or use basic text inputs)
    return """
    <html>
        <head><title>Bug Triage Engine</title></head>
        <body style="font-family: Arial; margin: 40px;">
            <h2>Bug Severity Classification System</h2>
            <form action="/predict" method="post" style="display: flex; flex-direction: column; width: 400px; gap: 15px;">
                <label><b>Bug Summary (Headline):</b></label>
                <input type="text" name="summary" placeholder="e.g., App crashes on startup" required style="padding: 8px;">
                
                <label><b>Bug Description (Logs / Steps):</b></label>
                <textarea name="description" rows="6" placeholder="e.g., NullPointerException at MainActivity.java line 43..." required style="padding: 8px;"></textarea>
                
                <button type="submit" style="padding: 10px; background-color: #007bff; color: white; border: none; cursor: pointer;">Analyze Severity</button>
            </form>
        </body>
    </html>
    """

@app.route('/predict', methods=['POST'])
def predict_datapoint():
    try:
        summary = request.form.get('summary')
        description = request.form.get('description')

        result = pipeline.predict(summary, description)

        text_color = "green" if result["status"] == "Automated" else "orange"

        return f"""
        <html>
            <body style="font-family: Arial; margin: 40px; line-height: 1.6;">
                <h2>Analysis Result</h2>
                <p><b>Summary:</b> {summary}</p>
                <p><b>System Routing Status:</b> <span style="color: {text_color}; font-weight: bold;">{result["status"]}</span></p>
                <p><b>Model Confidence Score:</b> {result["confidence"]}</p>
                <p><b>Assigned Class/Action:</b> <span style="font-weight: bold;">{result["severity"]}</span></p>
                <br>
                <a href="/">Go Back</a>
            </body>
        </html>
        """
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)