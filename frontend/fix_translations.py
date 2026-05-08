import re

file_path = "client/src/lib/translations.ts"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# The bug is that lp_ben_3_desc: "Something
# is missing the closing ", at the end before the newline.

content = re.sub(r'(lp_ben_3_desc: ".*?[^\"])\n', r'\1",\n', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Syntax error fixed.")
