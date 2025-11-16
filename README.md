# 🎓 Powerpuff College Chatbot  
### *A Role-Specific GenAI Assistant for Colleges*  
> Built by **The Powerpuff Girls** 💖 — empowering education through AI!  

---

## 🚀 Overview

The **Powerpuff College Chatbot** is a **GenAI-powered RAG-based assistant** designed to deliver **role-specific insights** across a college ecosystem.  
Each user — whether **Student, Parent, Professor, or Dean** — gets personalized access to relevant information, securely filtered by their role.  

---

## 🎯 Core Features

- 🔐 **Role-Based Authentication**
  - Secure login and signup using MySQL database  
  - Each user is assigned one of four roles: `student`, `parent`, `professor`, or `dean`

- 🧠 **Retrieval-Augmented Generation (RAG)**
  - Queries are enhanced using context from stored college documents  
  - Ensures accurate, context-aware, and role-specific responses  

- 🏫 **Role-Specific Access**
  - 🎓 Students: syllabus, exams, placements, events  
  - 👨‍👩‍👧 Parents: college overview, placements, fees, and courses  
  - 👩‍🏫 Professors: academic policies, events, evaluations  
  - 🎓 Dean: aggregated analytics, performance data, and planning  

- 💬 **Interactive Chat Interface**
  - Built using **Streamlit** with a modern, responsive UI  
  - Personalized quick prompts for each role  
  - Live AI-generated responses with chat history  

- 🗂️ **Vector Database**
  - Documents are embedded using **Sentence Transformers**  
  - Stored and retrieved via **ChromaDB**, filtered by role metadata  

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-------------|
| 💻 Frontend | Streamlit |
| 🧠 LLM | Kimi K2 via Groq |
| 🗃️ Vector Store | ChromaDB |
| 🧩 Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| 🧾 Relational Database | MySQL |
| 🔒 Authentication | Role-Based Access Control (RBAC) |

---

## ⚡ Project Workflow

1. **User Login & Role Detection**  
   → Authentication and session management  

2. **Role-Based Document Access**  
   → Fetch only the content that the role is authorized for  

3. **Query Handling via RAG**  
   → Retrieve relevant vector data based on the query  

4. **LLM Response Generation**  
   → Context + Query → AI-generated answer  

5. **Response Delivery**  
   → Displayed in chat UI, with persistent history  

---

## 🧩 Example Role-Specific Interactions

| Role | Sample Query | Example Response |
|------|---------------|------------------|
| 👩‍🎓 Student | “Show my exam schedule.” | Returns student’s exam timetable |
| 👨‍👩‍👧 Parent | “What's the fee structure” | Reurns the fee structure |
| 👩‍🏫 Professor | “Show the leave policy” | Returns the leave policy |
| 🎓 Dean | “show me the strategic planning” | Displays the plan |

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.3+
- MySQL installed and running

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/RevathiS2025/powerpuff_college_chatbot.git
cd powerpuff_college_chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (create .env)
MYSQL_HOST=localhost
MYSQL_DATABASE=powerpuff_college
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
GROQ_API_KEY=your_api_key_here

# 5. Ingest documents
python backend/document_ingest.py

# 6. Run the app
streamlit run app/main.py

```
## 💡 Future Enhancements

1. 📊 Integration with college APIs for real-time data
2. 🎙️ Voice-based assistant for accessibility
3. 📱 Mobile-responsive UI
4. 🧾 Analytics dashboard for deans

---

## 🔗 Live Link

👉 [powerpuffchatbot.streamlit.app](https://powerpuffchatbot.streamlit.app/)

---

## 👩‍💻 Team Members

- **Pavithra A** – [LinkedIn](https://www.linkedin.com/in/pavithraakkaraju/)
- **Revathi S** – [LinkedIn](https://www.linkedin.com/in/revathis2024/)  
- **Dhanashree S R** – [LinkedIn](https://www.linkedin.com/in/dhanashreesr/)  

---

## 🤝 Contributions & Feedback

This is a community-inspired project. We welcome feedback, issues, and pull requests.  
Feel free to open an issue or connect with us on LinkedIn.

---
