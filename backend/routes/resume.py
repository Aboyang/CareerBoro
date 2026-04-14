from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services.resume import ResumeService

resume = ResumeService()

router = APIRouter(
    prefix="/resume",
    tags=["resume"]
)

@router.post("/")
async def get_resume_context(file: UploadFile = File(...)):

    print("File received: ", file)
    
    if not file.filename.endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed"}, status_code=400)

    pdf_bytes = await file.read()
    resume_context = resume.extract_resume_context(pdf_bytes)

    return { "resume_context": resume_context }
