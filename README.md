
# 🧠 SkillMate – AI-Powered Skill-Based Matchmaking Platform

SkillMate is a full-stack, real-time matchmaking and collaboration platform for students, developers, and tech enthusiasts. It uses **AI**, **vector similarity**, and **WebSockets** to connect people based on shared interests and tech stacks. Think of it as **Tinder for developers** — but smarter.

---

## 📌 Table of Contents

- [🔮 Overview](#-overview)
- [🛠 Tech Stack](#-tech-stack)
- [📂 Project Structure](#-project-structure)
- [⚙️ Backend Architecture](#-backend-architecture)
- [🎨 Frontend Functionality](#-frontend-functionality)
- [🤖 AI Assistant + Flowchart Generation](#-ai-assistant--flowchart-generation)
- [📈 User Embedding + Clustering](#-user-embedding--clustering)
- [🧪 Docker & Data Bootstrapping](#-docker--data-bootstrapping)
- [📦 .env Configuration](#-env-configuration)
- [🚀 Running the Project (Locally & Docker)](#-running-the-project-locally--docker)
- [🔧 CI/CD Ready](#-cicd-ready)
- [🛣 Roadmap](#-roadmap)
- [📬 Contact](#-contact)

---

## 🔮 Overview

SkillMate helps users find ideal tech partners based on:

- Tech stack similarity
- Year of study/experience
- AI-driven profile vector embeddings
- Realtime swipes, chats, and AI assistant

Built for:
- Hackathons
- Tech communities
- Learning buddies

---

## 🛠 Tech Stack

### ✅ Backend
- **Flask** + **Flask-SocketIO**
- **MongoDB Atlas**
- **Qdrant** (Vector Search DB)
- **Sentence Transformers**
- **Gemini API** (via Google AI)

### ✅ Frontend
- **React.js**
- **Tailwind CSS**
- **Socket.IO Client**
- **AI SDK for Flowcharts**

### ✅ DevOps
- **Docker & Docker Compose**
- **Python 3.11 Slim**
- **`uv` package manager** for fast, isolated builds

---

## 📂 Project Structure

```
skillmate/
├── app/
│   ├── ai/
│   ├── database/
│   ├── embeddings/
│   ├── sockets/
│   ├── utils/
│   └── __init__.py
├── assets/photos/
├── static/photos/
├── populate.py
├── main.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env
└── README.md
```

---

## ⚙️ Backend Architecture

- **WebSockets** for real-time communication
- **Qdrant** stores vector embeddings of user profiles
- **MongoDB** for storing:
  - Users
  - Swipes
  - Conversations
  - Messages

### Key Socket Events

- `find_skillmate`: Triggers vector search in Qdrant, filters swiped users
- `swipe`: Records like/dislike and checks for mutual match
- `match`: Emits matched profile to both users
- `join_chat`, `send_message`, `fetch_messages`: Handles chat room logic

---

## 🎨 Frontend Functionality

- Real-time swipe interface
- Photo carousel from dummy image seeds
- AI assistant toggle button
- AI responses and chat rendering
- Special SDK section for Flowchart rendering

---

## 🤖 AI Assistant + Flowchart Generation

### ✅ General AI Room

- Works like ChatGPT
- Chat history maintained (session-based)
- Uses `Gemini API` under the hood

### ✅ Special Mode – Flowchart

If user types:

```
MAKE FLOWCHART: How to build a MERN blog
```

→ AI returns code logic → Rendered in frontend using flowchart SDK

---

## 📈 User Embedding + Clustering

- `populate.py`:
  - Generates 1000+ fake users
  - Assigns photo, techstack, and name
  - Embeds profile using SentenceTransformer
  - Clusters embeddings with HDBSCAN + PCA + UMAP
  - Saves 2D plots of clusters in `./plots/`

---

## 🧪 Docker & Data Bootstrapping

### Dockerized services:
- `backend`: Flask + SocketIO app
- `mongo`: MongoDB database
- `qdrant`: Vector DB engine

### Bootstrap Data

On first build, the `populate.py` script:
- Seeds dummy users
- Uploads their vectors to Qdrant
- Clusters and visualizes results

---

## 📦 .env Configuration

```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/skillmate
MONGO_DB=skillmate
SECRET_KEY=supersecretkey123

MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key

QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

---

## 🚀 Running the Project (Locally & Docker)

### ▶️ Locally

```bash
pip install -r requirements.txt
python populate.py
python main.py
```

### 🐳 Docker

```bash
docker-compose build
docker-compose up
```

Flask app will be available at `localhost:5000`.

---

## 🔧 CI/CD Ready

You can add GitHub Actions to:

- Rebuild image on push
- Run backend tests
- Lint Python code
- (Optional) Deploy to Render, Railway, or self-hosted VPS

---

## 🛣 Roadmap

- [x] Basic vector-based matching
- [x] Dummy image & photo handling
- [x] Real-time WebSocket chat
- [x] AI Assistant + Gemini API
- [x] Flowchart generation support
- [x] Dockerized + seeding support
- [ ] Auth + JWT
- [ ] OAuth login (GitHub/Google)
- [ ] Save AI conversations to DB
- [ ] Team formation and scoring
- [ ] Fully responsive frontend

---

## 📬 Contact

- ✉️ Email: `hari@gmail.com`
- 💬 Raise an [issue](https://github.com/yourusername/skillmate/issues)
- 🤝 Contributions welcome via PR

---

> ⚡ Built with passion to connect developers, by developers.
