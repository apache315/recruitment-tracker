import sys

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace use_container_width=True with width="stretch"
content = content.replace('use_container_width=True', 'width="stretch"')

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed use_container_width deprecation warnings!")
