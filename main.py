import os
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    """
    Accepts a blood smear image and returns a mock malaria prediction.
    This placeholder simulates model latency and returns a deterministic
    confidence based on file size so the demo feels realistic without a model.
    """
    try:
        if image.content_type not in {"image/png", "image/jpeg", "image/jpg", "image/webp"}:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        start = time.perf_counter()
        content = await image.read()
        file_size = len(content)

        # Simple deterministic heuristic for demo purposes
        # Map file size to a confidence score between 0.65 and 0.99
        base = (file_size % 100000) / 100000.0
        confidence = 0.65 + (0.34 * base)

        # Alternate label based on parity to show variability
        label = "Malaria Detected" if (file_size % 2 == 0) else "No Malaria Detected"

        # Simulate processing time (80-180ms)
        time.sleep(0.08 + (file_size % 100) / 1000.0)
        duration = (time.perf_counter() - start) * 1000

        return JSONResponse(
            {
                "label": label,
                "confidence": round(confidence, 3),
                "processing_ms": int(duration),
                "file_size": file_size,
                "model": "demo-vgg16-emulator",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)[:120]}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
