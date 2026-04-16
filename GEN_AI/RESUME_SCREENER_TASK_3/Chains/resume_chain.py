from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.output_parsers import StrOutputParser
from prompts.templates import screening_prompt_template
from utils.parser import parse_json_safely
from config.settings import HF_TOKEN, MODEL_REPO, MODEL_CONFIG


def get_llm():
    llm = HuggingFaceEndpoint(
        repo_id=MODEL_REPO,
        task="conversational",
        huggingfacehub_api_token=HF_TOKEN,
        **MODEL_CONFIG
    )

    return ChatHuggingFace(llm=llm)


def get_screening_chain():
    llm = get_llm()

    chain = (
        screening_prompt_template
        | llm
        | StrOutputParser()
    )

    return chain


def run_screening(chain, job_description, resume, config=None):
    raw_output = chain.invoke(
        {
            "job_description": job_description,
            "resume": resume
        },
        config=config or {"run_name": "resume_screening"}
    )

    return parse_json_safely(raw_output)