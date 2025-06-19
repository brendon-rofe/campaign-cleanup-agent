from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import json

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
creds = flow.run_local_server(port=0)

# Save token
with open("google_token.json", "w") as token_file:
    token_file.write(creds.to_json())

gc = gspread.authorize(creds)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

app = FastAPI()

@app.get("/analyze-emails")
def analyze_emails():
    sh = gc.open_by_key("1k98KNtFJ8mciv07xIw8bXz7BT9GCzDMF8XvCFAJthyk")
    input_sheet = sh.worksheet("Sheet1")
    output_sheet = sh.worksheet("Sheet2")

    input_rows = input_sheet.get_all_values()
    if not input_rows or len(input_rows[0]) < 2:
        return {"error": "Sheet1 must have 'Subject Line' and 'Body Text' columns."}

    header, *data_rows = input_rows

    results = []
    for subject, body in data_rows:
        prompt = f"""
Analyze the following email for seasonality or time-sensitive language.

Subject: {subject}
Body: {body}

Return your answer like this (pipe-separated):
Seasonal? (Yes/No) | Flagged Terms | Suggested Action
"""
        raw_response = (llm.invoke(prompt).content or "").strip()
        parts = [p.strip() for p in raw_response.split("|")]

        if len(parts) != 3:
            parts = ["Error", "Could not parse response", raw_response]

        results.append([subject] + parts)

    output_sheet.clear()
    output_sheet.append_row(["Subject Line", "Seasonal?", "Flagged Terms", "Suggested Action"])
    for row in results:
        output_sheet.append_row(row)

    return {"status": "success", "analyzed": len(results)}
