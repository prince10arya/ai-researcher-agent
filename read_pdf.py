from langchain_core.tools import tool
import io
import requests
import PyPDF2

@tool
def read_pdf(url: str) -> str:

    """Read and extracted the pdf from the given url
    Args:
        url: the pdf url to read
    Returns:
        str: returns the extracted text from the pdf
    """
    # Step1: Acces Pdf via URL
    response = requests.get(url=url)
    # Step1: Convert to Bytes
    pdf_file = io.BytesIO(response.content)
    # Step2: Retrive Text from PDF
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    page_len=len(pdf_reader.pages)

    # Extract text from all the pages

    text = ""

    for i, page in enumerate(pdf_reader.pages, 1):
        print(f"Extracting text from page {i}/{page_len}")
        text += page.extract_text() + "\n"
    print("Successfully extrancted")
    return text.strip()

