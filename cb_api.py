from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import initialize_agent, AgentType
from langchain_cohere import ChatCohere
from langchain.tools import Tool
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from urllib.parse import quote
import os

app = FastAPI()

# Environment variables
SUPABASE_URL = "https://nizvcdssajfpjtncbojx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc"
COHERE_API_KEY = "8ueWFEgswEV04DUHCsnpIiFqYDeD35e4BPs8sepl"
SUPABASE_PASSWORD = "SupaBase@Ishanya@Team_2"

# Initialize database connection
#db = SQLDatabase.from_uri(
#    f"postgresql://postgres:{quote(str(SUPABASE_PASSWORD), safe='')}@db.{SUPABASE_URL.split('//')[-1]}:6543/postgres"
#)

db = SQLDatabase.from_uri(
    f"postgresql://postgres.nizvcdssajfpjtncbojx:{quote(str(SUPABASE_PASSWORD), safe='')}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
)


db_chain = SQLDatabaseChain.from_llm(
    llm=ChatCohere(cohere_api_key=COHERE_API_KEY),
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
llm = ChatCohere(cohere_api_key=COHERE_API_KEY, temperature=0)
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
        f"""You are an SQL Agent interacting with a database. 
        
        Ensure all queries respect foreign key constraints, data types, and relationships.
        Ensure all SQL queries adhere to these constraints given below and relationships while fetching, inserting, updating, or deleting records..
        Ensure SQL queries use parameterized placeholders (:teacher_employee_id) instead of raw values.
        You must also adhere to role-based access permissions.
        
        The user has one of the following roles: (Acess Level | Access Name | Access Description)
        1. **Admin** – Can view all data without restrictions.
        2. **HR** – Can view everything related to all Teachers and Employees but cannot access Student-related data.
        3. **Teacher** – Can view all details related to Students who are assigned to the same program but cannot access unrelated Student, Employee, or Teacher data.
        
        Ensure that queries enforce these access rules by filtering data appropriately. If the user requests unauthorized information, respond with an error message instead of generating a query.

        Now, given the following access level : {request.user_access_level}, generate a valid SQL query that respects these permissions and display thhe results




        
        
        ### Database Schema:
        
        #### 1. students
        Stores information about students.
        
        - `id` (int, PRIMARY KEY)
        - `first_name` (text)
        - `last_name` (text)
        - `photo` (text)
        - `gender` (text)
        - `primary_diagnosis` (text)
        - `comorbidity` (text)
        - `student_id` (int, UNIQUE)
        - `enrollment_year` (int)
        - `status` (text)
        - `student_email` (text, UNIQUE)
        - `program_id` (int, FOREIGN KEY → programs.id)
        - `program_2_id` (int, FOREIGN KEY → programs.id)
        - `number_of_sessions` (int)
        - `timings` (text)
        - `day_of_week` (text)
        - `educator_employee_id` (int, FOREIGN KEY → employees.id)
        - `secondary_educator` (int, FOREIGN KEY → employees.id)
        - `session_type` (text)
        - `fathers_name` (text)
        - `mothers_name` (text)
        - `blood_group` (text)
        - `allergies` (text)
        - `contact_number` (text)
        - `alt_contact_number` (text)
        - `parents_email` (text)
        - `address` (text)
        - `transport` (text)
        - `strength` (text)
        - `weakness` (text)
        - `comments` (text)
        - `center_id` (int, FOREIGN KEY → centers.id)
        
        #### 2. educators
        Stores information about educators.
        
        - `id` (int, PRIMARY KEY)
        - `employee_id` (int, FOREIGN KEY → employees.id)
        - `name` (text)
        - `photo` (text)
        - `designation` (text)
        - `email` (text, UNIQUE)
        - `phone` (text, UNIQUE)
        - `date_of_birth` (date)
        - `date_of_joining` (date)
        - `work_location` (text)
        - `created_at` (timestamp)
        
        #### 3. employees
        Stores general employee information.
        
        - `id` (int, PRIMARY KEY)
        - `employee_id` (text, UNIQUE)
        - `name` (text)
        - `gender` (text)
        - `designation` (text)
        - `department` (text)
        - `employment_type` (text)
        - `email` (text, UNIQUE)
        - `phone` (text, UNIQUE)
        - `date_of_birth` (date)
        - `date_of_joining` (date)
        - `date_of_leaving` (date)
        - `status` (text)
        - `work_location` (text)
        - `emergency_contact` (text)
        - `blood_group` (text)
        - `created_at` (timestamp)
        - `center_id` (int, FOREIGN KEY → centers.id)
        - `LOR` (text)
        - `password` (text)
        
        #### 4. employee_attendance
        Stores attendance records for employees.
        
        - `employee_id` (int, FOREIGN KEY → employees.id)
        - `date` (date)
        - `attendance` (bool)
        
        #### 5. student_attendance
        Stores attendance records for students.
        
        - `program_id` (int, FOREIGN KEY → programs.id)
        - `student_id` (int, FOREIGN KEY → students.id)
        - `date` (date)
        - `attendance` (bool)
        
        #### 6. programs
        Stores information about programs.
        
        - `id` (int, PRIMARY KEY)
        - `program_id` (text, UNIQUE)
        - `name` (text)
        - `num_of_student` (int)
        - `num_of_educator` (int)
        - `center_id` (int, FOREIGN KEY → centers.id)
        - `created_at` (timestamp)
        - `start_date` (date)
        - `end_date` (date)
        
        #### 7. centers
        Stores information about different centers.
        
        - `id` (int, PRIMARY KEY)
        - `center_id` (text, UNIQUE)
        - `name` (text)
        - `num_of_student` (int)
        - `num_of_educator` (int)
        - `num_of_employees` (int)
        - `location` (text)
        - `created_at` (timestamp)
        
        #### 8. reports
        Stores reports generated by educators or employees.
        
        - `id` (int, PRIMARY KEY)
        - `generated_by` (int, FOREIGN KEY → employees.id)
        - `student_id` (int, FOREIGN KEY → students.id)
        - `report_type` (json)
        - `content` (text)
        - `created_at` (timestamp)
        
        #### 9. announcements
        Stores announcements made by administrators.
        
        - `announcement_id` (int, PRIMARY KEY)
        - `admin_id` (int, FOREIGN KEY → employees.id)
        - `announcement` (text)
        - `created_at` (timestamp)
        - `title` (text)
        
        #### 10. goals_tasks
        Stores tasks assigned to students.
        
        - `task_id` (int, PRIMARY KEY)
        - `student_id` (int, FOREIGN KEY → students.id)
        - `assigned_by` (int, FOREIGN KEY → employees.id)
        - `description` (text)
        - `due_date` (date)
        - `status` (text)
        - `created_at` (timestamp)
        - `feedback` (text)
        - `program_id` (int, FOREIGN KEY → programs.id)
        
        ### Relationships:
        - Each student belongs to **one or two programs**.
        - Each educator is also an **employee**.
        - Attendance records link students and employees to their respective programs.
        - Announcements are made by **admins** (who are employees).
        
        
    
        """
        )
        response = agent.invoke(user_query)
        return {"response": response.get('output', "No response")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
