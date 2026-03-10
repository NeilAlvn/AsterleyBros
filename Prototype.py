import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from tavily import TavilyClient

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Asterley Bros Scout", page_icon="", layout="wide")

# --- API Configurations ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- System Prompt ---
SYSTEM_PROMPT = """You are an AI assistant for Rob Asterley, founder of Asterley Bros.
We make premium British Amaro, Vermouth, and Fernet in South London.

YOUR GOAL:
1. Scan the provided Context for any CONTACT EMAIL address.
2. Write a 3-4 sentence warm, craft-focused pitch. Compliment their menu/vibe.

RESPONSE FORMAT (STRICT):
CONTACT EMAIL: [The email or "Not found"]
PITCH:
[The email draft]
"""

# --- Initialize Session State for Tracking ---
if 'total_prompt_tokens' not in st.session_state:
    st.session_state.total_prompt_tokens = 0
if 'total_output_tokens' not in st.session_state:
    st.session_state.total_output_tokens = 0
if 'leads_df' not in st.session_state:
    st.session_state.leads_df = pd.DataFrame({
        'Target Name': ['Schofield\'s Bar', 'Swift Soho', ''],
        'City/Area': ['Manchester', 'London', ''],
        'Venue Type': ['Cocktail Bar', 'Cocktail Bar', 'Restaurant'],
        'Found Email': ['', '', ''], 
        'Status': ['Ready for AI', 'Ready for AI', ''],
        'Vibe Context': ['', '', ''],
        'AI Drafted Email': ['', '', '']
    })

# --- Core Functions ---

def get_venue_context(venue, city):
    search_query = f"{venue} {city} official website contact email instagram facebook menu vibe"
    try:
        response = tavily_client.search(query=search_query, search_depth="advanced", max_results=5)
        if "results" in response and len(response["results"]) > 0:
            return " ".join([result['content'] for result in response['results']])
        return "No data found."
    except Exception as e:
        return f"Tavily Error: {e}"

def generate_pitch(venue_name, city, venue_type, context):
    full_prompt = f"Venue: {venue_name} ({city}). Type: {venue_type}\n\nContext Found:\n{context}"
    try:
        response = model.generate_content([SYSTEM_PROMPT, full_prompt])
        
        # Track Tokens
        usage = response.usage_metadata
        st.session_state.total_prompt_tokens += usage.prompt_token_count
        st.session_state.total_output_tokens += usage.candidates_token_count
        
        output = response.text
        extracted_email = "Not found"
        draft = output
        
        if "CONTACT EMAIL:" in output and "PITCH:" in output:
            parts = output.split("PITCH:")
            extracted_email = parts[0].replace("CONTACT EMAIL:", "").strip()
            draft = parts[1].strip()
            
        return extracted_email, draft
    except Exception as e:
        return "Error", f"Pitch Error: {e}"

# --- Sidebar: Token Usage Pie Chart ---
with st.sidebar:
    st.header("Token Usage")
    total = st.session_state.total_prompt_tokens + st.session_state.total_output_tokens
    
    if total > 0:
        st.write(f"Total Tokens: {total:,}")
        
        # Create the Pie Chart
        labels = ['Prompt (Input)', 'Output (AI)']
        sizes = [st.session_state.total_prompt_tokens, st.session_state.total_output_tokens]
        colors = ['#ff9999','#66b3ff']
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        st.pyplot(fig)
        
        st.metric("Prompt Tokens", f"{st.session_state.total_prompt_tokens:,}")
        st.metric("Output Tokens", f"{st.session_state.total_output_tokens:,}")
    else:
        st.write("No usage data yet. Run a scout to see stats!")

# --- UI: Main Content ---
st.title("Generate personalised outreach (emails/DMs)")
st.markdown("### Powered by Tavily Deep Search + Gemini 3 Flash")

tab1, tab2 = st.tabs(["Single Scout", "CRM"])    

with tab1:
    with st.form("single_form"):
        col1, col2 = st.columns(2)
        with col1:
            v = st.text_input("Venue Name")
        with col2:
            c = st.text_input("City")
        t = st.selectbox("Type", ["Cocktail Bar", "Bottle Shop", "Restaurant"])
        btn = st.form_submit_button("Scout & Extract")

    if btn and v:
        with st.spinner("Searching web and socials..."):
            ctx = get_venue_context(v, c)
            found_email, pitch = generate_pitch(v, c, t, ctx)
            
            st.success("Analysis Complete")
            st.info(f"**Extracted Contact:** {found_email}")
            st.text_area("Custom Pitch:", pitch, height=200)

with tab2:
    st.subheader("Interactive CRM")
    edited_df = st.data_editor(st.session_state.leads_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("🚀 Run Bulk Research"):
        rows_to_do = edited_df[edited_df['Status'] == 'Ready for AI']
        if not rows_to_do.empty:
            progress = st.progress(0)
            for i, (idx, row) in enumerate(rows_to_do.iterrows()):
                ctx = get_venue_context(row['Target Name'], row['City/Area'])
                found_email, pitch = generate_pitch(row['Target Name'], row['City/Area'], row['Venue Type'], ctx)
                
                edited_df.at[idx, 'Found Email'] = found_email
                edited_df.at[idx, 'Vibe Context'] = ctx
                edited_df.at[idx, 'AI Drafted Email'] = pitch
                edited_df.at[idx, 'Status'] = 'Drafted'
                progress.progress((i + 1) / len(rows_to_do))
            
            st.session_state.leads_df = edited_df
            st.rerun()

    st.divider()
    csv = st.session_state.leads_df.to_csv(index=False).encode('utf-8')

    st.download_button("📥 Download Lead Sheet", csv, "botanical_leads.csv", "text/csv")



