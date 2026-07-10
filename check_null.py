import json

with open('test_data.json', 'r') as f:
    data = json.load(f)

for item in data.get('data', []):
    if item.get('account_prefix') is None:
        print(f"Item {item.get('code')} has None account_prefix")
