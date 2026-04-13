from agent.model import model

class InterviewQuestionPreparer:
    def __init__(self, model_instance=None):
        self.model = model_instance if model_instance else model

    def prepare_questions(self, role, company, job_desc, resume_context):
        content = f'''
        You are an expert technical interviewer. 

        Candidate is interviewing for {role} at {company}.

        Your task is to prepare EXACTLY ONE high-quality interview question for EACH category below.

        Here is his Resume:
        {resume_context}

        This is the Job Description:
        {job_desc}

        ### QUESTION GUIDELINES

        1. Resume-related Question:
        - Focus on the candidate’s MOST relevant work experience or project
        - Ask about decisions made, challenges faced, or impact achieved

        2. Technical Question:
        - Must relate to the role requirements
        - Must reference technical skills or concepts listed in the resume
        - Test understanding, not trivia

        3. Behavioural Question:
        - Focus on attitude, leadership, teamwork, work ethic, adaptability, or growth mindset
        - Use real-world scenarios

        4. Company Question:
        - Evaluate how well the candidate has prepared
        - Focus on company knowledge, motivation, or alignment with the role

        ----------------------------------

        ### OUTPUT FORMAT (JSON ONLY, NO EXTRA TEXT)

        Return your answer in EXACTLY the following JSON structure:

        {{
        "question_resume": ["<one resume-related question>"],
        "question_technical": ["<one technical question>"],
        "question_behavioural": ["<one behavioural question>"],
        "question_company": ["<one company-related question>"]
        }}

        - Each list MUST contain EXACTLY ONE question
        - Do NOT include explanations or commentary
        - Do NOT include markdown or formatting
        '''

        result = self.model.invoke(content)

        return result.content