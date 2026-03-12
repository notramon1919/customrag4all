<script setup>
import { ref } from 'vue'

const backendUrl = 'http://localhost:5000';
const fileList = ref([])
const uploading = ref(false)
const uploadResponse = ref('')
const archivoActivo = ref(localStorage.getItem('doc_activo') || 'Ninguno')

const pregunta = ref('')
const respuesta = ref('')
const preguntando = ref(false)

const handleUpload = async () => {
  if (fileList.value.length === 0) return
  const formData = new FormData()
  formData.append('file', fileList.value[0].file)

  uploading.value = true
  try {
    const res = await fetch(`${backendUrl}/upload`, { method: 'POST', body: formData })
    const data = await res.json()
    if (res.ok) {
      archivoActivo.value = data.filename
      localStorage.setItem('doc_activo', data.filename)
      uploadResponse.value = `Cargado: ${data.filename}`
    }
  } catch (err) {
    uploadResponse.value = 'Error de conexión'
  } finally {
    uploading.value = false
    fileList.value = []
  }
}

const hacerPregunta = async () => {
  if (!pregunta.value.trim()) return
  preguntando.value = true
  try {
    const res = await fetch(`${backendUrl}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta: pregunta.value })
    })
    const data = await res.json()
    respuesta.value = data.respuesta
    archivoActivo.value = data.archivo_activo
  } finally {
    preguntando.value = false
  }
}

const handleClear = async () => {
  pregunta.value = ''
  respuesta.value = ''
  await fetch(`${backendUrl}/clear`, { method: 'DELETE' })
  archivoActivo.value = 'Ninguno'
  localStorage.removeItem('doc_activo')
  respuesta.value = ''
}
</script>

<template>
  <main class="p-6 max-w-2xl mx-auto">
    <n-card title="RAG Documento Único" class="mb-4">
      <div class="mb-4 p-2 bg-blue-50 border-l-4 border-blue-500 text-blue-700">
        <strong>Documento activo:</strong> {{ archivoActivo }}
      </div>

      <n-upload :max="1" v-model:file-list="fileList" accept=".pdf" :custom-request="() => {}">
        <n-upload-dragger>
            <div style="margin-bottom: 12px">
              <n-icon size="48">
                <i class="mdi mdi-upload" />
              </n-icon>
            </div>
            <n-text style="font-size: 16px">
              Hazme click para seleccionar un PDF o arrastrame uno.
            </n-text>
          </n-upload-dragger>
      </n-upload>

      <n-button type="primary" block :loading="uploading" @click="handleUpload" class="mt-4">
        Cambiar Documento Activo
      </n-button>
    </n-card>

    <n-card v-if="archivoActivo !== 'Ninguno'">
      <n-input v-model:value="pregunta" type="textarea" placeholder="Pregunta algo..." />
      <n-button type="info" block :loading="preguntando" @click="hacerPregunta" class="mt-2">
        Preguntar a Qwen
      </n-button>
      
      <div v-if="respuesta" class="mt-4 p-4 bg-gray-100 rounded text-sm font-mono">
        {{ respuesta }}
      </div>
    </n-card>

    <n-button ghost type="error" size="small" @click="handleClear" class="mt-4">
      Limpiar Documento
    </n-button>
  </main>
</template>