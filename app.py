import streamlit as st
import requests
from datetime import datetime
import time

# ── Config ─────────────────────────────────────────────────────────────────────
NEWS_API_KEY = "896a6179a44247c3b02b0f710e3af7e4"
GEMINI_URL   = ("https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-2.0-flash:generateContent?key=AIzaSyAIZL2r2jBRLxdBtWs3kAkH-74G4lkVMuA")
SEARCH_URL   = "https://newsapi.org/v2/everything"
HEADLINES_URL = "https://newsapi.org/v2/top-headlines"

CATEGORIES  = ["general","technology","sports","business","health","entertainment"]
CAT_ICONS   = {"general":"🌐","technology":"💻","sports":"⚽","business":"💼","health":"🏥","entertainment":"🎬"}
CAT_QUERIES = {
    "general":       "India news today",
    "technology":    "India technology tech news",
    "sports":        "India sports cricket news",
    "business":      "India business economy finance",
    "health":        "India health medical news",
    "entertainment": "India entertainment celebrity movies",
}
CAT_ALIASES = {
    "tech":"technology","sport":"sports","finance":"business","economy":"business",
    "medical":"health","movies":"entertainment","cinema":"entertainment",
}
INDIAN_STATES = [
    "andhra pradesh","arunachal pradesh","assam","bihar","chhattisgarh","goa",
    "gujarat","haryana","himachal pradesh","jharkhand","karnataka","kerala",
    "madhya pradesh","maharashtra","manipur","meghalaya","mizoram","nagaland",
    "odisha","punjab","rajasthan","sikkim","tamil nadu","telangana","tripura",
    "uttar pradesh","uttarakhand","west bengal","delhi","jammu","kashmir",
    "ladakh","puducherry","chandigarh","mumbai","bangalore","bengaluru",
    "chennai","hyderabad","kolkata","pune","ahmedabad","jaipur","lucknow",
    "patna","bhopal","bhubaneswar",
]

st.set_page_config(page_title="NewsMate AI", page_icon="📰", layout="wide")

for k, v in {
    "messages":[], "category":"general", "state":"All India",
    "dark":False, "fetched":None, "articles":[],
    "last_intent":None, "last_query":None, "context_label":"",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme ──────────────────────────────────────────────────────────────────────
D      = st.session_state.dark
BG     = "#0d0d1a" if D else "#f0f4f8"
CARD   = "#1a1a2e" if D else "#ffffff"
SB     = "#13132a" if D else "#ffffff"
TXT    = "#e2e8f0" if D else "#1e293b"
STXT   = "#94a3b8" if D else "#64748b"
BORDER = "#2d3748" if D else "#e2e8f0"
ACCENT = "#4f8ef7"
RPANEL = "#16213e" if D else "#f8fafc"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family:'Inter',sans-serif; box-sizing:border-box; margin:0; padding:0; }}
.stApp {{ background:{BG}; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] > div {{
    background:{SB}; border-right:1px solid {BORDER}; padding:0 !important;
}}
.sb-head {{
    padding:22px 18px 14px; border-bottom:1px solid {BORDER};
}}
.sb-head h2 {{
    font-size:1.25rem; font-weight:700; margin:0;
    background:linear-gradient(135deg,#4f8ef7,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.sb-head p {{ color:{STXT}; font-size:0.72rem; margin:3px 0 0; }}
.sb-lbl {{
    font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
    text-transform:uppercase; color:{STXT}; margin:14px 0 6px;
}}

/* ── Header ── */
.nm-hdr {{
    text-align:center; padding:22px 0 14px;
    border-bottom:1px solid {BORDER}; margin-bottom:0;
}}
.nm-hdr h1 {{
    font-size:1.9rem; font-weight:700; margin:0;
    background:linear-gradient(135deg,#4f8ef7,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.nm-hdr p {{ color:{STXT}; font-size:0.85rem; margin:4px 0 0; }}

/* ── Chat ── */
.chat-wrap {{
    height:500px; overflow-y:auto; padding:14px 6px;
    display:flex; flex-direction:column; gap:10px;
    scrollbar-width:thin; scrollbar-color:{BORDER} transparent;
    scroll-behavior:smooth;
}}
.chat-wrap::-webkit-scrollbar {{ width:5px; }}
.chat-wrap::-webkit-scrollbar-track {{ background:transparent; }}
.chat-wrap::-webkit-scrollbar-thumb {{ background:{BORDER}; border-radius:10px; }}
.row-user {{ display:flex; justify-content:flex-end; align-items:flex-end; gap:7px; }}
.row-bot  {{ display:flex; justify-content:flex-start; align-items:flex-end; gap:7px; }}
.av {{
    width:32px; height:32px; border-radius:50%; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:0.9rem;
}}
.av-bot  {{ background:linear-gradient(135deg,#4f8ef7,#a78bfa); }}
.av-user {{ background:linear-gradient(135deg,#f97316,#ef4444); }}
.bub-user {{
    background:linear-gradient(135deg,#4f8ef7,#6366f1);
    color:#fff; border-radius:18px 18px 4px 18px;
    padding:11px 15px; max-width:65%; font-size:0.9rem; line-height:1.5;
    box-shadow:0 2px 8px rgba(79,142,247,0.25); word-wrap:break-word;
}}
.bub-bot {{
    background:{CARD}; color:{TXT}; border:1px solid {BORDER};
    border-radius:18px 18px 18px 4px;
    padding:13px 16px; max-width:88%; font-size:0.9rem; line-height:1.6;
    box-shadow:0 2px 8px rgba(0,0,0,0.07); word-wrap:break-word;
    overflow-x:hidden;
}}

/* ── Right panel news card ── */
.rp-wrap {{
    background:{RPANEL}; border:1px solid {BORDER};
    border-radius:14px; padding:14px; height:560px;
    overflow-y:auto; scrollbar-width:thin; scrollbar-color:{BORDER} transparent;
}}
.rp-title {{
    font-size:0.78rem; font-weight:700; letter-spacing:0.08em;
    text-transform:uppercase; color:{STXT}; margin-bottom:12px;
    padding-bottom:8px; border-bottom:1px solid {BORDER};
}}
.rcard {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
    padding:11px 13px; margin-bottom:10px; border-left:3px solid {ACCENT};
    transition:transform 0.15s;
}}
.rcard:hover {{ transform:translateX(2px); }}
.rcard-num {{
    font-size:0.68rem; font-weight:700; color:{ACCENT};
    text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;
}}
.rcard-t {{ font-weight:600; font-size:0.85rem; color:{TXT}; line-height:1.4; margin-bottom:5px; }}
.rcard-src {{ font-size:0.72rem; color:{STXT}; }}
.rcard-src a {{ color:{ACCENT}; text-decoration:none; }}

/* ── Chat news card ── */
.ncard {{
    background:{BG}; border:1px solid {BORDER}; border-radius:10px;
    padding:11px 13px; margin:7px 0; border-left:3px solid {ACCENT};
    width:100%; box-sizing:border-box;
}}
.ncard-t {{ font-weight:600; font-size:0.88rem; color:{TXT}; margin-bottom:4px; line-height:1.4; }}
.ncard-d {{ font-size:0.81rem; color:{STXT}; line-height:1.5; }}
.ncard-m {{ font-size:0.71rem; color:{STXT}; margin-top:7px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
.ncard-m a {{ color:{ACCENT}; text-decoration:none; }}
.ncard-m a:hover {{ text-decoration:underline; }}

/* ── Input form ── */
div[data-testid="stForm"] {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
    padding:5px 5px 5px 14px; box-shadow:0 2px 10px rgba(0,0,0,0.07);
    margin-top:12px;
}}
.stTextInput > div > div > input {{
    background:transparent !important; border:none !important;
    color:{TXT} !important; font-size:0.92rem !important; box-shadow:none !important;
}}
.stTextInput > div {{ border:none !important; box-shadow:none !important; }}
.stFormSubmitButton > button {{
    background:linear-gradient(135deg,#4f8ef7,#6366f1) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; padding:8px 18px !important;
}}
.stFormSubmitButton > button:hover {{
    background:linear-gradient(135deg,#6366f1,#4f8ef7) !important;
}}

/* ── Streamlit overrides ── */
div[data-testid="stSelectbox"] > div > div {{
    background:{BG} !important; border-color:{BORDER} !important;
    color:{TXT} !important; border-radius:8px !important;
}}
.stButton > button {{
    border-radius:8px !important; font-size:0.82rem !important;
    font-weight:500 !important; border:1px solid {BORDER} !important;
    background:{BG} !important; color:{TXT} !important; transition:all 0.2s !important;
}}
.stButton > button:hover {{
    background:{ACCENT} !important; color:#fff !important; border-color:{ACCENT} !important;
}}
hr {{ border-color:{BORDER} !important; margin:10px 0 !important; }}
.stCaption {{ color:{STXT} !important; font-size:0.72rem !important; }}
</style>
""", unsafe_allow_html=True)

# --- Clean ChatGPT-Style Layout CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}

/* Hide Streamlit Header & Padding */
header[data-testid="stHeader"] {{ visibility: hidden; }}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 120px; max-width: 95%; }}

/* Fix background */
.stApp {{ background: {BG}; }}

/* Fixed Input Bar at Bottom - Centered in Content Area */
div[data-testid="stForm"] {{
    position: fixed;
    bottom: 30px;
    left: 45%; /* Slightly right to account for sidebar */
    transform: translateX(-50%);
    width: 50%;
    max-width: 750px;
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
    z-index: 1001;
    padding: 10px 20px !important;
}}

/* For smaller screens, adjust centering */
@media (max-width: 1200px) {{
    div[data-testid="stForm"] {{ width: 70%; left: 50%; }}
}}
@media (max-width: 800px) {{
    div[data-testid="stForm"] {{ width: 90%; left: 50%; bottom: 10px; }}
}}

/* Chat Bubble Layout - Centered */
.chat-container-wrap {{
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
}}

/* Chat Bubble Styles */
.row-user, .row-bot {{
    display: flex;
    gap: 12px;
    margin-bottom: 15px;
    padding: 10px;
    width: 100%;
}}
.row-user {{ justify-content: flex-end; }}
.bub-user {{
    background: {ACCENT};
    color: white;
    border-radius: 15px 15px 2px 15px;
    padding: 10px 15px;
    max-width: 80%;
    font-size: 0.9rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}
.bub-bot {{
    background: {CARD};
    color: {TXT};
    border: 1px solid {BORDER};
    border-radius: 15px 15px 15px 2px;
    padding: 12px 18px;
    max-width: 90%;
    font-size: 0.9rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}}
.av {{
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}}
.av-bot {{ background: linear-gradient(135deg, #4f8ef7, #a78bfa); }}
.av-user {{ background: #f97316; }}

/* News Card Styles */
.rcard {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: transform 0.2s;
}}
.rcard:hover {{ transform: scale(1.02); border-color: {ACCENT}; }}
.rcard-t {{ font-weight: 600; font-size: 0.85rem; color: {TXT}; margin-bottom: 5px; }}
.rcard-src {{ font-size: 0.7rem; color: {STXT}; }}

/* Form Styling */
div[data-testid="stForm"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 15px !important;
    background: {CARD} !important;
    padding: 5px 15px !important;
    margin-top: 10px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def fetch_by_category(category="general"):
    """Use top-headlines for pure category queries (more relevant)."""
    try:
        resp = requests.get(HEADLINES_URL, params={
            "country":"in", "category":category,
            "pageSize":5, "apiKey":NEWS_API_KEY,
        }, timeout=10)
        data = resp.json()
        arts = [a for a in data.get("articles",[])
                if a.get("title") and a["title"] != "[Removed]"]
        # fallback to /everything if top-headlines returns nothing
        if data.get("status") == "ok" and arts:
            return arts, None
        return fetch_by_search(CAT_QUERIES.get(category, "India news"))
    except Exception:
        return fetch_by_search(CAT_QUERIES.get(category, "India news"))

def fetch_by_search(query):
    """Use /everything for location, keyword, or custom queries."""
    try:
        resp = requests.get(SEARCH_URL, params={
            "q":query, "language":"en", "sortBy":"publishedAt",
            "pageSize":5, "apiKey":NEWS_API_KEY,
        }, timeout=10)
        data = resp.json()
        if data.get("status") == "ok":
            return [a for a in data.get("articles",[])
                    if a.get("title") and a["title"] != "[Removed]"], None
        return [], data.get("message","API error.")
    except requests.exceptions.ConnectionError:
        return [], "🌐 Network error — check your internet."
    except requests.exceptions.Timeout:
        return [], "⏱️ Request timed out."
    except Exception as e:
        return [], str(e)

def fmt_time(s):
    try:
        return datetime.strptime(s,"%Y-%m-%dT%H:%M:%SZ").strftime("%d %b, %I:%M %p")
    except Exception:
        return s or "—"

def gemini(prompt):
    try:
        r = requests.post(GEMINI_URL,
                          json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=12)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return ""

def gemini_intent(user_input):
    """
    Ask Gemini to classify the user intent and extract key info.
    Includes context from session state for follow-ups.
    """
    context = ""
    if st.session_state.messages:
        # Get last few messages for context
        last_msgs = st.session_state.messages[-3:]
        context = "Conversation context:\n"
        for m in last_msgs:
            role = "User" if m["role"] == "user" else "Assistant"
            context += f"{role}: {m['content'][:200]}\n"

    prompt = f"""You are an intent classifier for a news chatbot about India.
{context}

Analyze this new user message: "{user_input}"

Classify into ONE of these types:
- category   → user wants news by category (technology/sports/business/health/entertainment/general)
- location   → user mentions a city, state, or region in India
- keyword    → user wants news about a specific topic/keyword
- explain    → user wants explanation or more details about the previous news shown
- greeting   → hello, hi, how are you etc.
- unknown    → cannot determine

Respond ONLY in this exact JSON format:
{{"type":"category","value":"technology","category":"technology","conversational":"Here are the latest tech news updates from India!"}}

Rules:
- If the user says "Explain more" or "Tell me more about this", set type to "explain".
- For location: value = the location name (e.g. "Bengaluru", "Kerala")
- For category: value = one of [general,technology,sports,business,health,entertainment]
- For keyword: value = the search keyword (e.g. "AI", "IPL")
- conversational = a friendly 1-line intro sentence.
- If it's a follow-up about a previous location, maintain that location in the value."""

    result = gemini(prompt)
    try:
        import json, re
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return None

def get_desc(a):
    d = a.get("description") or a.get("content") or ""
    return (d[:240].rsplit(" ",1)[0]+"...") if len(d)>240 else d or "No description."

def chat_cards(articles, label, icon="📰"):
    html = f"<div style='font-weight:600;font-size:0.95rem;color:{TXT};margin-bottom:10px;'>{icon} <span style='color:{ACCENT}'>{label}</span> — Latest News</div>"
    for i, a in enumerate(articles, 1):
        html += f"""
        <div class='ncard'>
            <div class='ncard-t'>{i}. {a.get('title','No title')}</div>
            <div class='ncard-d'>{get_desc(a)}</div>
            <div class='ncard-m'>
                <span>📡 {a.get('source',{}).get('name','Unknown')}</span>
                <span>🕒 {fmt_time(a.get('publishedAt',''))}</span>
                <a href='{a.get('url','#')}' target='_blank'>🔗 Read more</a>
            </div>
        </div>"""
    return html


# ── Parser (rule-based fast path, Gemini as fallback) ─────────────────────────
def parse(text):
    t = text.lower().strip()
    # strip trailing noise words to get clean subject
    t_clean = t
    for suffix in [" news", " update", " updates", " headlines", " latest"]:
        t_clean = t_clean.replace(suffix, "")
    t_clean = t_clean.strip()
    words = t_clean.split()

    # ── Hard commands ──
    if t.startswith("search "): return "search", text[7:].strip()
    if any(p in t for p in ["explain more", "tell me more", "elaborate", "explain this"]):
        return "explain", None
    if t.startswith("category:"):
        c = t.split(":", 1)[1].strip()
        if c in CATEGORIES: return "category", c
    if any(g in t for g in ["hello", "hi ", "hey ", "good morning", "good evening",
                             "how are you", "what's up", "sup "]):
        return "greeting", None
    if any(p in t for p in ["show more", "more news", "load more", "next news", "latest updates", "show latest updates"]):
        return "more", None

    # ── Location detection ──
    # Sort longest first so multi-word states match before single words
    detected_cat = "general"
    detected_loc = None
    for state in sorted(INDIAN_STATES, key=len, reverse=True):
        # match against both full text and cleaned text
        if state in t or state in t_clean:
            detected_loc = state.title()
            # also check if a category word appears alongside
            for w, c in CAT_ALIASES.items():
                if w in words: detected_cat = c; break
            for c in CATEGORIES:
                if c in words: detected_cat = c; break
            break
    if detected_loc:
        return "location", {"location": detected_loc, "category": detected_cat}

    # ── Category detection ──
    for w, c in CAT_ALIASES.items():
        if w in words or f"{w} news" in t:
            return "category", c
    for c in CATEGORIES:
        if c in words or t_clean == c:
            return "category", c

    # ── Generic news ──
    if any(w in t for w in ["news", "headlines", "latest", "current", "today", "update"]):
        return "news", st.session_state.category

    # ── Fallback → Gemini ──
    return "gemini", text

# ── Respond ────────────────────────────────────────────────────────────────────
def respond(user_input):
    intent, payload = parse(user_input)

    # ── Search (explicit) ──
    if intent == "search":
        with st.spinner("🔍 Searching..."):
            arts, err = fetch_by_search(payload)
        if err: return f"⚠️ {err}"
        if not arts: return f"😔 No results found for <b>'{payload}'</b>."
        st.session_state.articles = arts
        st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
        st.session_state.last_intent = "search"
        st.session_state.last_query  = payload
        st.session_state.context_label = payload.title()
        return chat_cards(arts, payload.title(), "🔍")

    # ── Greeting ──
    if intent == "greeting":
        reply = gemini(f"You are NewsMate AI, a friendly India news chatbot. Reply warmly to: '{user_input}' in 1-2 lines and invite them to ask for news.")
        return reply or "👋 Hey there! I'm NewsMate AI. Ask me for <b>latest news</b>, <b>tech news</b>, <b>Kerala news</b> or anything!"

    # ── Show more (context memory) ──
    if intent == "more":
        if st.session_state.last_query:
            with st.spinner("📡 Fetching more..."):
                if st.session_state.last_intent == "category":
                    arts, err = fetch_by_category(st.session_state.last_query)
                else:
                    arts, err = fetch_by_search(st.session_state.last_query)
            if err: return f"⚠️ {err}"
            if not arts: return "😔 No more news found."
            st.session_state.articles = arts
            return chat_cards(arts, st.session_state.context_label, "🔄")
        return "ℹ️ Ask me for some news first, then say <b>show more</b>!"

    # ── Explain ──
    if intent == "explain":
        if not st.session_state.articles:
            return "ℹ️ Please fetch some news first, then ask me to explain!"
        a = st.session_state.articles[0]
        with st.spinner("🤖 Gemini is analyzing..."):
            # Context-aware explanation
            prompt = f"""Explain this news article in 5-6 clear, simple lines for a general audience. 
            Highlight the key impact for India.
            
            Title: {a.get('title','')}
            Description: {a.get('description','')}
            Content: {a.get('content','')}"""
            detail = gemini(prompt)
        return (f"<b>📖 Gemini AI Deep Dive</b><br><br>"
                f"<b>{a.get('title','')}</b><br><br>"
                f"{detail or a.get('description','No detail available.')}<br><br>"
                f"<a href='{a.get('url','#')}' target='_blank' style='color:{ACCENT}; text-decoration: none;'>🔗 Read full article on {a.get('source',{}).get('name','source')}</a>")

    # ── Location (city/state) → /everything ──
    if intent == "location":
        loc  = payload["location"]
        cat  = payload["category"]
        q    = f"{loc} {cat} news" if cat != "general" else f"{loc} news"
        label = f"{loc} · {cat.capitalize()}" if cat != "general" else loc
        with st.spinner(f"📍 Fetching {loc} news..."):
            arts, err = fetch_by_search(q)
        if err: return f"⚠️ {err}"
        if not arts: return f"😔 Couldn't find current news for <b>{loc}</b>. Try a broader search."
        st.session_state.articles = arts
        st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
        st.session_state.last_intent = "search"
        st.session_state.last_query  = q
        st.session_state.context_label = label
        intro = gemini(f"Write a friendly 1-line intro for showing news results about '{loc}' in India. Keep it natural.")
        intro = intro or f"Here are the latest news updates from <b>{loc}</b>."
        return f"{intro}<br><br>" + chat_cards(arts, label, "📍")

    # ── Category → top-headlines ──
    if intent == "category":
        st.session_state.category = payload
        with st.spinner(f"📡 Fetching {payload} news..."):
            arts, err = fetch_by_category(payload)
        if err: return f"⚠️ {err}"
        if not arts: return f"😔 No news found for <b>{payload}</b> right now."
        st.session_state.articles = arts
        st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
        st.session_state.last_intent = "category"
        st.session_state.last_query  = payload
        st.session_state.context_label = payload.capitalize()
        intro = gemini(f"Write a friendly 1-line intro for showing '{payload}' news from India. Keep it natural and short.")
        intro = intro or f"Here are the latest <b>{payload}</b> news updates from India."
        return f"{intro}<br><br>" + chat_cards(arts, payload.capitalize(), CAT_ICONS.get(payload,"📰"))

    # ── Generic news ──
    if intent == "news":
        cat = payload or st.session_state.category
        with st.spinner(f"📡 Fetching {cat} news..."):
            arts, err = fetch_by_category(cat)
        if err: return f"⚠️ {err}"
        if not arts: return f"😔 No news found for <b>{cat}</b>."
        st.session_state.articles = arts
        st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
        st.session_state.last_intent = "category"
        st.session_state.last_query  = cat
        st.session_state.context_label = cat.capitalize()
        intro = gemini(f"Write a friendly 1-line intro for showing '{cat}' news from India.")
        intro = intro or f"Here are the latest <b>{cat}</b> news updates from India."
        return f"{intro}<br><br>" + chat_cards(arts, cat.capitalize(), CAT_ICONS.get(cat,"📰"))

    # ── Gemini-powered intent (unknown queries) ──
    if intent == "gemini":
        with st.spinner("🤖 Understanding your query..."):
            classified = gemini_intent(payload)
        if classified:
            itype = classified.get("type","unknown")
            val   = classified.get("value","")
            intro = classified.get("conversational","")

            if itype == "greeting":
                return intro or "👋 Hey! Ask me for any news from India!"

            if itype == "location" and val:
                cat = classified.get("category","general")
                q   = f"{val} {cat} news" if cat != "general" else f"{val} news"
                with st.spinner(f"📍 Fetching {val} news..."):
                    arts, err = fetch_by_search(q)
                if err: return f"⚠️ {err}"
                if not arts: return f"😔 No news found for <b>{val}</b>."
                st.session_state.articles = arts
                st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
                st.session_state.last_intent = "search"
                st.session_state.last_query  = q
                st.session_state.context_label = val
                return f"{intro}<br><br>" + chat_cards(arts, val, "📍") if intro else chat_cards(arts, val, "📍")

            if itype == "category" and val:
                with st.spinner(f"📡 Fetching {val} news..."):
                    arts, err = fetch_by_category(val)
                if err: return f"⚠️ {err}"
                if not arts: return f"😔 No news for <b>{val}</b>."
                st.session_state.articles = arts
                st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
                st.session_state.last_intent = "category"
                st.session_state.last_query  = val
                st.session_state.context_label = val.capitalize()
                return f"{intro}<br><br>" + chat_cards(arts, val.capitalize(), CAT_ICONS.get(val,"📰")) if intro else chat_cards(arts, val.capitalize(), CAT_ICONS.get(val,"📰"))

            if itype == "keyword" and val:
                with st.spinner(f"🔍 Searching for {val}..."):
                    arts, err = fetch_by_search(f"{val} India")
                if err: return f"⚠️ {err}"
                if not arts: return f"😔 No results for <b>{val}</b>."
                st.session_state.articles = arts
                st.session_state.fetched  = datetime.now().strftime("%I:%M %p")
                st.session_state.last_intent = "search"
                st.session_state.last_query  = f"{val} India"
                st.session_state.context_label = val.title()
                return f"{intro}<br><br>" + chat_cards(arts, val.title(), "🔍") if intro else chat_cards(arts, val.title(), "🔍")

        # Pure conversational fallback via Gemini
        reply = gemini(f"You are NewsMate AI, a friendly India news chatbot. The user said: '{payload}'. Reply helpfully in 2-3 lines. If it's a news topic, suggest they ask 'search [topic] news'.")
        return reply or (f"🤖 I'm not sure about that. Try asking:<br>"
                         f"<span style='color:{STXT}'>• <b>latest news</b> &nbsp;• <b>tech news</b><br>"
                         f"• <b>Bengaluru news</b> &nbsp;• <b>search AI news</b><br>"
                         f"• <b>explain more</b></span>")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sb-head'>
        <h2>📰 NewsMate AI</h2>
        <p>Real-time India news assistant 🇮🇳</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 16px 16px'>", unsafe_allow_html=True)

    st.session_state.dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark)
    st.markdown("---")

    st.markdown("<div class='sb-lbl'>📂 Category</div>", unsafe_allow_html=True)
    cat = st.selectbox("cat", CATEGORIES,
                       index=CATEGORIES.index(st.session_state.category),
                       format_func=lambda c: f"{CAT_ICONS[c]} {c.capitalize()}",
                       label_visibility="collapsed")
    if cat != st.session_state.category:
        st.session_state.category = cat
    st.markdown("---")

    st.markdown("<div class='sb-lbl'>📍 State News</div>", unsafe_allow_html=True)
    state_opts = ["All India"] + [s.title() for s in sorted(set(INDIAN_STATES))]
    sel_state = st.selectbox("state", state_opts,
                             index=state_opts.index(st.session_state.state)
                             if st.session_state.state in state_opts else 0,
                             label_visibility="collapsed", key="state_sel")
    st.session_state.state = sel_state
    if st.button("📍 Get State News", use_container_width=True):
        loc = sel_state
        cmd = f"{loc} news"
        with st.spinner(f"📍 Fetching {loc} news..."):
            arts, err = fetch_by_search(f"{loc} news")
        if arts:
            st.session_state.articles = arts
            st.session_state.highlights = arts
            st.session_state.fetched = datetime.now().strftime("%I:%M %p")
            st.session_state.last_intent = "search"
            st.session_state.last_query  = f"{loc} news"
            st.session_state.context_label = loc
            st.session_state.messages.append({"role":"user","content":cmd})
            st.session_state.messages.append({"role":"bot","content":
                f"Here are the latest news updates from <b>{loc}</b>.<br><br>"
                + chat_cards(arts, loc, "📍")})
            st.rerun()
    st.markdown("---")

    if st.button("🔄 Refresh News", use_container_width=True):
        with st.spinner("Fetching..."):
            if st.session_state.state != "All India":
                arts, err = fetch_by_search(f"{st.session_state.state} {st.session_state.category} news")
            else:
                arts, err = fetch_by_category(st.session_state.category)
        if err:
            st.error(err)
        elif arts:
            st.session_state.articles = arts
            st.session_state.highlights = arts
            st.session_state.fetched = datetime.now().strftime("%I:%M %p")
            # Clear chat history and show fresh news
            st.session_state.messages = []
            label = st.session_state.category.capitalize()
            icon  = CAT_ICONS.get(st.session_state.category, "📰")
            st.session_state.messages.append({
                "role": "bot",
                "content": (f"🔄 News refreshed! Here are the latest <b>{label}</b> updates.<br><br>"
                            + chat_cards(arts, label, icon))
            })
            st.rerun()

    if st.session_state.fetched:
        st.caption(f"🕒 Last fetched: {st.session_state.fetched}")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Main Layout: Integrated ChatGPT Style ─────────────────────

st.title("📰 NewsMate AI")
st.caption("Your real-time India news assistant 🇮🇳")

col_chat, col_right = st.columns([7, 3], gap="medium")

with col_right:
    st.subheader("🔴 LIVE HIGHLIGHTS")
    # Standard container (auto-height)
    if "highlights" not in st.session_state:
        h_arts, _ = fetch_by_category("general")
        st.session_state.highlights = h_arts
    
    h_arts = st.session_state.highlights or st.session_state.articles
    if h_arts:
        for i, a in enumerate(h_arts[:15], 1):
            st.markdown(f"""
            <div class='rcard' onclick="window.open('{a.get('url','#')}', '_blank')">
                <div class='rcard-t'>{a.get('title','No title')}</div>
                <div class='rcard-src'>{a.get('source',{}).get('name','Unknown')} · {fmt_time(a.get('publishedAt',''))}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No highlights yet.")

with col_chat:
    # Centered wrapper for messages
    st.markdown("<div class='chat-container-wrap'>", unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "bot",
            "content": "👋 **Welcome to NewsMate AI!** I'm your real-time news assistant for India. <br><br>Try asking for:<br>• *Latest tech news*<br>• *Mumbai weather updates*<br>• *Explain the current economy news*"
        })

    for msg in st.session_state.messages:
        role_class = "row-user" if msg["role"] == "user" else "row-bot"
        bub_class = "bub-user" if msg["role"] == "user" else "bub-bot"
        av_class = "av-user" if msg["role"] == "user" else "av-bot"
        icon = "👤" if msg["role"] == "user" else "🤖"
        
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='{role_class}'>
                <div class='{bub_class}'>{msg['content']}</div>
                <div class='av {av_class}'>{icon}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='{role_class}'>
                <div class='av {av_class}'>{icon}</div>
                <div class='{bub_class}'>{msg['content']}</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True) # End chat-container-wrap
    
    # Input remains fixed at bottom via CSS (targeting stForm)
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([8, 2])
        with c1:
            user_input = st.text_input("input", placeholder="Ask NewsMate anything...", label_visibility="collapsed")
        with c2:
            submitted = st.form_submit_button("Send 🚀")
    
    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = respond(user_input)
            st.session_state.messages.append({"role": "bot", "content": reply})
        st.rerun()

# No JavaScript needed for container scroll if we use page scroll
