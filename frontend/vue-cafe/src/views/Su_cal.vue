<template>
  <section class="content">
    <header class="major">

     <h1> <RouterLink to="/Superuser">Espace Superuser</RouterLink> </h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel" style="text-align: center">
      <PromoSelect v-model="selectedPromo" />
    </div>
    <br>

    <div class="panel" v-if="selectedPromo" style="text-align: center;">
      <div style="display: flex; flex-direction: row; justify-content: center;">
        <button
          class="csv button"
          type="button"
          :disabled="isDownloading"
          @click="downloadCsv"
        >
          {{ isDownloading ? 'Téléchargement…' : `Télécharger .csv ${selectedPromo}` }}
        </button>
        &nbsp; &nbsp; &nbsp;
        <button class="button csv">Upload le .csv {{ selectedPromo }}</button>
      </div>
      <p v-if="downloadError" class="download-error">{{ downloadError }}</p>
      <br>
      <h2 style="text-align: left;">Calendrier {{ selectedPromo }}</h2>
      <Calendar_compo_SU :selectedPromo="selectedPromo" />
   
    </div>

  </section>


</template>

<script setup lang="ts">
import { ref } from 'vue'
import PromoSelect from '@/components/PromoSelect.vue'
import Calendar_compo_SU from '@/components/Calendar_compo_SU.vue'
import { getCSV } from '@/api'


const selectedPromo = ref('')
const isDownloading = ref(false)
const downloadError = ref<string | null>(null)

function createDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

async function downloadCsv() {
  if (!selectedPromo.value) return
  isDownloading.value = true
  downloadError.value = null

  try {
    const data = await getCSV(selectedPromo.value)
    const blob =
      data instanceof Blob
        ? data
        : new Blob(
            [
              typeof data === 'string'
                ? data
                : data?.csv ?? data?.content ?? JSON.stringify(data),
            ],
            { type: 'text/csv;charset=utf-8;' },
          )

    createDownload(blob, `cal-${selectedPromo.value}.csv`)
  } catch (err) {
    console.error('Unable to download CSV', err)
    downloadError.value = 'Impossible de télécharger le CSV.'
  } finally {
    isDownloading.value = false
  }
}
</script>

<style scoped>
.panel {
  margin-top: 2rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: #01768b1c;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
}

.csv {
  background: #01778b;
  color: white;

}

.download-error {
  margin-top: 0.75rem;
  color: #c0392b;
}
</style>
