from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import easyocr
import pandas as pd

app = FastAPI()


# ✅ Initialize OCR model
reader = easyocr.Reader(['en'],gpu=False)




def create_excel(data):
    # Convert dict to table format
    rows = []
    
    for key, value in data.items():
        rows.append({
            "Test": key.capitalize(),
            "Value": value
        })

    df = pd.DataFrame(rows)

    file_path = "report.xlsx"
    df.to_excel(file_path, index=False)

    return file_path

def is_number(text):
    text = text.replace(",", ".")
    
    # remove units
    text = text.replace("g/dl", "").replace("mg/dl", "").strip()

    try:
        float(text)
        return True
    except:
        return False

def extract_medical_data(text_list):
    data = {}

    # Normalize text
    text_list = [t.lower().strip() for t in text_list if t.strip() != ""]

    for i, word in enumerate(text_list):

        # Look ahead up to 3 positions
        for j in range(1, 4):
            if i + j < len(text_list):
                next_word = text_list[i + j]

                if is_number(next_word):
                    value = next_word.replace(",", ".")
                    value = value.replace("g/dl", "").replace("mg/dl", "").strip()

                    # Hemoglobin
                    if "hemoglobin" in word or word == "hb":
                        data["hemoglobin"] = value

                    # RBC
                    if "rbc" in word:
                        data["rbc"] = value

                    # WBC
                    if "wbc" in word:
                        data["wbc"] = value

                    # Platelet
                    if "platelet" in word:
                        data["platelet"] = value
                        
                    # Add inside your loop

                    # MCV
                    if "mcv" in word:
                        data["mcv"] = value

                    # MCH
                    if "mch" in word:
                        data["mch"] = value

                    # MCHC
                    if "mchc" in word:
                        data["mchc"] = value

                    # RDW
                    if "rdw" in word:
                     data["rdw"] = value

                    break  # stop after finding first number

    return data


@app.get("/")
def home():
    return {"message": "Backend with OCR + Extraction running 🚀"}


@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):

    # ✅ Save uploaded file
    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ OCR
    results = reader.readtext(file_location)
    extracted_text = [text for (_, text, _) in results]

    # ✅ Extraction logic
    structured_data = extract_medical_data(extracted_text)

    excel_file = create_excel(structured_data)

    return FileResponse(
        path=excel_file,
        filename="report.xlsx",
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      )