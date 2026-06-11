import json

accounts_dict = {
    '410103': {
        'code': '410103',
        'balances': {'2023-01': 100},
        'children': ['41010303'],
        'has_children': True,
        'parent_code': None,
        'has_discrepancy': False,
        'discrepancy': {'2023-01': 0}
    },
    '41010303': {
        'code': '41010303',
        'balances': {'2023-01': 100},
        'children': ['4101030301'],
        'has_children': True,
        'parent_code': '410103',
        'has_discrepancy': True,
        'discrepancy': {'2023-01': 90}
    },
    '4101030301': {
        'code': '4101030301',
        'balances': {'2023-01': 10},
        'children': [],
        'has_children': False,
        'parent_code': '41010303',
        'has_discrepancy': False,
        'discrepancy': {'2023-01': 0}
    }
}

def has_movement(node):
    if any(abs(v) > 0.005 for v in node['balances'].values()):
        return True
    return any(has_movement(accounts_dict[c]) for c in node['children'])

def flatten_tree(nodes, depth=1):
    flat = []
    for n in sorted(nodes, key=lambda x: x['code']):
        if not has_movement(n):
            continue
        n_copy = dict(n)
        child_nodes = [accounts_dict[c] for c in n['children']]
        n_copy['children_codes'] = [c for c in n['children'] if has_movement(accounts_dict[c])]
        
        dummy_node = None
        if n_copy.get('has_discrepancy'):
            dummy_code = n['code'] + '99'
            while dummy_code in accounts_dict:
                dummy_code += '9'
            n_copy['children_codes'].append(dummy_code)
            dummy_node = {
                'code': dummy_code,
                'name': 'Saldos no asignados a subcuentas',
                'parent_code': n['code'],
                'children': [],
                'has_children': False,
                'balances': dict(n.get('discrepancy', {})),
                'monthly_balances': {},
                'has_discrepancy': False,
                'discrepancy': {},
                'children_codes': [],
                'depth': depth + 1,
                'level': len(dummy_code)
            }
            
        n_copy['depth'] = depth
        n_copy['level'] = len(n['code'])
        del n_copy['children']
        flat.append(n_copy)
        
        if child_nodes:
            flat.extend(flatten_tree(child_nodes, depth + 1))
            
        if dummy_node:
            flat.append(dummy_node)
    return flat

roots = [accounts_dict['410103']]
flat_list = flatten_tree(roots)
print("Flat list:")
for item in flat_list:
    print(f"- {item['code']}: {item.get('name')} (children: {item.get('children_codes')})")

