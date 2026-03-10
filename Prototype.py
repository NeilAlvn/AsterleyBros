import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import json
from tavily import TavilyClient

# --- Page Configuration ---
st.set_page_config(page_title="Asterley Bros | Trade Scout", layout="wide")

# --- UI Branding & Styling (Matching AsterleyBros.com) ---
st.markdown("""
    <style>
    /* Import Elegant Fonts (Playfair Display for Headers, Lato for Body) */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
    }
    
    h1, h2, h3, .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px;
    }

    /* Subtle Copper/Gold Accents from their bottle labels */
    :root {
        --brand-copper: #C8A97E;
    }

    /* Center the Header and Control Logo Size */
    .brand-header {
        text-align: center;
        padding-bottom: 20px;
    }
    .brand-header img {
        width: 280px; /* Fixed size to prevent the massive stretch */
        margin-bottom: 15px;
    }
    .brand-header h1 {
        margin-bottom: 0px;
        padding-bottom: 0px;
        font-size: 2.2rem;
    }
    .brand-header p {
        color: #888888;
        font-size: 1.1rem;
        letter-spacing: 1px;
    }

    /* Premium Metric Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(200, 169, 126, 0.2);
        padding: 20px;
        border-radius: 2px;
    }

    /* Elegant Action Button */
    div.stButton > button:first-child {
        background-color: transparent;
        color: var(--brand-copper);
        border-radius: 2px;
        border: 1px solid var(--brand-copper);
        height: 3.5em;
        width: 100%;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: var(--brand-copper);
        color: #000000;
        border: 1px solid var(--brand-copper);
    }
    
    /* Customize the Horizontal Rule */
    hr {
        border-bottom: 1px solid rgba(200, 169, 126, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Perfectly Centered Header Section ---
LOGO_URL = "https://asterleybros.com/cdn/shop/files/logo.png?v=1722617407"

st.markdown(f"""
    <div class="brand-header">
        <img src="{LOGO_URL}" alt="Asterley Bros Logo">
        <h1>Trade Account Intelligence</h1>
        <p>Strategic Market Research & Personalised Outreach Console</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- API Configurations ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- System Prompt ---
SYSTEM_PROMPT = """You are Rob Asterley, founder of Asterley Bros. 
Write a warm, personal outreach email for each venue based on the research provided.

GREETING: Use "Hi [Name]," if a name is found. Otherwise, just use "Hi," or "Hello,". 
NEVER use "Hi Team" or "Hi [Venue Name]".

CONTENT: 
- Reference a specific detail from the research (e.g. their specific cocktail menu or vibe). 
- Suggest a sample drop-off of Dispense Amaro or Schofield's Dry Vermouth.

FORMAT: Return ONLY a JSON list of objects with 'name', 'email', and 'pitch'."""

# --- Initialize Session State ---
if 'total_prompt_tokens' not in st.session_state:
    st.session_state.total_prompt_tokens = 0
if 'total_output_tokens' not in st.session_state:
    st.session_state.total_output_tokens = 0
if 'leads_df' not in st.session_state:
    st.session_state.leads_df = pd.DataFrame({
        'Target Name': ['Satan\'s Whiskers', 'Panda & Sons', 'The Connaught Bar'],
        'City/Area': ['London', 'Edinburgh', 'London'],
        'Venue Type': ['Cocktail Bar', 'Cocktail Bar', 'Cocktail Bar'],
        'Found Email': ['', '', ''], 
        'Status': ['Ready for Processing', 'Ready for Processing', 'Ready for Processing'],
        'Research Context': ['', '', ''],
        'AI Drafted Pitch': ['', '', '']
    })

# --- Business Logic Functions ---
def get_research_for_leads(df_subset):
    research_results = []
    for _, row in df_subset.iterrows():
        query = f"{row['Target Name']} {row['City/Area']} bar manager name cocktail menu vibe"
        try:
            search = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            context = " ".join([r['content'] for r in search['results']])
            research_results.append({"name": row['Target Name'], "research": context})
        except:
            research_results.append({"name": row['Target Name'], "research": "Data unavailable."})
    return research_results

def run_one_shot_ai(research_bundle):
    prompt = f"Using this research context, write the emails:\n{json.dumps(research_bundle)}"
    try:
        response = model.generate_content([SYSTEM_PROMPT, prompt], generation_config={"response_mime_type": "application/json"})
        usage = response.usage_metadata
        st.session_state.total_prompt_tokens += usage.prompt_token_count
        st.session_state.total_output_tokens += usage.candidates_token_count
        return json.loads(response.text)
    except:
        return None

# --- Main Interface ---
tab1, tab2 = st.tabs(["Active Leads", "Platform Analytics"])

with tab1:
    st.write("### Account Pipeline")
    edited_df = st.data_editor(st.session_state.leads_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Execute Batch Analysis"):
        rows_to_do = edited_df[edited_df['Status'] == 'Ready for Processing']
        if not rows_to_do.empty:
            with st.status("Gathering Market Intel...", expanded=True) as status:
                research_bundle = get_research_for_leads(rows_to_do)
                results = run_one_shot_ai(research_bundle)
                
                if results:
                    for i, res in enumerate(results):
                        idx = edited_df[edited_df['Target Name'] == res['name']].index
                        if not idx.empty:
                            edited_df.at[idx[0], 'Found Email'] = res.get('email', 'info@')
                            edited_df.at[idx[0], 'Research Context'] = research_bundle[i]['research'][:500] + "..."
                            edited_df.at[idx[0], 'AI Drafted Pitch'] = res.get('pitch', '')
                            edited_df.at[idx[0], 'Status'] = 'Drafted'
                    
                    st.session_state.leads_df = edited_df
                    st.rerun()

    st.download_button("Export Data", st.session_state.leads_df.to_csv(index=False).encode('utf-8'), "asterley_leads.csv")

with tab2:
    st.write("### Compute Consumption")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Input Tokens", f"{st.session_state.total_prompt_tokens:,}")
    with col_b:
        st.metric("Output Tokens", f"{st.session_state.total_output_tokens:,}")
    
    if (st.session_state.total_prompt_tokens + st.session_state.total_output_tokens) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        # Updated chart to match the copper brand aesthetic
        ax.pie([st.session_state.total_prompt_tokens, st.session_state.total_output_tokens], 
               labels=['Input', 'Output'], autopct='%1.1f%%', colors=['#C8A97E','#444444'], textprops={'color':"grey"})
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        st.pyplot(fig)
