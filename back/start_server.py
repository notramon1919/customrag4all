import os
import ngrok
import fitz
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from supabase import create_client, Client
from google import genai

app = Flask(__name__, template_folder='templates')
CORS(app, origins="*")

load_dotenv(dotenv_path=".env", override=True)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
google_gemini = os.getenv("GEMINI_KEY")
ngrok_key = os.getenv("NGROK_KEY")

# Establish connectivity (NGROK)
listener = ngrok.forward(5000, authtoken=ngrok_key)
print(f"Ingress established at {listener.url()}")

# Supabase
supabase: Client = create_client(supabase_url, supabase_key)

# Modelo de embeddings y pregunta-respuesta
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Gemini
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400

    # file: type FileStorage (flask)
    file = request.files['file']
    filename = file.filename

    if filename == '':
        return jsonify({'error': 'Nombre de archivo vacío.'}), 400

    if not filename.endswith('.pdf'):
        return jsonify({'error': 'Solo se permiten archivos PDF.'}), 400

    # Podemos guardarnos el pdf
    # os.makedirs("./pdfs", exist_ok=True)
    # file.save("./pdfs")

    pdf_bytes = file.read()

    # Leer PDF con PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    texto_completo = ""
    for page in doc:
        texto_completo += page.get_text()

    doc.close()

    # Guardar texto en Supabase
    supabase.table('documentos').insert({"contenido": texto_completo}).execute()

    return jsonify({'mensaje': f'Archivo {filename} cargado y guardado correctamente.'})


# === Pregunta del Usuario ===
@app.route('/question', methods=['POST'])
def question():
    data = request.json
    pregunta = data.get('question')

    if not pregunta:
        return jsonify({'error': 'No se proporcionó ninguna pregunta.'}), 400

    respuesta = responder_pregunta(pregunta)
    return jsonify({'respuesta': respuesta})


# Obtener contexto relevante desde Supabase
def buscar_en_supabase(pregunta):
    # Paso 1: Embedding de la pregunta
    pregunta_emb = embedding_model.encode(pregunta, convert_to_tensor=True)

    # Paso 2: Obtener documentos desde Supabase
    data = supabase.table('documentos').select("contenido").execute()
    documentos = [doc['contenido'] for doc in data.data]

    if not documentos:
        return []

    # Paso 3: Calcular similitud
    docs_emb = embedding_model.encode(documentos, convert_to_tensor=True)
    similitudes = util.cos_sim(pregunta_emb, docs_emb)[0]

    top_indices = similitudes.argsort(descending=True)[:1]
    contextos_relevantes = [documentos[i] for i in top_indices]

    return "\n".join(contextos_relevantes)


# Generar respuesta
def responder_pregunta(pregunta):
    contextos = buscar_en_supabase(pregunta)

    if not contextos:
        return "No encontré información relevante en el documento."

    prompt = f"""
    Eres un asistente de inteligencia artificial especializado en la comprensión y análisis de documentos
    proporcionados por el usuario. Tu objetivo principal es responder de manera precisa y clara a las preguntas
    formuladas, basándote exclusivamente en el contenido de los documentos suministrados.
    Utiliza únicamente la información contenida en los documentos proporcionados para generar tus respuestas.
    No recurras a conocimientos externos o información adicional que no esté presente en los documentos.
    Ofrece respuestas directas y fáciles de entender. Si la información relevante es extensa, proporciona un resumen.
    Cuando sea posible, indica la sección o parte del documento donde se encuentra la información.
    Si no hay información suficiente en los documentos para responder, indícalo claramente.
    Mantén un tono respetuoso, profesional y utiliza un lenguaje formal y en español.
    Evita suposiciones o inferencias no respaldadas por el documento. No generes listas por puntos ni nada de eso.
    Prioriza siempre la información más reciente en caso de múltiples documentos.

    Contexto:
    {contextos}

    Pregunta: {pregunta}

    Respuesta:
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )

    return response.text.strip()

@app.route('/')
def landoing():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)