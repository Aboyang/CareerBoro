from utils.pdf_to_string import pdf_to_string
from agent.model import model

class ResumeService:

    def __init__(self):
        self.resume_string = ""

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

    def extract_resume_context(self, pdf_bytes):
        self.resume_string = pdf_to_string(pdf_bytes)
        return self.parsed_resume()