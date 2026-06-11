with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<!-- Montecarlo Comparative Section -->')
end = text.find('<div class="text-center mt-4">', start)
print(text[start:end])
