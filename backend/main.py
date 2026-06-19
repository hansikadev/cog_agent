import uuid
import traceback
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from backend.services.pdf_service import extract_text_from_pdf
from backend.services.claim_extractor import extract_claims_from_text
from backend.services.verifier import verify_claim

app = FastAPI(title="Fact-Check Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for jobs since we removed SQLite
jobs: Dict[str, Any] = {}

def process_document_background(job_id: str, file_bytes: bytes):
    try:
        # 1. Extract text
        text = extract_text_from_pdf(file_bytes)
        print(f"[{job_id}] PDF text extracted: {len(text)} characters")
        
        # 2. Extract claims
        claims = extract_claims_from_text(text)
        print(f"[{job_id}] Claims extracted: {len(claims)} claims found")
        
        jobs[job_id]["total_claims"] = len(claims)
        jobs[job_id]["claims"] = []
        jobs[job_id]["status"] = "EXTRACTED"
        print(f"[{job_id}] Status set to EXTRACTED with {len(claims)} claims")
        
        # 3. Verify each claim
        for idx, claim in enumerate(claims):
            result = verify_claim(claim)
            print(f"[{job_id}] Verified claim {idx+1}/{len(claims)}: {claim.claim_text[:50]}...")
            
            jobs[job_id]["claims"].append({
                "original_claim": claim.model_dump(),
                "status": result.status.value,
                "confidence_score": result.confidence_score,
                "correct_value": result.correct_value,
                "explanation": result.explanation,
                "evidence_sources": [e.model_dump() for e in result.evidence_sources]
            })
            jobs[job_id]["verified_count"] = len(jobs[job_id]["claims"])
            
        jobs[job_id]["status"] = "COMPLETED"
        print(f"[{job_id}] Processing COMPLETED. Total claims: {len(claims)}, Verified: {len(jobs[job_id]['claims'])}")
        
    except Exception as e:
        print(f"Background task failed: {e}")
        traceback.print_exc()
        if job_id in jobs:
            jobs[job_id]["status"] = "FAILED"
            jobs[job_id]["error"] = str(e)

@app.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    jobs[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "status": "PROCESSING",
        "progress": "0/0",
        "total_claims": 0,
        "verified_count": 0,
        "claims": []
    }
    
    background_tasks.add_task(process_document_background, job_id, file_bytes)
    
    return {"job_id": job_id, "message": "Document uploaded and processing started."}

@app.get("/api/status/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    progress = f"{job.get('verified_count', 0)}/{job.get('total_claims', 0)}" if job.get('total_claims', 0) > 0 else "Extracting claims..."
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "status": job["status"],
        "progress": progress
    }

@app.get("/api/report/{job_id}")
def get_report(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs[job_id]
    
    verified_count = sum(1 for c in job["claims"] if c["status"] == "VERIFIED")
    inaccurate_count = sum(1 for c in job["claims"] if c["status"] == "INACCURATE")
    false_count = sum(1 for c in job["claims"] if c["status"] == "FALSE")
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "total_claims": job["total_claims"],
        "verified_count": verified_count,
        "inaccurate_count": inaccurate_count,
        "false_count": false_count,
        "claims": job["claims"]
    }
