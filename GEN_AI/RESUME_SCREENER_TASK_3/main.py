from chains.resume_chain import get_screening_chain, run_screening

job_description = """
Data Scientist role requiring 3+ years of experience.
Must have Python, Machine Learning, SQL, Deep Learning.
Nice to have: LangChain, NLP, AWS.
"""

resumes = {
    "Strong": "5 years Data Scientist. Python, SQL, ML, DL. NLP with LangChain, deployed on AWS.",
    "Average": "2 years Data Analyst. Python, SQL. Some ML models. Learning LangChain.",
    "Weak": "Biology graduate. Lab experience. Excel. No coding."
}


def main():
    chain = get_screening_chain()

    for label, resume in resumes.items():
        print(f"\n--- {label} Candidate ---")

        response = run_screening(
            chain,
            job_description,
            resume,
            config={
                "tags": [label.lower()],
                "run_name": "candidate_evaluation"
            }
        )

        print("Score :", response["fit_score"])
        print("Skills:", response["extracted_data"]["skills"])
        print("Why   :", response["explanation"])


if __name__ == "__main__":
    main()