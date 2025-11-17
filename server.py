import os
import uuid
import shutil
import tifffile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()
UPLOAD_DIR = "/Users/tony/projects/20251112_ergo_upload/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allow browser requests from local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Upload speed test
# ----------------------------------------------------------------------
@app.post("/speedtest")
async def speedtest(file: bytes = File(...)):
    return {"received": len(file)}

# ----------------------------------------------------------------------
# Start a new upload session
# ----------------------------------------------------------------------
@app.post("/upload/init")
def init_upload():
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)
    return {"session_id": session_id}

# ----------------------------------------------------------------------
# Upload a chunk
# ----------------------------------------------------------------------
@app.put("/upload/{session_id}")
async def upload_chunk(
    session_id: str,
    part: int = Query(..., ge=0),
    chunk: UploadFile = File(...)
):
    session_path = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_path):
        return JSONResponse(status_code=404, content={"error": "Invalid session"})

    part_path = os.path.join(session_path, f"part_{part}")
    with open(part_path, "wb") as f:
        while data := await chunk.read(1024 * 1024):
            f.write(data)

    return {"status": "ok", "part": part}

# ----------------------------------------------------------------------
# Check which chunks exist (for resume support)
# ----------------------------------------------------------------------
@app.get("/upload/{session_id}/status")
def upload_status(session_id: str):
    session_path = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_path):
        return JSONResponse(status_code=404, content={"error": "Invalid session"})

    existing = sorted(
        [int(f.split("_")[1]) for f in os.listdir(session_path) if f.startswith("part_")]
    )
    return {"existing_parts": existing}

# ----------------------------------------------------------------------
# Complete the upload (combine chunks)
# ----------------------------------------------------------------------
@app.post("/upload/{session_id}/complete")
def complete_upload(session_id: str, filename: str):
    session_path = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_path):
        return JSONResponse(status_code=404, content={"error": "Invalid session"})

    final_path = os.path.join(UPLOAD_DIR, filename)
    with open(final_path, "wb") as outfile:
        for part_file in sorted(os.listdir(session_path), key=lambda x: int(x.split("_")[1])):
            part_path = os.path.join(session_path, part_file)
            with open(part_path, "rb") as pf:
                shutil.copyfileobj(pf, outfile)

    # Cleanup session directory
    shutil.rmtree(session_path)

    return {"status": "done", "file": filename}

# ----------------------------------------------------------------------
# Root - serve index.html
# ----------------------------------------------------------------------
@app.get("/")
def root():
    return FileResponse("index.html", media_type="text/html")

@app.get("/canvas")
def canvas():
    return FileResponse("canvas.html", media_type="text/html")

@app.get('/file')
def get_file(filepath: str):
    return Path(filepath).exists()