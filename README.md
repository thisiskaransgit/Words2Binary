# Words2Binary
Natural Language to Code Generator 🗣️➡️💻

## What is Words2Binary?

Words2Binary is a web application that lets you turn plain English instructions into real, working computer code. Just type what you want the computer to do (for example, "calculate the factorial of 5"), pick your favorite programming language (like Python, C++, or Java), and the app will generate the code and even run it for you—showing you the result instantly.

## How Does It Work?

1. **You enter a command** in simple English.
2. **The app uses powerful AI models** to understand your request and generate the correct code.
3. **The code is shown to you** on the website.
4. **The code is run automatically** on a secure server, and you see the output right away.

## Why is it Useful?

- **No coding experience needed:** Anyone can try out programming ideas without knowing how to code.
- **Quick prototyping:** Developers can save time by letting AI write and test code snippets.
- **Learning tool:** See how your ideas translate into real code and learn from the examples.

## What Tools and Technologies Are Used?

- **Flask:** A lightweight Python web framework that powers the backend of the app.
- **Cerebras AI Models:** Advanced artificial intelligence models that understand your instructions and generate code in different programming languages.
- **Judge0:** An open-source code execution engine that safely runs the generated code and returns the output.
- **HTML, CSS, JavaScript:** These are used to build the user-friendly web interface.
- **Docker & Docker Compose:** Used to run Judge0 and its dependencies in isolated containers for security and reliability.


## How to Use

1. Open the website.
2. Type your instruction in the box (for example: "sort a list of numbers").
3. Choose the programming language and AI model.
4. Click "Generate & Run".
5. See the generated code and its output instantly!

---


## Setting Up the Development Environment

Follow these steps to set up Words2Binary on your local machine:

### 1. Prerequisites

- **Python 3.8+** installed on your system
- **Docker** and **Docker Compose** installed
- **Git** (optional, for cloning the repository)

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/Words2Binary.git
cd Words2Binary
```

4. Install Python Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
6. go to judge0 directory and Start Judge0 container
```bash
cd jugge0-v1.13.1 && docker-compose up -d
```

This will start the Judge0 code execution engine in a secure container.

7. Run the Flask App
```bash
cd .. && flask run
```