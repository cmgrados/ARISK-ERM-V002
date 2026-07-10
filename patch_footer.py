import re

file_path = r'templates\financial_planning\institutional_budget_builder.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Chunk 1
old_html = """                <tfoot class="font-weight-bold">
                    <tr class="bg-light text-success">
                        <td colspan="14" class="text-right border-right-0">TOTAL INGRESOS</td>
                        <td class="text-right" id="footer-ing-y1">0.00</td>
                        <td class="text-right" id="footer-ing-y2">0.00</td>
                        <td class="text-right" id="footer-ing-y3">0.00</td>
                    </tr>
                    <tr class="bg-light text-danger">
                        <td colspan="14" class="text-right border-right-0">TOTAL EGRESOS</td>
                        <td class="text-right" id="footer-eg-y1">0.00</td>
                        <td class="text-right" id="footer-eg-y2">0.00</td>
                        <td class="text-right" id="footer-eg-y3">0.00</td>
                    </tr>
                    <tr class="bg-dark text-white">
                        <td colspan="14" class="text-right border-right-0">RESULTADO OPERATIVO PRESUPUESTADO</td>
                        <td class="text-right" id="footer-y1">0.00</td>
                        <td class="text-right" id="footer-y2">0.00</td>
                        <td class="text-right" id="footer-y3">0.00</td>
                    </tr>
                </tfoot>"""

new_html = """                <tfoot class="font-weight-bold">
                    <tr class="bg-light text-success">
                        <td colspan="2" class="text-right border-right-0 pr-3">TOTAL INGRESOS</td>
                        <td class="text-right text-monospace" id="footer-ing-m0">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m1">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m2">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m3">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m4">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m5">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m6">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m7">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m8">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m9">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m10">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-m11">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-y1">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-y2">0.00</td>
                        <td class="text-right text-monospace" id="footer-ing-y3">0.00</td>
                    </tr>
                    <tr class="bg-light text-danger">
                        <td colspan="2" class="text-right border-right-0 pr-3">TOTAL EGRESOS</td>
                        <td class="text-right text-monospace" id="footer-eg-m0">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m1">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m2">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m3">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m4">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m5">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m6">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m7">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m8">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m9">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m10">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-m11">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-y1">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-y2">0.00</td>
                        <td class="text-right text-monospace" id="footer-eg-y3">0.00</td>
                    </tr>
                    <tr class="bg-dark text-white">
                        <td colspan="2" class="text-right border-right-0 pr-3">RESULTADO OPERATIVO PRESUPUESTADO</td>
                        <td class="text-right text-monospace" id="footer-res-m0">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m1">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m2">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m3">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m4">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m5">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m6">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m7">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m8">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m9">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m10">0.00</td>
                        <td class="text-right text-monospace" id="footer-res-m11">0.00</td>
                        <td class="text-right text-monospace" id="footer-y1">0.00</td>
                        <td class="text-right text-monospace" id="footer-y2">0.00</td>
                        <td class="text-right text-monospace" id="footer-y3">0.00</td>
                    </tr>
                </tfoot>"""

content = content.replace(old_html, new_html)

# Chunk 2
old_empty = """            document.getElementById('footer-ing-y1').innerText = '0.00';
            document.getElementById('footer-ing-y2').innerText = '0.00';
            document.getElementById('footer-ing-y3').innerText = '0.00';
            document.getElementById('footer-eg-y1').innerText = '0.00';
            document.getElementById('footer-eg-y2').innerText = '0.00';
            document.getElementById('footer-eg-y3').innerText = '0.00';
            document.getElementById('footer-y1').innerText = '0.00';
            document.getElementById('footer-y2').innerText = '0.00';
            document.getElementById('footer-y3').innerText = '0.00';"""

new_empty = """            for(let i=0; i<12; i++) {
                document.getElementById('footer-ing-m'+i).innerText = '0.00';
                document.getElementById('footer-eg-m'+i).innerText = '0.00';
                document.getElementById('footer-res-m'+i).innerText = '0.00';
            }
            document.getElementById('footer-ing-y1').innerText = '0.00';
            document.getElementById('footer-ing-y2').innerText = '0.00';
            document.getElementById('footer-ing-y3').innerText = '0.00';
            document.getElementById('footer-eg-y1').innerText = '0.00';
            document.getElementById('footer-eg-y2').innerText = '0.00';
            document.getElementById('footer-eg-y3').innerText = '0.00';
            document.getElementById('footer-y1').innerText = '0.00';
            document.getElementById('footer-y2').innerText = '0.00';
            document.getElementById('footer-y3').innerText = '0.00';"""

content = content.replace(old_empty, new_empty)

# Chunk 3
old_init = """        let html = '';
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        const isApproved = currentVersionStatus === 'APPROVED';"""

new_init = """        let html = '';
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        let resMonths = new Array(12).fill(0);
        let ingMonths = new Array(12).fill(0);
        let egMonths = new Array(12).fill(0);
        const isApproved = currentVersionStatus === 'APPROVED';"""
content = content.replace(old_init, new_init)

# Chunk 4
old_loop = """                let monthCells = '';
                for (let i = 0; i < 12; i++) {
                    const val = fmt(item.monthly_values[i] || 0);"""
new_loop = """                let monthCells = '';
                for (let i = 0; i < 12; i++) {
                    const mVal = item.monthly_values[i] || 0;
                    resMonths[i] += mVal * catInfo.sign;
                    if (catInfo.sign === 1) ingMonths[i] += mVal;
                    else egMonths[i] += mVal;
                    
                    const val = fmt(mVal);"""
content = content.replace(old_loop, new_loop)

# Chunk 5
old_update = """        tbody.innerHTML = html;
        document.getElementById('footer-ing-y1').innerText = fmt(ingY1);
        document.getElementById('footer-ing-y2').innerText = fmt(ingY2);
        document.getElementById('footer-ing-y3').innerText = fmt(ingY3);"""
new_update = """        tbody.innerHTML = html;
        for(let i=0; i<12; i++) {
            document.getElementById('footer-ing-m'+i).innerText = fmt(ingMonths[i]);
            document.getElementById('footer-eg-m'+i).innerText = fmt(egMonths[i]);
            document.getElementById('footer-res-m'+i).innerText = fmt(resMonths[i]);
        }
        document.getElementById('footer-ing-y1').innerText = fmt(ingY1);
        document.getElementById('footer-ing-y2').innerText = fmt(ingY2);
        document.getElementById('footer-ing-y3').innerText = fmt(ingY3);"""
content = content.replace(old_update, new_update)

# Chunk 6
old_rc1 = """    function recalcFooter() {
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        document.querySelectorAll('#budget-table-body tr[data-item-id]').forEach(tr => {"""
new_rc1 = """    function recalcFooter() {
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        let resMonths = new Array(12).fill(0);
        let ingMonths = new Array(12).fill(0);
        let egMonths = new Array(12).fill(0);
        document.querySelectorAll('#budget-table-body tr[data-item-id]').forEach(tr => {"""
content = content.replace(old_rc1, new_rc1)

# Chunk 7
old_rc2 = """            const sign = parseInt(tr.dataset.sign || '1');
            let y1 = 0;
            tr.querySelectorAll('.month-input').forEach(el => y1 += getMonthVal(el));
            const y2 = getYearVal(tr.querySelector('.y2-input'));"""
new_rc2 = """            const sign = parseInt(tr.dataset.sign || '1');
            let y1 = 0;
            tr.querySelectorAll('.month-input').forEach((el, i) => {
                const mVal = getMonthVal(el);
                y1 += mVal;
                resMonths[i] += mVal * sign;
                if (sign === 1) ingMonths[i] += mVal;
                else egMonths[i] += mVal;
            });
            const y2 = getYearVal(tr.querySelector('.y2-input'));"""
content = content.replace(old_rc2, new_rc2)

# Chunk 8
old_rc3 = """            }
        });
        document.getElementById('footer-ing-y1').innerText = fmt(ingY1);
        document.getElementById('footer-ing-y2').innerText = fmt(ingY2);
        document.getElementById('footer-ing-y3').innerText = fmt(ingY3);"""
new_rc3 = """            }
        });
        for(let i=0; i<12; i++) {
            document.getElementById('footer-ing-m'+i).innerText = fmt(ingMonths[i]);
            document.getElementById('footer-eg-m'+i).innerText = fmt(egMonths[i]);
            document.getElementById('footer-res-m'+i).innerText = fmt(resMonths[i]);
        }
        document.getElementById('footer-ing-y1').innerText = fmt(ingY1);
        document.getElementById('footer-ing-y2').innerText = fmt(ingY2);
        document.getElementById('footer-ing-y3').innerText = fmt(ingY3);"""
content = content.replace(old_rc3, new_rc3)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
