import codecs
with codecs.open('apps/financial_planning/views.py', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('@require_http_methods(["POST"])', 'from django.views.decorators.http import require_http_methods\n@require_http_methods(["POST"])')

with codecs.open('apps/financial_planning/views.py', 'w', 'utf-8') as f:
    f.write(content)
