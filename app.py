from flask import Flask, jsonify,request, render_template
import requests
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
import json


load_dotenv()

app = Flask(__name__)

try:
    client = Cerebras(
        api_key=os.getenv("CEREBRAS_API_KEY"),
    )
except Exception as e:
    raise ValueError("Cerebras API key not found. Make sure it's set in your .env file.") from e

JUDGE0_API_URL = "http://localhost:2358"
LANGUAGE_CONFIG = {
    "python": {
        "id": 71,
        "prompt": "Write a complete and executable Python script that {prompt}. Provide only the raw code."
    },
    "java": {
        "id": 62,
        "prompt": "Write a complete Java program that {prompt}. The code must be in a public class named 'Main' with a `public static void main(String[] args)` method. Provide only the raw code."
    },
    "c++": {
        "id": 53,
        "prompt": "Write a complete C++ program that {prompt}. The code must be in a `main` function with necessary headers like `<iostream>`. Provide only the raw code."
    }
}

def create_prompt(language, user_prompt):
    """Creates a prompt that instructs the AI to return a JSON object."""
    
    json_structure_prompt = """
    {
      "language": "The programming language used",
      "code": "The script must be self-contained, complete, and ready to execute. The code must include any necessary imports or setup.",
      "explanation": "A brief, one-sentence explanation of the code"
    }
    """

    return (
        f"Based on the user's request to '{user_prompt}', "
        f"generate a complete and executable script in {language}. "
        f"You MUST respond with a single JSON object that strictly follows this structure: {json_structure_prompt}. "
        "Do not include any other text or markdown formatting outside of the JSON object."
    )


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/generate-and-run', methods=['POST'])
def generate_and_run():
    """The main endpoint to generate and run code."""
    data = request.get_json()
    user_prompt = data.get('prompt')
    language = data.get('language', 'python').lower()

    if not user_prompt:
        return jsonify({"error": "Prompt is missing"}), 400

    # Get language configuration in one step
    config = LANGUAGE_CONFIG.get(language)
    if not config:
        return jsonify({"error": f"Unsupported language: {language}"}), 400


    try:
        prompt_for_ai = config["prompt"].format(prompt=user_prompt)
        
        chat_completion = client.chat.completions.create(
            model="gpt-oss-120b",  # TODO: Support dynamic model selection based on user input or config.
            messages=[{"role": "user", "content": prompt_for_ai}],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.1
        )
        json_response = chat_completion.choices[0].message.content
        parsed_response= json.loads(json_response)
        code_to_run = parsed_response.get("code", "").strip()
        if not code_to_run:
            return jsonify({"error": "AI did not return any code."}), 500
        # testing 
        # print("Generated Code:\n", code_to_run)  

    except Exception as e:
        return jsonify({"error": "Failed to generate code via API", "details": str(e)}), 500

    payload = {
        "language_id": config["id"],
        "source_code": code_to_run
    }

    try:
        response = requests.post(f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true", json=payload)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to self-hosted Judge0 API", "details": str(e)}), 500

    return jsonify({
        "generated_code": code_to_run,
        "execution_result": result
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)