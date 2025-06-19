from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_community import GoogleDriveLoader
import gspread
from google.oauth2.credentials import Credentials
import json

with open("google_token.json") as f:
    creds_data = json.load(f)
creds = Credentials.from_authorized_user_info(creds_data)

gc = gspread.authorize(creds)
sh = gc.open_by_key("1k98KNtFJ8mciv07xIw8bXz7BT9GCzDMF8XvCFAJthyk")
worksheet = sh.worksheet("Sheet1")

rows = worksheet.get_all_values()  # All data as list of rows

# Extract the first non-empty row
for row in rows:
    if any(cell.strip() for cell in row):
        sheet_content = " | ".join(row)
        break
else:
    sheet_content = "No data found."

load_dotenv()

loader = GoogleDriveLoader(
    folder_id="1rMCI28kcRS9BR7IH6nc7ErSQmaD9hHya",
    file_types=["sheet"],
    recursive=False,
    token_path="google_token.json",
)

docs = loader.load()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

app = FastAPI()

@app.get("/")
def read_root():
    return {"content": sheet_content}
