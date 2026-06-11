import sys
lines = open('processed_budget.html', encoding='utf-8').read()

normalization_block = """
// Normalize list of lists into list of dicts for historical_data fallback
if (data && data.income_statement && data.income_statement.length > 0) {
    if (Array.isArray(data.income_statement[0])) {
        // It's a list of lists (historical_data format)
        let periods = data.selected_periods || [];
        data.income_statement = data.income_statement.map(item => {
            if (Array.isArray(item) && item.length > 0) {
                let codeName = String(item[0]);
                let parts = codeName.split(' - ');
                let code = parts[0].trim();
                let name = parts.slice(1).join(' - ').trim();
                let balances = {};
                for (let i = 0; i < periods.length; i++) {
                    balances[periods[i]] = parseFloat(item[i+1]) || 0;
                }
                return {
                    code: code, 
                    name: name, 
                    balances: balances, 
                    parent_code: code.length > 1 ? code.substring(0, code.length - 1) : null
                };
            }
            return item;
        });
    }
}
"""

lines = lines.replace("// Filter out accounts other than 4 and 5 (like 'cuenta de orden')", normalization_block + "\\n                            // Filter out accounts other than 4 and 5 (like 'cuenta de orden')")

open('processed_budget2.html', 'w', encoding='utf-8').write(lines)
print('Done')
