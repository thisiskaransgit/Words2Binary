from flask import Flask, request, jsonify, render_template
import requests
import os
import re
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

app = Flask(__name__)


try:
    cerebras = Cerebras(
        api_key=os.environ.get("CEREBRAS_API_KEY")
    ) 
except Exception as e:
    raise ValueError("Cerebras API key not found. Make sure it's set in your .env file.") from e

JUDGE0_API_URL = "http://localhost:2358"


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

def extract_code(text):
    """Extracts code from a markdown block."""
    code_block = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()
    if text.strip().startswith("def ") or text.strip().startswith("import ") or text.strip().startswith("print("):
        return text.strip()
    return text

@app.route('/generate-and-run', methods=['POST'])
def generate_and_run():
    """The main endpoint to generate and run code."""
    user_prompt = request.json.get('prompt')
    if not user_prompt:
        return jsonify({"error": "Prompt is missing"}), 400

    prompt_for_ai = (
        f"Write a complete and executable Python 3 script that {user_prompt}. "
        "The script must be self-contained. Do not include any explanation or introductory text, only the raw code."
    )
    
    try:
        response = cerebras.chat.completions.create(
            model="gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_for_ai}],
            max_tokens=500,
            temperature=0.1
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": "Failed to generate code via Cerebras SDK", "details": str(e)}), 500

    code_to_run = extract_code(generated_text)

    headers_judge0 = {"Content-Type": "application/json"}
    payload_judge0 = {
        "language_id": 71, 
        "source_code": code_to_run
    }

    try:
        submit_response = requests.post(f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true", json=payload_judge0, headers=headers_judge0)
        submit_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to self-hosted Judge0 API.", "details": str(e)}), 500

    execution_result = submit_response.json()

    return jsonify({
        "generated_code": code_to_run,
        "execution_result": execution_result
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)