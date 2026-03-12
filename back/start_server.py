import os
import fitz  # PyMuPDF
import chromadb
import ollama
from flask import Flask, request, jsonify
from flask_cors import CORS
from chromadb.utils import embedding_functions

app = Flask(__name__)
CORS(app)

MODELO_LLM = "qwen2.5:7b"
chroma_client = chromadb.PersistentClient(path="./db_data")
model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_or_create_collection(name="documentos_rag", embedding_function=model_ef)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['file']
    file_path = os.path.join("./", file.filename)
    file.save(file_path)

    try:
        existing_docs = collection.get()
        if existing_docs['ids']:
            collection.delete(ids=existing_docs['ids'])

        doc = fitz.open(file_path)
        documents, metadatas, ids = [], [], []

        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                documents.append(text)
                metadatas.append({"source": file.filename, "page": i + 1})
                ids.append(f"p{i+1}")

        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        doc.close()
        os.remove(file_path)

        return jsonify({"message": "Nuevo documento indexado", "filename": file.filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_local_llm():
    data = request.json
    pregunta = data.get("pregunta")
    
    current_data = collection.get(limit=1)
    filename = current_data['metadatas'][0]['source'] if current_data['metadatas'] else "Documento desconocido"

    results = collection.query(query_texts=[pregunta], n_results=6)
    contexto = "\n".join(results['documents'][0])

    prompt_final = f"""Analiza el documento: {filename}.
                    Responde de forma fría y directa. 
                    Si la información no está en el contexto, di "No está en el documento".
                    Prohibido inventar o divagar.

                    CONTEXTO:
                    {contexto}

                    PREGUNTA:
                    {pregunta}"""

    response = ollama.generate(
        model=MODELO_LLM,
        prompt=prompt_final,
        options={"temperature": 0.2, "num_ctx": 4000}
    )
    
    return jsonify({
        "respuesta": response['response'],
        "archivo_activo": filename
    })

@app.route('/clear', methods=['DELETE'])
def clear_db():
    collection.delete(ids=collection.get()['ids'])
    return jsonify({"message": "DB vacía"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)