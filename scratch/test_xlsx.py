import io
import xlsxwriter

output = io.BytesIO()
workbook = xlsxwriter.Workbook(output)
sheet = workbook.add_worksheet("Test")
sheet.write(0, 0, "Hello")
workbook.close()

content = output.getvalue()
print(f"Content length: {len(content)}")
if content.startswith(b'PK'):
    print("Starts with PK (standard for .xlsx)")
else:
    print(f"Start bytes: {content[:10]}")
