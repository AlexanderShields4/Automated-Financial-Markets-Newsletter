import os
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

# Fallback to st.secrets for cloud deployment
if not supabase_url:
    try: supabase_url = st.secrets["SUPABASE_URL"]
    except: pass
if not supabase_key:
    try: supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
    except: pass

if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Supabase init error: {e}")
        supabase = None
else:
    supabase = None

# Initialize Gemini
api_key = os.getenv("RAG_BOT_KEY") or os.getenv("GOOGLE_KEY")
embedding_key = os.getenv("GOOGLE_EMBEDDING_KEY") or os.getenv("GOOGLE_KEY")

# Fallback to st.secrets
if not api_key:
    try: api_key = st.secrets["RAG_BOT_KEY"]
    except: 
        try: api_key = st.secrets["GOOGLE_KEY"]
        except: pass

if not embedding_key:
    try: embedding_key = st.secrets["GOOGLE_EMBEDDING_KEY"]
    except:
        try: embedding_key = st.secrets["GOOGLE_KEY"]
        except: pass

if api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
else:
    llm = None

if embedding_key:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=embedding_key
    )
else:
    embeddings = None

def query_market_history(question: str):
    """
    RAG function to answer user questions about market history using Supabase and Gemini.
    """
    if not supabase:
        return "System Error: Supabase credentials missing. Please configure secrets."
    if not llm or not embeddings:
         return "System Error: Google API keys missing. Please configure secrets."

    try:
        # 1. Generate embedding for the question
        query_vector = embeddings.embed_query(question)
        
        # 2. Search Supabase for similar newsletters
        response = supabase.rpc(
            'match_daily_briefs',
            {
                'query_embedding': query_vector,
                'match_threshold': 0.3, # Lowered threshold for broader matching
                'match_count': 5
            }
        ).execute()
        
        matches = response.data
        # print(f"Found {len(matches)} matches") # Debug log
        
        context_text = ""
        if matches:
            for match in matches:
                date = match.get('date', 'Unknown Date')
                content = match.get('full_text', '')
                context_text += f"\n--- Date: {date} ---\n{content}\n"
        else:
            context_text = "No relevant historical market data found."

        # 3. Generate Answer
        template = """You are a financial analyst assistant. Use the following historical market contexts to answer the user's question.
        If the answer is not in the context, say you don't have that information.

        Context:
        {context}

        Question: {question}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        
        answer = chain.invoke({"context": context_text, "question": question})
        
        return answer

    except Exception as e:
        return f"Error querying market history: {str(e)}"
