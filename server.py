from flask import Flask, request, Response
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime

# --- Configuración inicial ---
UPLOAD_FOLDER = "csv_temp"
CARPETA_DRIVE_ID = "1nH2lySfamPtIq0m268birQTZD_kaklhc"  # <-- Pega aquí el ID de tu carpeta de Drive
SERVICE_ACCOUNT_FILE = "emguploader-15d4576f75cc.json"   # <-- Nombre de tu archivo JSON de la Service Account

# Asegurar que la carpeta temp exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializar Flask
app = Flask(__name__)

# Inicializar cliente de Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

# Ruta principal solo para verificar que el server está activo
@app.route('/')
def index():
    return "✅ Servidor Flask activo y listo para recibir CSV."

# Ruta para recibir el POST con el CSV
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        # Obtener el contenido CSV
        csv_content = request.data.decode('utf-8')
        nombre_archivo = request.headers.get('nombre-archivo', 'archivo_emg.csv')

        # Logging bonito
        print("\n🔵 Nueva solicitud recibida:")
        print(f"📂 Nombre de archivo recibido: {nombre_archivo}")
        print(f"📏 Tamaño del CSV recibido: {len(csv_content.encode('utf-8'))} bytes")

        # Guardar CSV temporalmente
        temp_path = os.path.join(UPLOAD_FOLDER, nombre_archivo)
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("💾 CSV guardado localmente.")

        # Subir a Drive
        file_metadata = {
            'name': nombre_archivo,
            'parents': [CARPETA_DRIVE_ID]
        }
        media = MediaIoBaseUpload(
            io.FileIO(temp_path, 'rb'),
            mimetype='text/csv'
        )
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"✅ Archivo subido a Drive con ID: {file.get('id')}")

        return Response("Archivo recibido y subido a Drive.", status=200)

    except Exception as e:
        print(f"❌ Error al procesar CSV: {e}")
        return Response(f"Error al procesar CSV: {e}", status=500)

# --- Correr el servidor ---
if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print(f"📅 Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔈 Escuchando en http://0.0.0.0:${PORT}")
    print("========================================\n")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

