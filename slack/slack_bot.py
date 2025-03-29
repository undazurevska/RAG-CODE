from flask import Flask, request, jsonify
import os
import threading
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from rag_chain import build_rag_chain
from confluence_client import get_all_page_ids, get_page_content
from embedder import embed_documents

# Load environment variables
load_dotenv()

# Slack API configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Slack client and verifier
client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# Initialize Flask app
app = Flask(__name__)

# Initialize RAG pipeline
print("⚙️ Preparing RAG pipeline...")
page_ids = get_all_page_ids("SD")
pages = [get_page_content(pid) for pid in page_ids]
embeddings, docs = embed_documents(pages)
qa = build_rag_chain(docs)
print("✅ RAG ready.")

@app.route("/slack/commands", methods=["POST"])
def handle_slash_command():
    """
    Handle Slack slash commands.
    """
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 403

    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    question = data.get("text", "What can you do?")

    print(f"❓ Slash command from {user_id}: {question}")

    # Notify the user that the bot is processing the question
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=f"⏳ Thinking about: *{question}*"
    )

    # Process the answer in a background thread
    def process_answer():
        try:
            answer = qa.invoke(question)

            # Ensure the answer is a string
            if isinstance(answer, dict) and "result" in answer:
                answer = answer["result"]

            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=answer
            )
        except Exception as e:
            print("⚠️ Async error:", e)
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="❌ Something went wrong while generating the answer."
            )

    threading.Thread(target=process_answer).start()

    # Return a fast 200 OK to Slack
    return "", 200

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Handle Slack events.
    """
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 403

    data = request.get_json()

    # Respond to Slack's URL verification challenge
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
            print(f"❓ {user} asked: {question}")
            answer = qa.invoke(question)
            client.chat_postMessage(channel=channel, text=answer)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=3000)
