from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

app = FastAPI()

@app.get("/")
def read_root():
    response = llm.invoke("Sing a ballad of LangChain.")
    return response
