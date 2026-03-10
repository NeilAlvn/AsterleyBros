import streamlit as st
from google import genai
import pandas as pd
import json
from tavily import TavilyClient

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Asterley Bros Scout", page_icon="🍸", layout="wide")

# --- API Configurations ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- Session State ---
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

def get_bulk_context(df_subset):
    """Gathers research for multiple bars using Tavily (does not count toward Gemini RPD)."""
    bulk_data = []
    for _, row in df_subset.iterrows():
        query = f"{row['Target Name']} {row['City/Area']} cocktail menu vibe contact email"
        try:
            search = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            context = " ".join([r['content'] for r in search['results']])
            bulk_data.append({
                "name": row['Target Name'],
                "city": row['City/Area'],
                "context": context
            })
        except:
            bulk_data.append({"name": row['Target Name'], "city": row['City/Area'], "context": "No data found."})
    return bulk_data

def run_one_shot_ai(bulk_research):
    """Sends EVERYTHING to Gemini in exactly ONE request."""
    
    # We use a structured system instruction to ensure Gemini returns valid JSON
    system_instruction = """You are an assistant for Rob Asterley. 
    Write a 3-sentence craft-focused pitch for each venue provided. 
    Also, extract a contact email if visible in the context.
    
    IMPORTANT: You must return the data ONLY as a JSON list of objects with these keys: 
    'name', 'email', 'pitch'."""

    # Format the bulk data into a string for the prompt
    prompt_content = f"Generate pitches for these venues based on this research:\n{json.dumps(bulk_research)}"

    try:
        # This is your ONE DAILY REQUEST
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Switching to 2.5 as it has more requests left in your screenshot
            config={
                'system_instruction': system_instruction,
                'response_mime_type': 'application/json' 
            },
            contents=prompt_content
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- Main UI ---
st.title("The Botanical Scout 🍸")
st.info(f"Using 'One-Shot' Mode to save API Quota. This will use only 1 Gemini Request.")

edited_df = st.data_editor(st.session_state.leads_df, num_rows="dynamic", use_container_width=True)

if st.button("🚀 Run One-Shot Bulk Research"):
    rows_to_process = edited_df[edited_df['Status'] == 'Ready for AI']
    
    if not rows_to_process.empty:
        with st.spinner("Step 1: Gathering Web Research..."):
            research_data = get_bulk_context(rows_to_process)
        
        with st.spinner("Step 2: Sending ONE request to Gemini..."):
            results = run_one_shot_ai(research_data)
            
            if results:
                # Map the results back to the dataframe
                for item in results:
                    idx = edited_df[edited_df['Target Name'] == item['name']].index
                    if not idx.empty:
                        edited_df.at[idx[0], 'Found Email'] = item.get('email', 'Not found')
                        edited_df.at[idx[0], 'AI Drafted Email'] = item.get('pitch', '')
                        edited_df.at[idx[0], 'Status'] = 'Drafted'
                
                st.session_state.leads_df = edited_df
                st.success("Success! All leads processed in 1 API call.")
                st.rerun()

st.download_button("📥 Download CSV", st.session_state.leads_df.to_csv(index=False).encode('utf-8'), "asterley_leads.csv")



