# 🥃 Asterley Bros | Trade Account Intelligence

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)

A Streamlit-powered internal tool for researching prospective trade accounts and generating personalised outreach emails — built for the Asterley Bros sales workflow.

## 📋 Overview

This trade intelligence console enables the Asterley Bros sales team to identify, research, and personally reach out to high-potential venues at scale. Built with Python and Streamlit for the frontend, Google Gemini for AI-powered pitch generation, and Tavily for live web research, the system dramatically reduces the time spent on manual prospecting while keeping outreach feeling personal and authentic.

## ✨ Key Features

### 🔍 Automated Market Research
- **Live Venue Intel** - Scrapes and summarises cocktail menu focus, venue vibe, and manager names
- **Tavily-Powered Search** - Advanced web search with multi-source context aggregation
- **Batch Processing** - Research multiple venues in a single click
- **Context Snapshots** - Stores research summaries directly alongside each lead

### 🤖 AI-Powered Pitch Generation
- **Personalised Emails** - Every pitch references a specific detail about the target venue
- **Brand Voice** - Written in the voice of Rob Asterley, founder of Asterley Bros
- **Smart Greetings** - Detects real contact names; avoids generic "Hi Team" openers
- **Product Focused** - Naturally surfaces Dispense Amaro and Schofield's Dry Vermouth

### 📊 Pipeline Management
- **Editable Lead Table** - Add, update, and manage leads directly in the UI
- **Status Tracking** - Monitor each lead from `Ready for Processing` through to `Drafted`
- **CSV Export** - Download the full pipeline for use in external CRMs or email tools
- **Session Persistence** - Lead data is preserved across interactions within a session

### 📈 Platform Analytics
- **Token Usage Tracking** - Monitor cumulative Gemini API consumption
- **Input/Output Breakdown** - Pie chart visualisation of prompt vs. completion tokens
- **Cost Awareness** - Stay on top of API spend in real time

## 🚀 Technologies Used

### Backend
- **Python** - Core application logic and data processing
- **Google Gemini** (`gemini-3-flash-preview`) - AI email generation
- **Tavily API** - Live web research and venue intelligence

### Frontend
- **Streamlit** - Web application framework
- **Pandas** - Lead data management and CSV export
- **Matplotlib** - Token usage visualisation

### Data & Formatting
- **JSON** - Structured AI response parsing
- **CSS / Google Fonts** - Custom Asterley Bros branding (Playfair Display + Lato)

## 📋 Prerequisites

Before installation, ensure you have:

- **Python 3.8+** installed
- **Google Gemini API key** (via Google AI Studio)
- **Tavily API key** (via tavily.com)
- **Modern web browser** (Chrome, Firefox, Edge)
- **pip** package manager

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-org/asterley-trade-scout.git
cd asterley-trade-scout
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. 🔑 Configure API keys
Create a `.streamlit/secrets.toml` file in the project root:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
TAVILY_API_KEY = "your-tavily-api-key"
```

### 4. ▶️ Run the application
```bash
streamlit run app.py
```

### 5. Access the dashboard
Navigate to `http://localhost:8501` in your browser.

## 📁 Project Structure

```
asterley-trade-scout/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── secrets.toml           # 🔒 API keys (do not commit)
└── README.md                  # Documentation
```

## 🎯 Usage

### For the Sales Team

1. **Open the dashboard**
   - Run `streamlit run app.py`
   - Navigate to `http://localhost:8501`

2. **Add your leads**
   - Edit the leads table directly in the **Active Leads** tab
   - Enter venue name, city/area, and venue type
   - Ensure Status is set to `Ready for Processing`

3. **Run batch analysis**
   - Click **Execute Batch Analysis**
   - The system researches each venue and drafts a personalised pitch
   - Results populate directly back into the table

4. **Export your pipeline** 📥
   - Click **Export Data** to download the full lead list as a CSV
   - Import into your CRM or email tool of choice

### For Administrators

1. **Monitor API usage**
   - Navigate to the **Platform Analytics** tab
   - Review token consumption per session
   - Use this to estimate monthly API costs

2. **Update the AI prompt**
   - Edit the `SYSTEM_PROMPT` variable in `app.py`
   - Adjust tone, product focus, or output format as needed

3. **Switch AI models**
   - Update the model string in `app.py`
   - Current: `gemini-3-flash-preview`

## 🔐 Security Features

- **Secrets Management** - API keys stored in `.streamlit/secrets.toml`, never hardcoded
- **No Data Persistence** - Lead data and token counts reset on session end
- **Local Execution** - Application runs locally; no data sent to third parties beyond API calls
- **Gitignore Ready** - Secrets file excluded from version control

## 📊 Data & Metrics Collected

### Per Venue
- Target name and location
- Venue type and profile
- Found contact email
- Research context snippet (500 chars)
- AI-drafted outreach pitch
- Processing status

### Platform Analytics
- Total input (prompt) tokens used
- Total output (completion) tokens used
- Input/output token ratio

## 🛠️ Configuration

### AI Prompt

Edit the `SYSTEM_PROMPT` in `app.py` to adjust the email tone or product focus:
```python
SYSTEM_PROMPT = """You are Rob Asterley, founder of Asterley Bros.
Write a warm, personal outreach email for each venue based on the research provided.
...
"""
```

### Research Depth

Adjust Tavily search parameters in `get_research_for_leads()`:
```python
search = tavily_client.search(
    query=query,
    search_depth="advanced",  # "basic" or "advanced"
    max_results=3              # Increase for more context
)
```

### Context Snippet Length

Adjust the research context stored per lead:
```python
edited_df.at[idx[0], 'Research Context'] = research_bundle[i]['research'][:500] + "..."
#                                                                              ^^^^
#                                                              Increase for more detail
```

## 📈 Performance & Scalability

- **Batch Efficiency** - All venues in a batch are processed in a single Gemini API call
- **Minimal Latency** - One-shot AI generation reduces round-trips
- **Lightweight Frontend** - Streamlit handles UI state with no external database needed
- **Extensible Pipeline** - Easily add new columns or data sources to the leads table

## 🔧 Troubleshooting

### Pitches Not Generating

**AI returns empty or malformed output:**
- Check your `GEMINI_API_KEY` in `secrets.toml`
- Verify the model name is correct and available in your region
- Inspect the raw response by temporarily printing `response.text`

**Research context is empty:**
- Check your `TAVILY_API_KEY` in `secrets.toml`
- Verify network connectivity
- Try a simpler venue name in your query

### App Won't Start

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Secrets not found:**
- Ensure `.streamlit/secrets.toml` exists and is correctly formatted
- Keys are case-sensitive: `GEMINI_API_KEY` not `gemini_api_key`

### Export Not Working

**CSV download fails:**
- Ensure the leads table has been populated
- Try clearing the browser cache and reloading

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary to Asterley Bros. For licensing enquiries, please contact the team directly.

## 🚧 Future Enhancements

- [ ] CRM integration (HubSpot / Salesforce)
- [ ] Automated email sending via SendGrid or Mailgun
- [ ] Multi-user login with role-based access
- [ ] Persistent lead storage with database backend
- [ ] A/B testing for pitch variations
- [ ] Follow-up sequence generation
- [ ] Venue scoring and prioritisation
- [ ] Slack notifications for completed batches
- [ ] Mobile-friendly responsive layout
- [ ] Analytics dashboard with conversion tracking

## 👨‍💻 Developer

**Asterley Bros Internal Tools**

Built for the Asterley Bros sales and operations team, specialising in:
- Trade Account Prospecting
- AI-Powered Personalisation
- Sales Pipeline Automation
- Brand-Consistent Outreach

### 📍 Location
London, United Kingdom

### 🔗 Connect
- **Website**: [asterleybros.com](https://asterleybros.com)
- **Instagram**: [@asterleybros](https://instagram.com/asterleybros)

## 📞 Support

For technical support or feature requests:
- 🐙 GitHub Issues: [Report a bug](https://github.com/your-org/asterley-trade-scout/issues)

## 🙏 Acknowledgments

- Built to address real-world trade sales challenges at Asterley Bros
- Powered by Google Gemini and Tavily's research APIs
- Styled to match the Asterley Bros brand identity
- Inspired by the need for personal outreach at scale

## 📚 Documentation

For detailed documentation:
- **User Guide** - See `docs/user_guide.md`
- **Admin Manual** - See `docs/admin_manual.md`
- **API Reference** - See `docs/api_reference.md`

---

⭐ If this tool saves you time, share it with the team!

**Made with ❤️ for Asterley Bros**

© 2026 Asterley Bros. All rights reserved.
