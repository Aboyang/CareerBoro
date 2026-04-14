# from utils.pdf_to_string import pdf_to_string
# from agent.model import model

# class ResumeService:

#     def __init__(self):
#         self.resume_string = ""

#     def parsed_resume(self):
#         print(">>> Extracting information from resume string...")
#         prompt = f"""
#         You are a resume analysis expert.

#         Resume:
#         {self.resume_string}

#         ----------------------------------

#         1. University: Name of the university attended.
#         2. Grade: Overall academic grade or GPA.
#         3. Career Experience: A list of all relevant work experiences. For each experience, include:
#            - role: Job title or position
#            - description: 1-2 sentence summary of responsibilities and achievements
#            - date: Start and end dates (month/year or year)
#         4. Project Experience: A list of all relevant projects. For each project, include:
#            - role: Role in the project
#            - description: 1-2 sentence summary of the project and your contribution
#            - date: Start and end dates (month/year or year)
#         5. Technical Skillset: List all technical skills (programming, software, tools) mentioned.
#         6. Softskill Displayed: List all soft skills (communication, leadership, teamwork, problem-solving, etc.) demonstrated.

#         ----------------------------------

#         Return the result in the following **JSON format ONLY**:

#         {{
#             "University": "",
#             "Grade": "",
#             "Career Experience": [
#                 {{"role": "", "description": "", "date": ""}}
#             ],
#             "Project Experience": [
#                 {{"role": "", "description": "", "date": ""}}
#             ],
#             "Technical Skillset": [],
#             "Softskill Displayed": []
#         }}
#         """

#         response = model.invoke(prompt)
#         return response.content

#     def extract_resume_context(self, pdf_bytes):
#         self.resume_string = pdf_to_string(pdf_bytes)
#         return self.parsed_resume()


import boto3
import uuid
from utils.pdf_to_string import pdf_to_string
from agent.model import model

# ── S3 config ─────────────────────────────────────────────────────────────────
S3_BUCKET = "career-boro-resume"
S3_PREFIX = "resumes/"
S3_REGION = "ap-southeast-1"

s3_client = boto3.client("s3", region_name=S3_REGION)

class ResumeService:

    def __init__(self):
        self.resume_string = ""

    def _upload_to_s3(self, pdf_bytes: bytes, original_filename: str) -> str:
        """Upload raw PDF bytes to S3. Returns the S3 key."""
        key = f"{S3_PREFIX}{uuid.uuid4()}_{original_filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        print(f">>> Uploaded resume to S3: s3://{S3_BUCKET}/{key}")
        return key

    def parsed_resume(self):
        print(">>> Extracting information from resume string...")
        prompt = f"""
        You are a resume analysis expert.

        Resume:
        {self.resume_string}

        ----------------------------------

        1. University: Name of the university attended.
        2. Grade: Overall academic grade or GPA.
        3. Career Experience: A list of all relevant work experiences. For each experience, include:
           - role: Job title or position
           - description: 1-2 sentence summary of responsibilities and achievements
           - date: Start and end dates (month/year or year)
        4. Project Experience: A list of all relevant projects. For each project, include:
           - role: Role in the project
           - description: 1-2 sentence summary of the project and your contribution
           - date: Start and end dates (month/year or year)
        5. Technical Skillset: List all technical skills (programming, software, tools) mentioned.
        6. Softskill Displayed: List all soft skills (communication, leadership, teamwork, problem-solving, etc.) demonstrated.

        ----------------------------------

        Return the result in the following **JSON format ONLY**:

        {{
            "University": "",
            "Grade": "",
            "Career Experience": [
                {{"role": "", "description": "", "date": ""}}
            ],
            "Project Experience": [
                {{"role": "", "description": "", "date": ""}}
            ],
            "Technical Skillset": [],
            "Softskill Displayed": []
        }}
        """

        response = model.invoke(prompt)
        return response.content

    def extract_resume_context(self, pdf_bytes: bytes, original_filename: str = "resume.pdf"):
        """
        1. Upload the raw PDF to S3 for storage.
        2. Parse the PDF text locally.
        3. Run LLM extraction and return structured JSON string.
        """
        self._upload_to_s3(pdf_bytes, original_filename)
        self.resume_string = pdf_to_string(pdf_bytes)
        return self.parsed_resume()