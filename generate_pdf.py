import os
import dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from playwright.sync_api import sync_playwright

# Load environment variables
dotenv.load_dotenv()

# Setup API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set. "
        "Please add OPENROUTER_API_KEY=your_key_here to your .env file."
    )

HTML_FILE_PATH = os.path.abspath("resume.html")
PDF_FILE_PATH = os.path.abspath("resume.pdf")

print("Setting up CrewAI Agent...")

# Define the OpenRouter LLM via litellm (CrewAI uses this internally)
# You can change 'openai/gpt-4o-mini' to any OpenRouter model like 'anthropic/claude-3-haiku' etc.
openrouter_llm = LLM(
    model="openrouter/openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

from html_to_pdf_tool import convert_local_html_to_pdf

agent = Agent(
    role="Document Converter",
    goal="You are a helpful assistant that safely converts local files into PDF locally.",
    backstory="You are an expert at handling documents and converting them locally without leaking data online.",
    tools=[convert_local_html_to_pdf],
    llm=openrouter_llm,
    verbose=True,
    max_iter=15,
)

task = Task(
    description=(
        f"You need to grab a local HTML file and create a PDF saved to the local directory.\n"
        f"Because you run on the user's host machine, you do not need public URL uploads. Do NOT upload to the public internet.\n\n"
        f"Follow these exact steps strictly using the given tools:\n"
        f"1. Use the 'Convert Local HTML to PDF' tool. Pass `{HTML_FILE_PATH}` as the `html_file_path` argument and `{PDF_FILE_PATH}` as the `pdf_file_path` argument.\n"
        f"2. Read the response from the tool.\n"
        f"3. Return a successful confirmation message once finished, letting the user know it was saved locally.\n"
    ),
    expected_output="A confirmation message saying the file was grabbed from the local repo, converted locally, and saved to the local directory successfully.",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
print(f"Kicking off task to convert '{HTML_FILE_PATH}' to '{PDF_FILE_PATH}'...")

try:
    result = crew.kickoff()
    print("\n================== RESULT ==================")
    print(str(result))
except Exception as e:
    print("\n================== ERROR ==================")
    print(f"An error occurred: {e}")

