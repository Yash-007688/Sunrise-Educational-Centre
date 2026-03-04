
import os
import re

template_dir = r"c:\Users\YASH\Downloads\New folder (9)\Sunrise-Educational-Centre\templates"

def find_leaked_css():
    for root, _, files in os.walk(template_dir):
        for file in files:
            if not file.endswith(".html"):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
                
            in_style = False
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "<style" in line:
                    if "</style>" in line:
                        in_style = False
                    else:
                        in_style = True
                elif "</style>" in line:
                    in_style = False
                elif not in_style:
                    # Look for CSS rules outside style blocks
                    if re.match(r"^\s*(\.[a-zA-Z0-9_-]+|#[a-zA-Z0-9_-]+|body:not)\s*\{", line):
                        print(f"Possible leaking CSS class in {file} at line {i+1}: {line.strip()}")
                        # print context
                        # for j in range(max(0, i-2), min(len(lines), i+3)):
                        #     print(f"  {j+1}: {lines[j]}")

find_leaked_css()

