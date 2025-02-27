# from fastapi import FastAPI, File, UploadFile, HTTPException

# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Enable CORS for requests from your React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Allow frontend access
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )

# import json
# import os
# from openai import OpenAI
# from dotenv import load_dotenv
# from pydantic import BaseModel
# import numpy as np
# from PIL import Image
# import pytesseract
# import io

# # Load API key from .env file
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# if not api_key:
#     raise RuntimeError("Missing OpenAI API key. Set OPENAI_API_KEY in the environment.")

# # Initialize OpenAI client
# client = OpenAI(api_key=api_key)

# class ReceiptText(BaseModel):
#     text: str

# def extract_text_from_image(image_bytes):
#     """Extracts text from an uploaded image using OCR (Tesseract)."""
#     try:
#         img = Image.open(io.BytesIO(image_bytes))
#         img_array = np.array(img)
#         text = pytesseract.image_to_string(img_array)
#         return text.strip()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")

# def parse_bill_with_chatgpt(text):
#     """Sends extracted receipt text to GPT for structured item parsing."""
#     prompt = f"""
#     You are an AI that extracts item names and prices from receipts.
#     Given the following text, extract a list of items and their corresponding prices, split items if there are duplicates and divide the price accordingly.

#     Text:
#     {json.dumps(text)}

#     Return the data as a JSON array where each item has "name" and "price" fields.
#     Example Output:
#     [
#         {{"name": "Apples", "price": 2.99}},
#         {{"name": "Apples", "price": 2.99}},
#         {{"name": "Milk", "price": 3.50}},
#         {{"name": "Bread", "price": 1.99}}
#     ]
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "system", "content": "You are an expert text parser."},
#                       {"role": "user", "content": prompt}],
#             temperature=0.2
#         )

#         extracted_data = response.choices[0].message.content.strip()
#         return json.loads(extracted_data)

#     except json.JSONDecodeError:
#         raise HTTPException(status_code=500, detail="Error parsing JSON response from OpenAI.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

# @app.post("/extract-text")
# async def extract_text(file: UploadFile = File(...)):
#     """Extracts text from an uploaded image using OCR (Tesseract)."""
#     image_bytes = await file.read()
#     extracted_text = extract_text_from_image(image_bytes)
#     return {"text": extracted_text}

# @app.post("/parse-receipt")
# async def parse_receipt(receipt: ReceiptText):
#     """Parses structured receipt data from extracted text."""
#     parsed_items = parse_bill_with_chatgpt(receipt.text)
#     return {"items": parsed_items}

# @app.post("/upload-and-parse")
# async def upload_and_parse(file: UploadFile = File(...)):
#     """Uploads a receipt image, extracts text using OCR, and then parses items with GPT."""
#     print('fdsjonbvjshdnbvs')
#     image_bytes = await file.read()
#     extracted_text = extract_text_from_image(image_bytes)
#     parsed_items = parse_bill_with_chatgpt(extracted_text)
#     return {"text": extracted_text, "items": parsed_items}

# # Run the API using Uvicorn
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from PIL import Image
import pytesseract
import io
import re

app = FastAPI()

# Enable CORS for requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend access
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class ReceiptText(BaseModel):
    text: str

def extract_text_from_image(image_bytes):
    """Extracts text from an uploaded image using OCR (Tesseract)."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        text = pytesseract.image_to_string(img_array)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")

def parse_receipt_text(text):
    """Parses receipt text for specific items from Tennis Ballerz Evanston."""
    try:
        items = []
        item_patterns = [
            (r"(\d+) Stringing Labor \$(\d+\.\d{2})", "Stringing Labor"),
            (r"(\d+) Premium String - Poly or \$(\d+\.\d{2})", "Premium String - Poly or Multi"),
        ]
        
        for pattern, name in item_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    qty, price = match.groups()
                    for _ in range(int(qty)):
                        items.append({"name": name, "price": float(price) / 2})
                else:
                    price = match.group(1)
                    items.append({"name": name, "price": float(price)})
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing receipt text: {str(e)}")

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Extracts text from an uploaded image using OCR (Tesseract)."""
    image_bytes = await file.read()
    extracted_text = extract_text_from_image(image_bytes)
    return {"text": extracted_text}

@app.post("/parse-receipt")
async def parse_receipt(receipt: ReceiptText):
    """Parses structured receipt data from extracted text."""
    parsed_items = parse_receipt_text(receipt.text)
    return {"items": parsed_items}

@app.post("/upload-and-parse")
async def upload_and_parse(file: UploadFile = File(...)):
    """Uploads a receipt image, extracts text using OCR, and then parses items."""
    image_bytes = await file.read()
    extracted_text = extract_text_from_image(image_bytes)
    parsed_items = parse_receipt_text(extracted_text)
    return {"text": extracted_text, "items": parsed_items}

# Run the API using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)