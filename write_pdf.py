from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import os
import glob
import subprocess
import shutil

# Step2
def render_latex_pdf(latex_content: str) -> str:
    """Render latex document to pdf

    Args:
        latex_content (str): the latex content as string

    Returns:
        str: path to the generated pdf document
    """
    output_dir = Path("output").absolute()
    output_dir.mkdir(exist_ok=True)

    # Step3
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tex_filename = f"paper_{timestamp}.tex"
    pdf_filename = f"paper_{timestamp}.pdf"

    #Step 4
    tex_file = output_dir/tex_filename
    tex_file.write_text(latex_content)

    tex_to_pdf_clean(tex_file=tex_file)

    final_pdf = output_dir/pdf_filename
    if not final_pdf.exists():
        raise FileNotFoundError("PDF file was not generated")
    print(f"Successfully generated pdf at {final_pdf}")
    return str(final_pdf)



def tex_to_pdf_clean(tex_file):
    tex_dir = os.path.dirname(os.path.abspath(tex_file))
    base_name = os.path.splitext(os.path.basename(tex_file))[0]

    # Compile using MiKTeX
    subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_file], cwd=tex_dir)

    # Remove auxiliary files
    for ext in [".aux", ".log", ".out", ".toc"]:
        path = os.path.join(tex_dir, base_name + ext)
        if os.path.exists(path):
            os.remove(path)

    print("✅ PDF generated and cleaned successfully!")



