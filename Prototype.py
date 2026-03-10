import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import json
from tavily import TavilyClient

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Asterley Bros Scout", page_icon="🍸", layout="wide")

# --- API Configurations ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- System Prompt ---
SYSTEM_PROMPT = """You are Rob Asterley, founder of Asterley Bros (South London botanical spirits). 
Use the provided 'Research Context' to write a short, warm, professional outreach email for each venue.

STRATEGY:
1. Reference a specific detail found in the research (e.g., their menu style, a specific award, or their vibe).
2. Suggest why one of our products (Dispense Amaro, Schofield's Dry Vermouth, or Britannica Fernet) is a perfect fit.
3. Tone: Craft-focused, professional, and British.
4. If an email is found in the research, include it.

RESPONSE FORMAT (STRICT JSON):
[
  {"name": "Venue Name", "email": "extracted email or info@", "pitch": "Full email text..."},
  ...
]
"""

# --- Initialize Session State ---
if 'total_prompt_tokens' not in st.session_state:
    st.session_state.total_prompt_tokens = 0
if 'total_output_tokens' not in st.session_state:
    st.session_state.total_output_tokens = 0
if 'leads_df' not in st.session_state:
    st.session_state.leads_df = pd.DataFrame({
        'Target Name': ['Satan\'s Whiskers', 'Panda & Sons', 'Hedonism Wines'],
        'City/Area': ['London', 'Edinburgh', 'London'],
        'Venue Type': ['Cocktail Bar', 'Cocktail Bar', 'Bottle Shop'],
        'Found Email': ['', '', ''], 
        'Status': ['Ready for AI', 'Ready for AI', 'Ready for AI'],
        'AI Drafted Email': ['', '', '']
    })

# --- Core Functions ---

def get_research_for_leads(df_subset):
    """Uses Tavily to gather deep intel on every bar in the list."""
    research_results = []
    for _, row in df_subset.iterrows():
        query = f"{row['Target Name']} {row['City/Area']} cocktail bar menu vibe contact email"
        try:
            # We use Tavily to get the 'meat' for the email
            search = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            context = " ".join([r['content'] for r in search['results']])
            research_results.append({
                "name": row['Target Name'],
                "city": row['City/Area'],
                "research": context
            })
        except:
            research_results.append({"name": row['Target Name'], "research": "No specific data found."})
    return research_results

def run_one_shot_ai(research_bundle):
    """Sends the entire research bundle to Gemini in 1 single request."""
    prompt = f"Write personalized emails for these venues based on this research data:\n{json.dumps(research_bundle)}"
    
    try:
        response = model.generate_content(
            [SYSTEM_PROMPT, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Track Tokens
        usage = response.usage_metadata
        st.session_state.total_prompt_tokens += usage.prompt_token_count
        st.session_state.total_output_tokens += usage.candidates_token_count
        
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- Sidebar: Token Usage ---
with st.sidebar:
    st.header("📊 Token Usage")
    total = st.session_state.total_prompt_tokens + st.session_state.total_output_tokens
    if total > 0:
        st.write(f"Total Tokens: {total:,}")
        fig, ax = plt.subplots()
        ax.pie([st.session_state.total_prompt_tokens, st.session_state.total_output_tokens], 
               labels=['Input', 'Output'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
        st.pyplot(fig)

# --- Main UI ---
st.title("The Botanical Scout 🍸")
st.markdown("### Deep Research (Tavily) + One-Shot Drafting (Gemini 3)")

edited_df = st.data_editor(st.session_state.leads_df, num_rows="dynamic", use_container_width=True)

if st.button("🚀 Run Deep Research & Drafting"):
    rows_to_do = edited_df[edited_df['Status'] == 'Ready for AI']
    
    if not rows_to_do.empty:
        # STEP 1: Research (Tavily)
        with st.spinner("Step 1/2: Searching the web for venue intel..."):
            research_bundle = get_research_for_leads(rows_to_do)
        
        # STEP 2: Drafting (Gemini)
        with st.spinner("Step 2/2: Gemini is writing personalized emails..."):
            results = run_one_shot_ai(research_bundle)
            
            if results:
                for res in results:
                    idx = edited_df[edited_df['Target Name'] == res['name']].index
                    if not idx.empty:
                        edited_df.at[idx[0], 'Found Email'] = res.get('email', 'info@')
                        edited_df.at[idx[0], 'AI Drafted Email'] = res.get('pitch', '')
                        edited_df.at[idx[0], 'Status'] = 'Drafted'
                
                st.session_state.leads_df = edited_df
                st.success("Research and Drafting Complete in 1 Gemini Request!")
                st.rerun()

st.divider()
st.download_button("📥 Download Lead Sheet", st.session_state.leads_df.to_csv(index=False).encode('utf-8'), "asterley_leads.csv")
