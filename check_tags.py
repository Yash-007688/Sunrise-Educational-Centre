
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
            
            open_count = len(re.findall(r"<style", content, re.IGNORECASE))
            close_count = len(re.findall(r"</style>", content, re.IGNORECASE))
            if open_count != close_count:
                print(f"Mismatched style tags in {file}: {open_count} open, {close_count} close")
        except Exception as e:
            print(f"Error reading {file}: {e}")

