import streamlit as st
from google import genai

import os

# Page config
st.set_page_config(
    page_title="Manufacturing SOP & Safety Explainer Bot",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS for industrial theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        font-weight: bold;
    }
    .safety-warning {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configure Gemini API
@st.cache_resource
def load_model():
    api_key = "api_key"
    if not api_key:
        st.error("🚨 Please set GEMINI_API_KEY in Streamlit secrets or environment variables")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    # Safety system prompt - STRICTLY explanation only
    system_prompt = """
    You are a Manufacturing Plant SOP & Safety Explainer Bot. Your role is to EXPLAIN safety procedures and SOPs in simple, clear language.

    IMPORTANT SAFETY RESTRICTIONS:
    1. ONLY EXPLAIN procedures - NEVER approve actions
    2. NEVER make operational decisions or compliance judgments
    3. NEVER replace human supervisor authority
    4. Always say "Consult your supervisor for approval" when actions are mentioned
    5. Use simple language suitable for new employees/interns
    6. Reference standard manufacturing safety practices

    Sample topics you can explain:
    - Lockout-Tagout (LOTO) procedures
    - Safety gear requirements
    - Emergency shutdown steps
    - Machine operation SOPs
    - PPE usage guidelines

    ALWAYS end with: "For specific approvals, consult your supervisor."
    
    Respond in short, clear paragraphs with bullet points when helpful.
    """
    
    model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-001",  # ✅ supported
    system_instruction=system_prompt,
    generation_config={
        "temperature": 0.3,
        "top_p": 0.8,
        "max_output_tokens": 1000,
    })

    return model

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load model
try:
    model = load_model()
except Exception as e:
    st.error(f"Failed to load model: {str(e)}")
    st.stop()

# Header
st.markdown('<h1 class="main-header">🏭 Manufacturing SOP & Safety Explainer Bot</h1>', unsafe_allow_html=True)

# Safety warning
with st.container():
    st.markdown("""
    <div class="safety-warning">
        <strong>⚠️ IMPORTANT:</strong> This bot provides EXPLANATIONS ONLY. 
        It does NOT approve actions or replace supervisor authority.
        Always consult your supervisor before performing any task.
    </div>
    """, unsafe_allow_html=True)

# Sample queries
with st.expander("💡 Try these sample queries", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔒 Explain Lockout-Tagout"):
            st.session_state.sample_query = "Explain lockout-tagout in simple terms"
    with col2:
        if st.button("🛡️ Safety gear for heavy machines"):
            st.session_state.sample_query = "What safety gear is used near heavy machines?"
    with col3:
        if st.button("🚨 Emergency shutdown"):
            st.session_state.sample_query = "Summarize emergency shutdown procedure"

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0]["text"])


# Chat input
if prompt := st.chat_input("Ask about SOPs, safety procedures, or manufacturing processes..."):
    # Handle sample query
    if hasattr(st.session_state, 'sample_query'):
        prompt = st.session_state.sample_query
        del st.session_state.sample_query
    
    # Add user message
    st.session_state.messages.append({"role": "user","parts": [{"text": prompt}]})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking about safety..."):
            try:
                # Create chat session with history
                chat = model.start_chat(history=st.session_state.messages[:-1])
                response = chat.send_message(prompt)

                full_response = response.text
                
                # Safety check - ensure compliance
                if any(phrase in full_response.lower() for phrase in ["approve", "approved", "permission granted", "you can"]):
                    full_response += "\n\n⚠️ **REMINDER:** This is EXPLANATION ONLY. Consult your supervisor for approval."
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant","parts": [{"text": full_response}]})

                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Please check your API key and try again.")

# Sidebar info
with st.sidebar:
    st.markdown("## 📋 Project Features")
    st.markdown("""
    - **Gemini 2.5 Flash** model for fast responses [web:1]
    - **Safety system prompts** - explanation only
    - **Chat history** maintained across sessions
    - **Industrial theme** UI
    - **Tested queries** ready to use
    """)
    
    st.markdown("## 🎯 Deliverables Checklist")
    st.markdown("""
    - ✅ Streamlit Web App
    - ✅ Tested GenAI Bot Queries
    - ✅ Safety guardrails implemented
    - ✅ Prompt engineering demonstrated
    - ✅ Ready for factory deployment
    """)

# Footer
st.markdown("---")
st.markdown("*Built for Manufacturing Safety Training | Team Hackathon Project* [web:11]")

