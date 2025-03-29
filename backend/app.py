from flask import Flask, request, jsonify
import os
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv
from backend.rag_chain import build_rag_chain
from backend.confluence_client import get_all_page_ids, get_page_content
from backend.embedder import embed_documents
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Slack client and verifier
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
verifier = SignatureVerifier(os.getenv("SLACK_SIGNING_SECRET"))

# Prepare RAG pipeline
print("⚙️ Preparing RAG pipeline...")
page_ids = get_all_page_ids("SD")
pages = [get_page_content(pid) for pid in page_ids]
embeddings, docs = embed_documents(pages)
qa = build_rag_chain(docs)
print("✅ RAG ready.")

@app.route("/slack/commands", methods=["POST"])
def handle_slash_command():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 403

    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    question = data.get("text", "What can you do?")

    # Notify user that the bot is processing the question
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=f"⏳ Thinking about: *{question}*"
    )

    def process_answer():
        try:
            answer = qa.invoke(question)
            if isinstance(answer, dict) and "result" in answer:
                answer = answer["result"]
            client.chat_postEphemeral(channel=channel_id, user=user_id, text=answer)
        except Exception as e:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="❌ Something went wrong while generating the answer."
            )

    # Run the answer processing in a separate thread
    threading.Thread(target=process_answer).start()
    return "", 200

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 403

    data = request.get_json()

    # Handle URL verification challenge
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    # Handle app mentions
    if "event" in data:
        event = data["event"]
        if event.get("type") == "app_mention":
            user = event["user"]
            channel = event["channel"]
            text = event["text"]
            question = text.split(">")[-1].strip()

            # Generate an answer using the RAG pipeline
            answer = qa.invoke(question)
            if isinstance(answer, dict) and "result" in answer:
                answer = answer["result"]
            client.chat_postMessage(channel=channel, text=answer)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Run the Flask app on port 3000
    app.run(port=3000)
