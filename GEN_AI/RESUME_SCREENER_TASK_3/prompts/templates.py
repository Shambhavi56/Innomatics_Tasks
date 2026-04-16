from langchain_core.prompts import PromptTemplate

SCREENING_PROMPT = """
You are an expert technical recruiter.

Your task is to evaluate a candidate strictly based on the resume.

Job Description:
{job_description}

Candidate Resume:
{resume}

Follow these steps:
1. Extract:
   - Skills
   - Experience
   - Tools
2. Compare with job requirements
3. Assign a fit score (0–100)
4. Explain reasoning clearly

STRICT RULES:
- Do NOT hallucinate skills
- If missing skills → reduce score
- Keep explanation concise (3–4 lines max)

Return ONLY valid JSON:

{{
    "extracted_data": {{
        "skills": [],
        "experience": "",
        "tools": []
    }},
    "fit_score": 0,
    "explanation": ""
}}
"""

screening_prompt_template = PromptTemplate(
    input_variables=["job_description", "resume"],
    template=SCREENING_PROMPT,
)