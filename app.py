from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb+srv://admin:Harsha@0309cluster0.zyctgrk.mongodb.net/?appName=Cluster0")
db = client["github_events"]
collection = db["events"]


@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/webhook", methods=["POST"])
def github_webhook():
    payload = request.json
    event = request.headers.get("X-GitHub-Event")

    if event == "push":
        data = {
            "request_id": payload["after"],
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": payload["ref"].split("/")[-1],
            "timestamp": datetime.utcnow()
        }

    elif event == "pull_request":
        pr = payload["pull_request"]
        data = {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "PULL_REQUEST",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.utcnow()
        }

    else:
        return jsonify({"msg": "ignored"}), 200

    collection.insert_one(data)
    return jsonify({"msg": "saved"}), 200

@app.route("/events")
def get_events():
    events = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))
    return jsonify(events)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
