from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import initialize_agent, AgentType
from langchain_google_vertexai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from urllib.parse import quote
import os
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend domain(s) for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Environment variables
SUPABASE_URL = "https://nizvcdssajfpjtncbojx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc"
SUPABASE_PASSWORD = "SupaBase@Ishanya@Team_2"
GEMINI_API_KEY = "AIzaSyDOvCnh7ya7ARXpPeXs_1lI5goZg646xWA"

# Initialize database connection
db = SQLDatabase.from_uri(
    f"postgresql://postgres.nizvcdssajfpjtncbojx:{quote(str(SUPABASE_PASSWORD), safe='')}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
)

db_chain = SQLDatabaseChain.from_llm(
    llm=ChatGoogleGenerativeAI(model_name="gemini-pro", google_api_key=GEMINI_API_KEY),
    db=db,
    return_direct=True,
    verbose=True
)

def query_database(query: str):
    """Function to interact with Supabase using SQL queries."""
    print(f"Executing Query: {query}")
    result = db.run(query)
    print(f"Query Result: {result}")
    return result

tool = Tool(
    name="DatabaseQuery",
    func=query_database,
    description="Use this tool to query the Supabase database with SQL commands"
)

# Initialize LangChain agent
llm = ChatGoogleGenerativeAI(model_name="gemini-1.5-pro", google_api_key=GEMINI_API_KEY, temperature=0)
agent = initialize_agent(
    tools=[tool],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

class QueryRequest(BaseModel):
    user_access_level: int
    user_query: str

@app.post("/chatbot")
def chatbot(request: QueryRequest):
    try:
        user_query = request.user_query + (
        f"""You are an SQL Agent interacting with a database...
        (rest of your prompt remains unchanged)
        """
        )
        response = agent.run(user_query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
