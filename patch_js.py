import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix response.ok handling
old_then1 = """                        .then(response => {
                            if (!response.ok) throw new Error('Error en el servidor');
                            return response.json();
                        })"""
new_then1 = """                        .then(response => {
                            if (!response.ok) {
                                return response.json().then(errData => {
                                    throw new Error(errData.msg || 'Error del servidor');
                                }).catch(() => { throw new Error('Error del servidor: ' + response.status); });
                            }
                            return response.json();
                        })"""
text = text.replace(old_then1, new_then1)

# Fix result.data to result.trends
old_then2 = """                        .then(result => {
                            if(result.status === 'success' && result.data) {
                                window.montecarloData = result.data;"""
new_then2 = """                        .then(result => {
                            if(result.status === 'success' && result.trends) {
                                window.montecarloData = result.trends;"""
text = text.replace(old_then2, new_then2)

# Fix error reporting
old_catch = """                        .catch(err => {
                            status.html('<i class="fas fa-exclamation-triangle text-danger"></i> Error de conexi&oacute;n');
                        })"""
new_catch = """                        .catch(err => {
                            status.html('<i class="fas fa-exclamation-triangle text-danger"></i> ' + err.message);
                        })"""
text = text.replace(old_catch, new_catch)

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('JS patches applied!')
