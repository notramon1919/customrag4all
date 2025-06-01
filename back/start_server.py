from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from supabase import create_client, Client
from transformers import pipeline
import fitz

app = Flask(__name__)
CORS(app)

url = "SUPABASE_URL>"
key = "SUPABASE_KEY"

# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_KEY")

# Supabase
supabase: Client = create_client(url, key)

# Modelo de embeddings y pregunta-respuesta
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
qa_model = pipeline("text-generation", model="tiiuae/falcon-7b-instruct", max_new_tokens=100)


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
    Eres un asistente de IA experto en análisis de documentos.
    Responde de manera clara y amable. Evita caracteres especiales.

    Contexto:
    {contextos}

    Pregunta: {pregunta}

    Respuesta:
    """

    respuesta = qa_model(prompt)[0]['generated_text'].split("Respuesta:")[-1].strip()
    return respuesta


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
