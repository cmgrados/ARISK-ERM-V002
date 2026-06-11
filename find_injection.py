import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for "Detalle de Proyecciones" and the end of its card
match = re.search(r'Detalle de Proyecciones', text)
if match:
    # the card is a div, we find the next '<div class="card shadow-sm mb-4">'
    # or we can just append before the start of the Javascript section
    
    match_js = re.search(r'<script>', text)
    if match_js:
        # We can append it just before <script> or before the end of step-7-content
        # Let's search for '<div id="step-8-content"'
        match8 = re.search(r'<div\s+id="step-8-content"', text)
        if not match8:
            # Let's just find the closing tags before <script>
            start = match_js.start()
            print('Found <script> at', start)
            print(text[start-500:start])
