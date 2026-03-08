import os
directory = r"c:\Users\agarw\OneDrive\Desktop\Rohan\Crop (Capstone Project '26)\frontend\client\src"
for root, _, files in os.walk(directory):
    for f in files:
        if f.endswith('.tsx') or f.endswith('.ts') or f.endswith('.css'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'violet' in content:
                new_content = content.replace('violet', 'teal')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Replaced violet in {f}")
