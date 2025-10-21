import subprocess
import os

tex_file ='ex.tex'
tex_dir = os.path.dirname(os.path.abspath(tex_file))

subprocess.run(['pdflatex', "-interaction=nonstopmode",tex_file ], cwd=tex_dir)

for ext in [".aux", ".log", ".out", ".toc"]:
    path = os.path.join(tex_dir, base)



