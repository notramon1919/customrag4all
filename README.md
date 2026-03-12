# 📚 CustomRAG4All - Sistema RAG Local con Interfaz Web

Un sistema **RAG (Retrieval-Augmented Generation)** completamente local que permite interactuar con documentos PDF mediante preguntas en lenguaje natural, sin depender de servicios en la nube.

> Proyecto de culminación del Grado de Especialización de IA y Big Data 2024/2025

---

## 🎯 ¿Qué hace?

CustomRAG4All es una aplicación que te permite:

- ❓ **Hacer preguntas sobre PDFs** con comprensión contextual
- 📤 **Subir PDFs al instante** para consultar información específica
- 🔄 **Procesamiento RAG local** - Todo funciona en tu máquina
- 🤖 **Respuestas inteligentes** - Impulsadas por Ollama con modelos LLM locales

---

## 🏗️ Arquitectura

### Frontend
- **Framework:** Vue.js 3
- **Build Tool:** Vite
- **Componentes UI:** Naive-UI

### Backend
- **Servidor:** Flask + Flask-CORS
- **LLM Local:** Ollama (modelo: qwen2.5:7b (Predeterminado))
- **Base de Datos Vectorial:** ChromaDB
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Procesamiento PDF:** PyMuPDF (fitz)

---

## 🔧 Dependencias

### Backend (requirements.txt)
```
ollama
flask
flask-cors
chromadb
sentence-transformers
PyMuPDF
python-dotenv
```

### Frontend (package.json)
```
Vue 3.5.13
Vite 6.2.4
Naive-UI 2.41.0
Vue Router 4.5.0
Axios 1.9.0
```

---

## 🔄 Flujo de la Aplicación

1. El usuario sube un PDF o realiza una pregunta en la interfaz
2. El backend procesa el PDF con PyMuPDF y lo indexa en ChromaDB
3. Al hacer una pregunta, se buscan fragmentos relevantes (RAG)
4. Ollama genera la respuesta usando el modelo Qwen2.5:7b
5. La respuesta se retorna al usuario

---

## 📦 Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | Vue 3 + Vite + Naive-UI |
| **Backend** | Python + Flask |
| **Base de Datos Vectorial** | ChromaDB |
| **Modelo LLM** | Ollama (Qwen2.5:7b(Predeterminado)) |
| **Embeddings** | Sentence Transformers |
| **Procesamiento PDF** | PyMuPDF |

---

## 🚀 Inicio Rápido

1. **Backend:**
   ```bash
   cd back
   pip install -r requirements.txt
   python start_server.py
   ```

2. **Frontend:**
   ```bash
   cd front
   npm install
   npm run dev
   ```

3. Abre la aplicación web y comienza a subir PDFs y hacer preguntas

---

## 📝 Notas A Tener En Cuenta

1. El modelo se puede cambiar en cualquier modelo para usar el preferido. (Uso Qwen/Qwen2.5-7B-Instruct, RTX 3060)
