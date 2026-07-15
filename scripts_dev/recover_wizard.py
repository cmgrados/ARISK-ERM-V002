import os, json
brain_dir = r'C:\Users\VICTUS\.gemini\antigravity\brain'
for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f == 'overview.txt':
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    for line in file:
                        if '<!-- STEP 1:' in line and 'wizard.html' in line:
                            data = json.loads(line)
                            if 'tool_responses' in data:
                                for tr in data['tool_responses']:
                                    if 'output' in tr and '<!-- STEP 1:' in tr['output']:
                                        print(f'Length: {len(tr["output"])}')
                                        open('recovered_wizard.txt', 'a', encoding='utf-8').write(tr["output"] + "\n\n=====\n\n")
            except Exception as e:
                print(f"Error parsing {f}: {e}")
print("Done searching")
