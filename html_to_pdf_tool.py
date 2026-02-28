import os
from crewai.tools import tool
from playwright.sync_api import sync_playwright

@tool("Convert Local HTML to PDF")
def convert_local_html_to_pdf(html_file_path: str, pdf_file_path: str) -> str:
    """
    Converts a local HTML file into a PDF and saves it locally using an automated headless browser.
    
    Args:
        html_file_path (str): The path to the existing HTML file to convert (e.g., 'resume.html').
        pdf_file_path (str): The path where the resulting PDF should be saved (e.g., 'resume.pdf').
        
    Returns:
        str: A success message with the file path or an error message.
    """
    try:
        html_abs_path = os.path.abspath(html_file_path)
        pdf_abs_path = os.path.abspath(pdf_file_path)
        
        if not os.path.exists(html_abs_path):
            return f"Error: HTML file not found at {html_abs_path}"

        with sync_playwright() as p:
            # Launch headless chromium
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Go to the local HTML file
            page.goto(f"file://{html_abs_path}", wait_until="networkidle")
            
            # Generate the PDF
            page.pdf(path=pdf_abs_path, format="A4", print_background=True)
            browser.close()
            
        return f"Successfully converted HTML to PDF and saved locally to {pdf_abs_path}."
    except Exception as e:
        return f"Error converting HTML to PDF: {str(e)}"
