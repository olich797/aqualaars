# utils.py
def filtrar_productos_por_nombre(productos, nombre):
    return [p for p in productos if nombre.lower() in p["nombre"].lower()]

def calcular_precio_bob(precio_usd, tipo_cambio):
    return round(precio_usd * tipo_cambio, 2)

def inicializar_firebase(secrets):
    import firebase_admin
    from firebase_admin import credentials, firestore

    secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")
    if not firebase_admin._apps:
        cred = credentials.Certificate(secrets)
        firebase_admin.initialize_app(cred)
    return firestore.client()