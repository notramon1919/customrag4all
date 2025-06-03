RAG personalizado con interfaz web.

Proyecto realizado al final del Grado de Especialización de IA y Big Data 2024/2025.
Para el frontend se usa Vue con la librería Naive-UI. Y para el backend se usa un servidor Flask con dos Endpoints.

Variables necesarias SUPABASE_KEY, SUPABASE_URL, GEMINI_KEY, NGROK_KEY.
  - SUPABASE_KEY: Key de usuario o de superusuario (tener en cuenta que el de usuario debe tener acceso a la tabla)
  - SUPABASE_URL: Enlace público a la base de datos.
  - GEMINI_KEY: Key de la cuenta de google que tiene acceso a los modelos.
  - NGROK_KEY: Auth key de NGROk para que sea posible el reverse-proxy. (Completamente susceptible si quieres que sea solo local)

El flow de la aplicación es muy básica, puedes realizar preguntas sobre los PDFs alamcenados en Supabase. También puedes subir un PDF en el momento
para preguntar sobre este. Los PDFs no se borran al reiniciar la aplicación, se quedan en Supabase.
