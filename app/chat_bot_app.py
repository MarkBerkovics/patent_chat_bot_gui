import streamlit as st
# from dotenv import load_dotenv
import requests


# load_dotenv()

st.title("Patent laws and rules expert")

st.image("images/patent_lawyer.jpg", width=300)

st.markdown("##### Hi Ariel, I'm here to answer any question you have regarding patent laws, rules, \
    and the entire Manual of Patent Examining Procedure.")
st.markdown("##### How may I help you today?")
st.markdown("")

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


url = "http://127.0.0.1:8000/response"

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
            with st.chat_message(message["role"], avatar="images/Ariel_Averbuch_avatar.jpg"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar="images/patent_lawyer_avatar.jpg"):
                st.markdown(message["content"])

# Accept user input
query = st.chat_input("What is your question?")
if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    # Display user message in chat message container
    with st.chat_message("user", avatar="images/Ariel_Averbuch_avatar.jpg"):
        st.markdown(query)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="images/patent_lawyer_avatar.jpg"):

        def fetch_response(url, query, messages):
            payload = {
                "query": query,
                "messages": messages  # Send entire chat history
            }

            response = requests.post(url, json=payload, stream=True)

            def stream():
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk.decode("utf-8")  # Decode and stream response

            return stream

        ai_response = st.write_stream(fetch_response(url, query, st.session_state.messages))

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
