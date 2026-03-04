
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
            
            # Remove styles and scripts
            clean1 = re.sub(r"<style[\s\S]*?</style>", "", content, flags=re.IGNORECASE)
            clean2 = re.sub(r"<script[\s\S]*?</script>", "", clean1, flags=re.IGNORECASE)
            
            # Now look for typical CSS properties
            lines = clean2.split("\n")
            for i, line in enumerate(lines):
                if re.search(r"(position:\s*absolute|display:\s*flex|transform:\s*translate|margin-[a-z]+:\s*\d|padding:\s*\d)", line) and "{" in line:
                    print(f"Possible leaking CSS block in {file}: {line.strip()}")
                elif re.match(r"^\s*\.[a-zA-Z0-9_-]+\s*\{", line):
                    print(f"Possible leaking CSS class in {file}: {line.strip()}")
                    
        except Exception:
            pass

