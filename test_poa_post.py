import requests

url = "http://127.0.0.1:8000/estrategico/api/portafolio-poa/"
data = {
    "anio": "2026",
    "presupuesto": "5000",
    "nombre_proyecto": "PRUEBA2",
    "descripcion": "desc",
    "estrategia": 1, 
    "lider_proyecto": "",
    "plan": "1"
}
try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Response text:", response.text[:500])
except Exception as e:
    print(e)
