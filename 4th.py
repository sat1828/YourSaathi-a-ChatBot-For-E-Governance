import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Streamlit UI
st.title("✨🤖YOUR SAATHI")
st.write("Ask me anything about citizenship FAQs and records!")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Use free Hugging Face embeddings
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    st.error(f"Failed to initialize embeddings: {str(e)}")
    st.stop()

# Load or create FAISS vector store
faiss_index_path = "./faiss_index"
docs = []  # To store all documents (from both txt and Excel)

# Load citizenship FAQs from text file
faqs_file = "citizenship_faqs.txt"
if not os.path.exists(faqs_file):
    st.error(f"File '{faqs_file}' not found! Please ensure it exists in the project directory.")
    st.stop()

try:
    with open(faqs_file, "r", encoding="utf-8") as f:
        faqs_text = f.read()
except Exception as e:
    st.error(f"Failed to read '{faqs_file}': {str(e)}")
    st.stop()

faqs = [faq.strip() for faq in faqs_text.split("\n") if faq.strip()]
if not faqs:
    st.error("No FAQs found in 'citizenship_faqs.txt'. Please add some content.")
    st.stop()

# Add text file FAQs to documents
for faq in faqs:
    docs.append(Document(page_content=faq, metadata={"source": faqs_file}))

# Load data from combined Excel file
excel_file = "citizenship.xlsx"  # Update this to your Excel file path
if not os.path.exists(excel_file):
    st.error(f"Excel file '{excel_file}' not found! Please ensure it exists in the project directory.")
    st.stop()

try:
    # Read all sheets from the Excel file
    excel_data = pd.read_excel(excel_file, sheet_name=None)
    for sheet_name, df in excel_data.items():
        # Convert each row to a string for embedding
        for _, row in df.iterrows():
            # Combine all columns into a single string (you can customize this based on your data)
            row_text = " ".join(str(value) for value in row.values if pd.notna(value))
            if row_text.strip():
                docs.append(Document(page_content=row_text, metadata={"source": f"{excel_file}_{sheet_name}"}))
except Exception as e:
    st.error(f"Failed to read Excel file '{excel_file}': {str(e)}")
    st.stop()

# Create or load FAISS index
if os.path.exists(faiss_index_path):
    try:
        vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        # Add new documents to existing index (if needed)
        if docs:
            vectorstore.add_documents(docs)
            vectorstore.save_local(faiss_index_path)
            st.success("Updated FAISS index with new documents!")
    except Exception as e:
        st.error(f"Failed to load FAISS index: {str(e)}")
        st.stop()
else:
    if not docs:
        st.error("No documents to index from text or Excel files!")
        st.stop()
    try:
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(faiss_index_path)
        st.success("FAISS index created and saved successfully!")
    except Exception as e:
        st.error(f"Failed to create FAISS index: {str(e)}")
        st.stop()

# Initialize Groq client with API key
groq_api_key = "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"
if not groq_api_key:
    st.error("GROQ_API_KEY not found in environment variables!")
    st.stop()

try:
    llm = ChatGroq(
    api_key=groq_api_key,
    model_name="llama3-8b-8192"  # Updated model
)

except Exception as e:
    st.error(f"Failed to initialize Groq LLM: {str(e)}")
    st.stop()

try:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )
except Exception as e:
    st.error(f"Failed to create RetrievalQA chain: {str(e)}")
    st.stop()

# Streamlit Chat UI
user_input = st.text_input("Enter your question about citizenship:")

if user_input:
    try:
        response = qa_chain.invoke({"query": user_input})["result"]
        st.session_state.chat_history.append({"user": user_input, "bot": response})
        st.write("🤖 Chatbot Answer: ", response)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Display chat history
for chat in st.session_state.chat_history:
    st.write(f"**You:** {chat['user']}")
    st.write(f"**Bot:** {chat['bot']}")
    st.write("---")