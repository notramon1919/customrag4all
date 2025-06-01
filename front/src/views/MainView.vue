<script setup>
import {ref} from 'vue'

// Subida de archivo
const fileList = ref([])
const uploading = ref(false)
const uploadResponse = ref('')

// Pregunta y respuesta
const pregunta = ref('')
const respuesta = ref('')
const preguntando = ref(false)

// Subir PDF
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    uploadResponse.value = 'Selecciona un archivo PDF primero.'
    return
  }

  const file = fileList.value[0].file
  const formData = new FormData()
  formData.append('file', file)

  uploading.value = true
  uploadResponse.value = ''

  try {
    const res = await fetch('http://localhost:5000/upload_pdf', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()
    if (res.ok) {
      uploadResponse.value = data.mensaje
    } else {
      uploadResponse.value = data.error || 'Error al subir el archivo.'
    }
  } catch (err) {
    uploadResponse.value = 'Error de red o del servidor.'
  } finally {
    uploading.value = false
    fileList.value = []
  }
}

// Preguntar
const hacerPregunta = async () => {
  if (!pregunta.value.trim()) {
    respuesta.value = 'Escribe una pregunta primero.'
    return
  }

  preguntando.value = true
  respuesta.value = ''

  try {
    const res = await fetch('http://localhost:5000/question', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({question: pregunta.value})
    })

    const data = await res.json()
    if (res.ok) {
      respuesta.value = data.respuesta
    } else {
      respuesta.value = data.error || 'Error al procesar la pregunta.'
    }
  } catch (err) {
    respuesta.value = 'Error de red o del servidor.'
  } finally {
    preguntando.value = false
  }
}
</script>

<template>
  <main class="p-6">
    <n-card title="Subir PDF a Supabase" class="max-w-xl mx-auto mb-6">
      <n-space vertical size="large">

        <!-- Uploader -->
        <n-upload
            multiple
            :max="1"
            v-model:file-list="fileList"
            accept=".pdf"
            :custom-request="() => {}"
        >
          <n-upload-dragger>
            <div style="margin-bottom: 12px">
              <n-icon size="48">
              <i class="mdi mdi-upload" />
            </n-icon>
            </div>
            <n-text style="font-size: 16px">
              Hazme click para seleccionar un PDF o arrastrame uno!
            </n-text>
            <n-p depth="3" style="margin: 8px 0 0 0">
              De momento no se controla que puedas subir duplicados así que ten cuidado! :D kys
            </n-p>
          </n-upload-dragger>
        </n-upload>

        <!-- Botón subir PDF -->
        <n-button
            type="primary"
            :loading="uploading"
            @click="handleUpload"
        >
          Subir PDF
        </n-button>

        <n-text v-if="uploadResponse" type="info">
          {{ uploadResponse }}
        </n-text>
      </n-space>
    </n-card>

    <n-card title="Preguntar sobre los documentos subidos" class="max-w-xl mx-auto">
      <n-space vertical size="large">
        <n-input
            v-model:value="pregunta"
            placeholder="Escribe tu pregunta aquí"
            type="textarea"
            autosize
        />

        <n-button
            type="primary"
            :loading="preguntando"
            @click="hacerPregunta"
        >
          Enviar pregunta
        </n-button>

        <n-text v-if="respuesta" type="success">
          {{ respuesta }}
        </n-text>
      </n-space>
    </n-card>
  </main>
</template>
