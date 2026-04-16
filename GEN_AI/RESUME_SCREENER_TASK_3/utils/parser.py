import json
import re

def parse_json_safely(text):
    """Robust JSON extraction from LLM output."""

    if isinstance(text, dict):
        return text

    if hasattr(text, "content"):
        text = text.content

    text = str(text)

    # Extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {
        "fit_score": None,
        "explanation": text,
        "extracted_data": {"skills": [], "experience": "", "tools": []},
    }