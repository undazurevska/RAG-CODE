# RAG-powered Slackbot

A Slackbot powered by Retrieval-Augmented Generation (RAG) that connects with Confluence. Users can ask questions in Slack and get answers sourced from internal Confluence pages.

## Features

- **Slash command**: `/askrag`
- **Retrieves and embeds Confluence pages**
- **Uses local LLM**: Powered by Ollama (LLaMA2)
- **Asynchronous responses**: Responds to users in Slack while processing in the background

---

## Setup Instructions

### 1. Clone the repo

### 2. Set up .env
    SLACK_BOT_TOKEN=xoxb-your-token
    SLACK_SIGNING_SECRET=your-signing-secret
    CONFLUENCE_BASE_URL=https://yourdomain.atlassian.net/wiki
    CONFLUENCE_USERNAME=your@email.com
    CONFLUENCE_API_TOKEN=your-api-token

### 3. Run Setup Script
chmod +x start.sh
./start.sh

### 4. Expose to Slack via ngrok
    ngrok http 3000
    // update Slack App’s slash command or event URL with the HTTPS tunnel link.
    // Slack app -> Event Subscriptions -> Request URL
    // Slash Commands

## File Description

backend/app.py
The main Flask application that handles Slack commands and events. It integrates with the RAG pipeline to process user questions and respond in Slack.

backend/confluence_client.py
Handles interactions with the Confluence API, including fetching page content and retrieving page IDs from a specific space.

backend/rag_chain.py
Builds the RAG pipeline, which combines document embeddings and a local LLM to generate answers.

backend/embedder.py
Processes and embeds Confluence page content for use in the RAG pipeline.

requirements.txt
Lists all Python dependencies required to run the project.