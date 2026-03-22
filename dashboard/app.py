# app.py
from flask import Flask, render_template, jsonify
import json
from config import USERS_JSON, LEADS_JSON, MESSAGES_JSON, LOGS_JSON

app = Flask(__name__)

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@app.route("/")
def index():
    users = load_json(USERS_JSON)
    leads = load_json(LEADS_JSON)
    messages = load_json(MESSAGES_JSON)
    logs = load_json(LOGS_JSON)
    return render_template("dashboard.html", users=users, leads=leads, messages=messages, logs=logs)

@app.route("/api/users")
def api_users():
    return jsonify(load_json(USERS_JSON))

@app.route("/api/leads")
def api_leads():
    return jsonify(load_json(LEADS_JSON))

if __name__ == "__main__":
    app.run(port=5000, debug=True)