import json
import re
import os

log_path = r'C:\Users\VICTUS\.gemini\antigravity\brain\38769ff1-8576-4fe1-84f2-186dbc5b4b24\.system_generated\logs\overview.txt'

files_content = {}
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
        except:
            continue
            
        if data.get('type') == 'TOOL_RESPONSE' and data.get('name') == 'view_file':
            output = data.get('output', '')
            if 'Total Lines:' in output and 'The following code has been modified' in output:
                # print(output[:100])
                m = re.search(r'File Path: `file:///c:/Users/VICTUS/Desktop/A.RISK%20ERM%20-%20V2/templates/strategic_risk/([^`]+)`', output, re.IGNORECASE)
                if m:
                    name = m.group(1)
                    # Extract contents
                    parts = output.split('1: ', 1)
                    if len(parts) == 2:
                        content_with_trailer = parts[1]
                        # Remove the trailer
                        if 'The above content does NOT show' in content_with_trailer:
                            content = content_with_trailer.split('The above content does NOT show')[0]
                        elif 'The above content shows the entire' in content_with_trailer:
                            content = content_with_trailer.split('The above content shows the entire')[0]
                        else:
                            content = content_with_trailer
                            
                        # Clean line numbers
                        cleaned = re.sub(r'(?m)^\d+:\s?', '', '1: ' + content)
                        files_content[name] = cleaned.strip('\n')

for name, content in files_content.items():
    print(f"Found {name} with length {len(content)}")
    out_path = os.path.join(r'c:\Users\VICTUS\Desktop\A.RISK ERM - V2\templates\strategic_risk', name)
    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write(content)
            print(f"Restored {name}")

