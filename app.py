import streamlit as st
import os
from crewai import Agent, Task, Crew
from dotenv import load_dotenv, find_dotenv
from crewai_tools import FileReadTool, ScrapeWebsiteTool, MDXSearchTool, SerperDevTool
import google.generativeai as genai
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    from langchain_community.chat_models import ChatGoogleGenerativeAI  # fallback for LC >= 0.2

# Load environment variables
def load_env():
    _ = load_dotenv(find_dotenv())

def get_google_api_key():
    load_env()
    return os.getenv("GOOGLE_API_KEY")

def get_serper_api_key():
    load_env()
    return os.getenv("SERPER_API_KEY")

# Set API keys and model for Gemini
os.environ["GOOGLE_API_KEY"] = get_google_api_key() or ""
os.environ["SERPER_API_KEY"] = get_serper_api_key() or ""

# Create a shared Gemini LLM instance
GEMINI_MODEL_NAME = "models/gemini-2.0-flash"  # Google calls require full path

gemini_llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL_NAME,
    temperature=0.2,
)

# Initialize session state
if "tailored_resume_content" not in st.session_state:
    st.session_state["tailored_resume_content"] = None
if "interview_prep_content" not in st.session_state:
    st.session_state["interview_prep_content"] = None

# Streamlit UI
st.title("Resume Customization and Interview Preparation Tool")

# User inputs
st.header("Step 1: Provide Required Details")
job_posting_url = st.text_input("Enter the Job Posting URL")
github_url = st.text_input("Enter Your GitHub Profile URL")
personal_writeup = st.text_area("Enter a Brief Personal Write-Up")

# Upload section
st.header("Step 2: Upload Your Resume")
uploaded_file = st.file_uploader("Upload your Markdown Resume file (.md)", type=["md"])

# Process the file
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("Uploaded Resume Content", file_content, height=300)

    if st.button("Generate Tailored Resume and Interview Prep"):
        # Save the uploaded file temporarily
        with open("uploaded_resume.md", "w") as f:
            f.write(file_content)

        # Define agents and tasks
        search_tool = SerperDevTool()
        scrape_tool = ScrapeWebsiteTool()
        read_resume = FileReadTool(file_path="uploaded_resume.md")
        semantic_search_resume = MDXSearchTool(mdx="uploaded_resume.md")

        researcher = Agent(
            role = "Tech Job Researcher",
            goal = """Make sure to do amazing analysis on
                    job posting to help job applicants""",
            tools = [scrape_tool, search_tool],
            llm = gemini_llm,
            verbose=True,
            backstory = """
            As a Job Researcher, your prowess in
            navigating and extracting critical
            information from job postings is unmatched.
            Your skills help pinpoint the necessary
            qualifications and skills sought
            by employers, forming the foundation for
            effective application tailoring.
            """
        )

        profiler = Agent(
            role="Personal Profiler for Engineers",
            goal=(
                "Do incredible research on job applicants "
                "to help them stand out in the job market"
            ),
            tools=[scrape_tool, search_tool, read_resume, semantic_search_resume],
            llm=gemini_llm,
            verbose=True,
            backstory=(
                "Equipped with analytical prowess, you dissect "
                "and synthesize information from diverse sources "
                "to craft comprehensive personal and professional profiles, "
                "laying the groundwork for personalized resume enhancements."
            )
        )

        resume_strategist = Agent(
            role="Resume Strategist for Engineers",
            goal="Find all the best ways to make a "
                 "resume stand out in the job market.",
            tools = [scrape_tool, search_tool,
                     read_resume, semantic_search_resume],
            llm=gemini_llm,
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you "
                "excel at refining resumes to highlight the most "
                "relevant skills and experiences, ensuring they "
                "resonate perfectly with the job's requirements."
            )
        )

        interview_preparer = Agent(
            role="Engineering Interview Preparer",
            goal="Create interview questions and talking points "
                 "based on the resume and job requirements",
            tools = [scrape_tool, search_tool,
                     read_resume, semantic_search_resume],
            llm=gemini_llm,
            verbose=True,
            backstory=(
                "Your role is crucial in anticipating the dynamics of "
                "interviews. With your ability to formulate key questions "
                "and talking points, you prepare candidates for success, "
                "ensuring they can confidently address all aspects of the "
                "job they are applying for."
            )
        )

        # Define tasks
        research_task = Task(
            description = """
            Analyze the job posting URL provided ({job_posting_url})
            to extract key skills, experiences, and qualifications
            required. Use the tools to gather content and identify
            and categorize the requirements.""",
            expected_output = """
            A structured list of job requirements, including necessary
            skills, qualifications, and experiences.""",
            agent = researcher,
            async_execution=True
        )

        profile_task = Task(
            description=(
                "Compile a detailed personal and professional profile "
                "using the GitHub ({github_url}) URLs, and personal write-up "
                "({personal_writeup}). Utilize tools to extract and "
                "synthesize information from these sources."
            ),
            expected_output=(
                "A comprehensive profile document that includes skills, "
                "project experiences, contributions, interests, and "
                "communication style."
            ),
            agent=profiler,
            async_execution=True
        )

        # Helper to reduce repetition when offering downloads
        def _offer_download(filepath: str, button_label: str, session_key: str):
            """Display a Streamlit download button if *filepath* exists.

            The file is read into session_state under *session_key* so a second
            call does not need to hit the disk again.
            """
            if os.path.exists(filepath):
                if session_key not in st.session_state:
                    with open(filepath, "r") as f:
                        st.session_state[session_key] = f.read()
                st.download_button(button_label, st.session_state[session_key], file_name=os.path.basename(filepath))
                return True
            return False

        resume_strategy_task = Task(
            description=(
                "Using the profile and job requirements obtained from "
                "previous tasks, tailor the resume to highlight the most "
                "relevant areas. Employ tools to adjust and enhance the "
                "resume content. Make sure this is the best resume even but "
                "don't make up any information. Update every section, "
                "inlcuding the initial summary, work experience, skills, "
                "and education. All to better reflrect the candidates "
                "abilities and how it matches the job posting."
            ),
            expected_output=(
                "An updated resume that effectively highlights the candidate's "
                "qualifications and experiences relevant to the job."
            ),
            output_file = "tailored_resume.md",
            context = [research_task, profile_task],
            agent=resume_strategist,
        )
        
        interview_preparation_task = Task(
            description=(
                "Create a set of potential interview questions and talking "
                "points based on the tailored resume and job requirements. "
                "Utilize tools to generate relevant questions and discussion "
                "points. Make sure to use these question and talking points to "
                "help the candiadte highlight the main points of the resume "
                "and how it matches the job posting."
            ),
            expected_output=(
                "A document containing key questions and talking points "
                "that the candidate should prepare for the initial interview."
            ),
            output_file="interview_materials.md",
            context=[research_task, profile_task, resume_strategy_task],
            agent=interview_preparer
        )

        job_application_crew = Crew(
            agents = [
                researcher,
                profiler,
                resume_strategist,
                interview_preparer,
            ],
            tasks = [
                research_task,
                profile_task,
                resume_strategy_task,
                interview_preparation_task
            ],
            verbose=True
        )

        # Execute the process
        job_application_inputs = {
            'job_posting_url': job_posting_url,
            'github_url': github_url,
            'personal_writeup': personal_writeup
        }

        result = job_application_crew.kickoff(inputs=job_application_inputs)

        # Display and allow file download
        tailored_resume_path = "tailored_resume.md"
        interview_prep_path = "interview_materials.md"

        # Offer downloads in a DRY manner
        generated_any = False
        generated_any |= _offer_download(tailored_resume_path, "Download Tailored Resume", "tailored_resume_content")
        generated_any |= _offer_download(interview_prep_path, "Download Interview Preparation File", "interview_prep_content")

        if not generated_any:
            st.error("Error: Could not generate the output files.")
