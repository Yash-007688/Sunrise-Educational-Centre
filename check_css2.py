
import os
import re

template_dir = r"c:\Users\YASH\Downloads\New folder (9)\Sunrise-Educational-Centre\templates"

for root, _, files in os.walk(template_dir):
    for file in files:
        if not file.endswith(".html"):
            continue
        path = os.path.join(root, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            clean1 = re.sub(r"<style[\s\S]*?</style>", "", content, flags=re.IGNORECASE)
            clean2 = re.sub(r"<script[\s\S]*?</script>", "", clean1, flags=re.IGNORECASE)
            # Remove jinja blocks
            clean3 = re.sub(r"\{\{[\s\S]*?\}\}", "", clean2)
            clean4 = re.sub(r"\{%[\s\S]*?%\}", "", clean3)
            
            # Now look for lines that look like CSS rules but aren`t in inline styles
            lines = clean4.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                # If a line contains { and not in inline style="...", it might be CSS
                if "{" in line and "style=" not in line and "function" not in line and "class=" not in line:
                    # Ignore some common JS artifacts that might have escaped the script tags somehow
                    if "if " in line or "for " in line or "while " in line:
                        continue
                    # Ignore json dumps
                    if ":" in line and "\"" in line:
                        continue
                        
                    print(f"Possible leaking CSS block in {file}: {line}")
        except Exception:
            pass

