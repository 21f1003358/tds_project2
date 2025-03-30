from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import zipfile, os, pandas as pd
import openai

app = FastAPI()

# Add your OpenAI key here or load it from env
openai.api_key = "YOUR_OPENAI_KEY"

@app.post("/api/")
async def answer_question(question: str = Form(...), file: UploadFile = File(None)):
    # Save uploaded file (if any)
    if file:
        with open(file.filename, "wb") as f:
            f.write(await file.read())
        # If ZIP, extract it
        if file.filename.endswith(".zip"):
            with zipfile.ZipFile(file.filename, 'r') as zip_ref:
                zip_ref.extractall("extracted")
            # Assume there's only one CSV
            for f in os.listdir("extracted"):
                if f.endswith(".csv"):
                    df = pd.read_csv(os.path.join("extracted", f))
                    if "answer" in df.columns:
                        return {"answer": str(df["answer"].iloc[0])}
    
    # If no file or no direct CSV answer, use LLM
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    answer = response.choices[0].message.content.strip()
    return {"answer": answer}
