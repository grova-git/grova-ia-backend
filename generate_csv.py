import csv
import random

# Definir las cabeceras requeridas
headers = ['nombre', 'descripcion', 'precio', 'stock']

# Listas de prefijos y tipos de productos para generar combinaciones únicas
marcas = ['Bayer', 'Pfizer', 'Roemmers', 'Bagó', 'Elea', 'Casasco', 'Raffo', 'Andrómaco', 'Gador', 'Baliarda']
tipos_medicamentos = ['Paracetamol', 'Ibuprofeno', 'Amoxicilina', 'Loratadina', 'Diclofenac', 'Omeprazol', 'Clonazepam', 'Aspirina', 'Cetirizina', 'Enalapril', 'Losartan', 'Levotiroxina', 'Metformina', 'Atorvastatina', 'Alprazolam']
formatos = ['500mg', '1g', '400mg', '20mg', '50mg', '10mg', 'Comprimidos x30', 'Jarabe 120ml', 'Gotas', 'Crema 50g']

otros_productos = [
    'Alcohol en Gel', 'Vendas de Algodón', 'Termómetro Digital', 'Gasa Estéril', 
    'Agua Oxigenada', 'Cinta Adhesiva Hipoalergénica', 'Solución Fisiológica', 
    'Preservativos Prime', 'Test de Embarazo', 'Ibuprofeno Pediátrico',
    'Jabón de Glicerina', 'Pasta Dental Sensodyne', 'Cepillo Dental Oral-B',
    'Shampoo Anticaspa', 'Crema Hidratante Dermaglós', 'Protector Solar Factor 50',
    'Pañales Pampers', 'Toallas Femeninas Siempre Libre', 'Desodorante Dove',
    'Suplemento Vitamínico Centrum'
]

# Generar 150 productos
productos = []

# Primero agregamos los "otros productos" básicos (20)
for prod in otros_productos:
    precio = round(random.uniform(500.0, 15000.0), 2)
    stock = random.randint(5, 100)
    descripcion = f"{prod} de alta calidad, ideal para el botiquín del hogar."
    productos.append({'nombre': prod, 'descripcion': descripcion, 'precio': precio, 'stock': stock})

# Luego generamos combinaciones hasta llegar a 150 (130 faltantes)
while len(productos) < 150:
    marca = random.choice(marcas)
    tipo = random.choice(tipos_medicamentos)
    formato = random.choice(formatos)
    
    nombre = f"{tipo} {marca} {formato}"
    # Evitar duplicados
    if not any(p['nombre'] == nombre for p in productos):
        precio = round(random.uniform(1000.0, 25000.0), 2)
        stock = random.randint(10, 50)
        descripcion = f"Medicamento {tipo} elaborado por laboratorio {marca}. Presentación: {formato}."
        productos.append({'nombre': nombre, 'descripcion': descripcion, 'precio': precio, 'stock': stock})

# Guardar en CSV
csv_filename = "C:\\Users\\ezequ\\Desktop\\productos_farmacia.csv"
try:
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(productos)
    print(f"Archivo generado exitosamente en: {csv_filename}")
except Exception as e:
    # Si falla al guardar en Desktop, intentamos en el proyecto
    fallback = "productos_farmacia.csv"
    with open(fallback, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(productos)
    print(f"Archivo generado en directorio actual: {fallback}")
