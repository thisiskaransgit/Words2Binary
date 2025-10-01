import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Define the direct URLs for our services
JUDGE0_URL = "http://localhost:2358"
CEREBRAS_API_URL = "https://api.cerebras.net/v1/chat/completions"

# It's best practice to get the API key from an environment variable
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

@app.route("/generate", methods=["POST"])
def generate_code():
    if not CEREBRAS_API_KEY:
        return jsonify({"error": "CEREBRAS_API_KEY environment variable not set."}), 500
        
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is missing"}), 400

    try:
        # STEP 1: Call the Cerebras LLM API directly
        print("--> Calling Cerebras API directly...")
        llm_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CEREBRAS_API_KEY}"
        }
        llm_payload = {
            "model": "BTLM-3B-8K-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        llm_response = requests.post(CEREBRAS_API_URL, headers=llm_headers, json=llm_payload)
        llm_response.raise_for_status()
        generated_code = llm_response.json()["choices"][0]["message"]["content"]
        print("<-- Cerebras API call successful.")

        # STEP 2: Call Judge0 API directly
        print("--> Calling Judge0 API directly...")
        judge0_payload = {
            "language_id": 71,  # 71 is for Python
            "source_code": generated_code
        }
        judge0_response = requests.post(f"{JUDGE0_URL}/submissions?wait=true", json=judge0_payload)
        judge0_response.raise_for_status()
        execution_result = judge0_response.json()
        print("<-- Judge0 API call successful.")
        
        # STEP 3: Return the combined result
        return jsonify({
            "generated_code": generated_code,
            "execution_result": execution_result
        })

    except requests.exceptions.RequestException as e:
        print(f"!!! API Error: {e}")
        return jsonify({"error": f"An API error occurred: {e}"}), 500
    except Exception as e:
        print(f"!!! General Error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)