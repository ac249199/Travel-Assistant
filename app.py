
import streamlit as st
import asyncio
import uuid
import re

from app.orchestration.orchestrator import orchestrate


# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="Banarasi Bhaukal Travel Guru",
    page_icon="🧭",
    layout="centered"
)


# ---------------------------------
# SIMPLE CSS
# ---------------------------------

st.markdown("""
<style>

.main .block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.stChatMessage {
    border-radius: 12px;
}

h1 {
    font-size: 30px;
}

.chat-subtitle {
    color: #888888;
    font-size: 14px;
    margin-top: -15px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------
# SESSION STATE
# ---------------------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------
# NEW CHAT
# ---------------------------------

def start_new_chat():

    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []


# ---------------------------------
# HEADER
# ---------------------------------

header_col1, header_col2 = st.columns([4, 1])

with header_col1:

    st.title("Banarasi Bhaukal Travel Guru")

    st.markdown(
        '<p class="chat-subtitle">'
        'Your AI-powered travel assistant'
        '</p>',
        unsafe_allow_html=True
    )

with header_col2:

    st.button(
        "＋ New Chat",
        on_click=start_new_chat,
        use_container_width=True
    )

st.divider()


# ---------------------------------
# WELCOME MESSAGE
# ---------------------------------

if not st.session_state.messages:

    st.markdown("### Namaste! Welcome 👋")

    st.write(
        "I can help you explore Varanasi, plan your trip "
        "and search for hotels, flights and trains."
    )

    st.caption("Try asking:")

    suggestions = [
        "Tell me about Kashi Vishwanath Temple",
        "Plan a 3-day trip to Varanasi",
        "Find hotels in Varanasi",
        "Find a train from Varanasi to Delhi"
    ]

    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")

    st.divider()


# ---------------------------------
# RESPONSE EXTRACTION
# ---------------------------------

def extract_response(response):

    if isinstance(response, dict):

        assistant_response = response.get("response")

        if isinstance(assistant_response, dict):

            assistant_response = (
                assistant_response.get("message")
                or assistant_response.get("formatted_message")
                or assistant_response.get("answer")
                or str(assistant_response)
            )

        elif not assistant_response:

            assistant_response = (
                response.get("message")
                or response.get("formatted_message")
                or response.get("answer")
                or str(response)
            )

    else:
        assistant_response = str(response)

    return str(assistant_response)


# ---------------------------------
# RESPONSE DISPLAY
# ---------------------------------

def display_response(content):

    # Render normal Markdown, headings, lists and links.
    # Convert escaped separator lines into clean horizontal rules.
    content = content.replace("\\==========", "==========")

    st.markdown(content)


# ---------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        display_response(message["content"])


# ---------------------------------
# CHAT INPUT
# ---------------------------------

user_query = st.chat_input(
    "Ask me anything about Varanasi or your travel plans..."
)


if user_query:

    # Save and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)


    # Get response from Orchestrator
    with st.chat_message("assistant"):

        with st.spinner("Planning your experience..."):

            try:

                response = asyncio.run(
                    orchestrate(
                        user_query,
                        conversation_id=st.session_state.conversation_id
                    )
                )

                assistant_response = extract_response(response)

            except Exception as e:

                assistant_response = (
                    "Something went wrong while processing your request.\n\n"
                    f"Error: `{str(e)}`"
                )

        display_response(assistant_response)


    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })
