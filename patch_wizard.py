import re
with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the Montecarlo button from step 6
pattern1 = re.compile(r'<div class="d-inline-flex align-items-center mr-2 mb-2 mb-md-0">\s*<input type="number" id="mc-iterations"[^>]*>\s*<button type="button" class="btn btn-sm btn-outline-warning[^>]*id="btn-run-mc"[^>]*>\s*<i class="fas fa-random mr-1"></i> Montecarlo\s*</button>\s*</div>')
text, count1 = pattern1.subn('', text)
print(f"Removed btn-run-mc {count1} times")

# Remove display:none from montecarlo-body-container
pattern2 = re.compile(r'id="montecarlo-body-container"\s*style="display:\s*none;"')
text, count2 = pattern2.subn('id="montecarlo-body-container"', text)
print(f"Removed display:none {count2} times")

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)
