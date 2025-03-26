import streamlit as st
import requests
import datetime
import pytz


st.set_page_config(layout="wide")

if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.datetime.now(pytz.timezone("Israel")).strftime("%d-%m-%y %H:%M:%S")

left, main, right = st.columns([0.2, 0.6, 0.2])

main.title("Patent expert chatbot")
left.markdown("")
left.markdown("#### Previous Conversations")

main.image("images/patent_lawyer.jpg", width=300)

main.markdown("##### Hi Ariel, I'm here to answer any question you have regarding patent laws, rules, \
    and the entire Manual of Patent Examining Procedure.")
main.markdown("##### How may I help you today?")
main.markdown("")


prompt_template = """
    # Persona
    You are an expert patent lawyer. You have deep knoeledge of the patent laws and regulations in the United States. \
    as well as the procedures and requirements for submitting a patent application to the United States Patent and Trademark Office.

    # Task
    Answer the query of the user using your knowledge base. Always refer to your knowledge base when answering the user's query. \
    If the answer to the user's query is not in your knowledge base, say you don't know, do not make something up. \
    You can ask the user for more information if you need it to answer the query. Answer the user's query in a clear, \
    complete and concise manner, make sure you have given a full answer.

    # Important rules
    - Always refer to your knowledge base before answering the user's query.
    - If there's no answer in your knowledge base, say you don't know, do not make something up.
    - Ask the user for more information if you need it to answer the query.
    - Answer the user's query in a clear, complete and concise manner, make sure you have given a full answer.
    - If you can, add a reference to the source of the information you provide.

    'query': {query}
    'knowledge_base': {knowledge_base}
    """


response_url = "https://patent-chat-bot-qa-2dkcwif5ra-ew.a.run.app/response"
save_chat_history_url = "https://patent-chat-bot-qa-2dkcwif5ra-ew.a.run.app/save_chat_history"
load_chat_history_url = "https://patent-chat-bot-qa-2dkcwif5ra-ew.a.run.app/load_chat_history"


# Load previous conversations
if "previous_conversations" not in st.session_state:
    loading_status = requests.get(load_chat_history_url)
    if loading_status.status_code == 200:
        st.session_state.previous_conversations = loading_status.json()
    else:
        st.error("Failed to load previous conversations")

# Display previous conversations on app rerun
for k, v in st.session_state.previous_conversations.items():
    if left.button(k):
        if "messages" in st.session_state: # In case there are messages in the current session
            st.session_state.messages = v
            st.session_state.start_time = k
        else: # In case there are no messages in the current session
            st.session_state.messages = v


# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": prompt_template}]

# Display chat messages from history on app rerun
for i, message in enumerate(st.session_state.messages):
    if i != 0:
        if message["role"] == "user":
            with main:
                with st.chat_message(message["role"], avatar="images/Ariel_Averbuch_avatar.jpg"):
                    st.markdown(message["content"])
        else:
            with main:
                with st.chat_message(message["role"], avatar="images/patent_lawyer_avatar.jpg"):
                    st.markdown(message["content"])

# Accept user input
query = st.chat_input("What is your question?")
with main:
    # query = st.chat_input("What is your question?")

    if query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user", avatar="images/Ariel_Averbuch_avatar.jpg"):
            st.markdown(query)

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar="images/patent_lawyer_avatar.jpg"):

            def fetch_response(response_url, query, messages):
                payload = {
                    "query": query,
                    "messages": messages  # Send entire chat history
                }

                response = requests.post(response_url, json=payload, stream=True)

                def stream():
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk.decode("utf-8")  # Decode and stream response

                return stream

            ai_response = st.write_stream(fetch_response(response_url, query, st.session_state.messages))

        st.session_state.messages.append({"role": "assistant", "content": ai_response})


        # Send the chat history to the backend
        payload = {
            "chat_history": st.session_state.messages,
            "start_time": st.session_state.start_time
        }
        response = requests.post(save_chat_history_url, json=payload)
