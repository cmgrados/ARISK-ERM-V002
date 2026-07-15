import os

filepath = os.path.join('apps', 'utilities', 'views.py')

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines before fix: {len(lines)}")

# Keep lines 0..1490 (up to and including '        return True')
# Then add the correct except block ending for process_portfolio_load
# Then keep lines from 1697 onwards (the correct delete functions)

except_block = [
    "    except Exception as e:\n",
    "        import traceback\n",
    "        with open('debug_load.log', 'a', encoding='utf-8') as f:\n",
    '            f.write(f"Error procesando balance: {str(e)}\\n")\n',
    '            f.write(traceback.format_exc() + "\\n")\n',
    "        \n",
    "        upload = LiqBalanceUpload.objects.get(id=upload_id)\n",
    "        upload.status = LiqLoadStatus.ERROR\n",
    "        upload.save()\n",
    "        return False\n",
    "\n",
]

new_lines = lines[:1491]  # up to and including '        return True'
new_lines.extend(except_block)
new_lines.extend(lines[1697:])  # the correct delete functions at the end

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Total lines after fix: {len(new_lines)}")
print("Fix applied successfully!")
