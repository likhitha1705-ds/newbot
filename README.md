# 📰 NewsMate AI — Real-Time News Chatbot

A modern conversational AI chatbot that fetches and displays **live news from India** using [NewsAPI](https://newsapi.org/), built with **Python + Streamlit**.

---

## 🚀 Features

| Feature | Details |
|---|---|
| 🔴 Real-Time News | Fetches current top headlines from India via NewsAPI |
| 📂 6 Categories | General, Technology, Sports, Business, Health, Entertainment |
| 🤖 AI Summaries | Auto-summarizes each article in 2–3 lines |
| 🔍 Search | Search any topic — e.g. `search AI news` |
| 📖 Explain More | Type `explain more` for a detailed breakdown |
| ⭐ Favorites | Save your preferred news category |
| 🌙 Dark/Light Mode | Toggle from the sidebar |
| 🔄 Refresh | One-click refresh for the latest news |
| 💡 Quick Commands | Sidebar shortcut buttons for common queries |

---

## 🛠️ Setup Instructions

### 1. Clone / Download the project

```bash
cd Desktop/newsbot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your FREE NewsAPI key

1. Go to [https://newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key from the dashboard

### 5. Add your API key

Open `app.py` and replace line 6:

```python
NEWS_API_KEY = "YOUR_NEWS_API_KEY"   # ← paste your key here
```

### 6. Run the chatbot

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## 💬 Supported Commands

| Command | Action |
|---|---|
| `latest news` | Fetch current top headlines |
| `tech news` / `sports news` | Fetch category-specific news |
| `category: business` | Switch to a specific category |
| `search AI news` | Search any keyword |
| `explain more` | Detailed explanation of last article |
| `my favorite news` | Load your saved favorite category |
| `change category` | Instructions to switch category |

---

## 📁 Project Structure

```
newsbot/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## ⚠️ Notes

- The **free NewsAPI plan** only supports `top-headlines` for country-based queries.
- The `/everything` endpoint (used for search) requires an active internet connection.
- API rate limit on the free plan: **100 requests/day**.

---

## 🎓 Built With

- [Streamlit](https://streamlit.io/) — Frontend UI
- [NewsAPI](https://newsapi.org/) — Live news data
- [Requests](https://docs.python-requests.org/) — HTTP calls
- Python 3.8+
