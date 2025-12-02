import os
import uuid
import shutil
import tifffile
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
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

@app.get("/debug_canvas")
def debug_canvas():
    return FileResponse("debug_canvas.html", media_type="text/html")

@app.get('/file/{filename}')
def get_file(filename: str):
    """Returns the file's metadata"""
    path = Path('./data/' + filename)
    print('looking for', path)

    if not path.exists():
        print('ERROR: Could not find', path)
        return JSONResponse({'error': 'File not found'}, status_code=404)
    
    img = tifffile.memmap(path).squeeze()

    metadata = {
        'shape': img.shape,
        'dtype': str(img.dtype),
    }

    return JSONResponse(metadata)

@app.get('/filenames')
def get_files():
    """Returns a list of all possible files that can be retrieved"""
    root = Path('./data')
    
    names = []
    for path in root.glob('.*'):
        if path.is_dir():
            names.append(path.name[1:]) # remove the '.' at the beginning

    return names

#
#   Tiles
#

@app.get('/tile/{filename}/{tilekey}')
def get_tiles(filename: str, tilekey: str):
    from fastapi.responses import Response
    
    root = Path('./data')
    filedir = root / f'.{Path(filename).stem}'
    filepath = filedir / (tilekey + '.tif')

    if not filedir.exists() or not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    img = tifffile.imread(filepath)
    return Response(content=img.tobytes(), media_type="application/octet-stream")


'''
Notes 11/20/25
### Sessions
 - When you navigate to */session/{id}, it either loads a pre-existing one, or it inits a new one
 - A session simply points to pre-existing assets. That is, assets are reused across sessions
 - Assets are loaded as lazily as possible:
    - Pyramids are generated only for current zplane
    - Given that pyramids are 'invisible', should there be an entirely new table for them, or simply a hidden folder at the same level, checked during runtime?
    - 
'''