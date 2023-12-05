from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import csv
import io

from crud import create_user
from database import SessionLocal, engine, get_db
from models import Base
from schemas import UserCreate
import chardet



app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>CSV Upload</title>
        </head>
        <body>
            <form action="/uploadfile/" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <button type="submit">Upload CSV</button>
            </form>
        </body>
    </html>
    """




@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_content = await file.read()
    result = chardet.detect(raw_content)
    encoding = result['encoding'] or 'utf-8'
    decoded_content = raw_content.decode(encoding, errors='replace')

    csv_reader = csv.reader(io.StringIO(decoded_content))
    header = next(csv_reader)
    required_columns = ["Name", "Age"]
    missing_columns = [col for col in required_columns if col not in header]

    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing_columns)}")

    try:
        name_column = header.index("Name")
        age_column = header.index("Age")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error finding column indices: {e}")

    for row in csv_reader:
        try:
            if row[age_column]:
                user_data = {"name": row[name_column], "age": int(row[age_column])}
                create_user(db, UserCreate(**user_data))
        except (ValueError, IndexError) as e:
            raise HTTPException(status_code=400, detail=f"Error processing row: {e}")

    return {"filename": file.filename, "name_column": name_column, "age_column": age_column, "encoding": encoding}
 
