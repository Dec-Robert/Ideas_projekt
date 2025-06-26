<template>
  <div class="hello">
    <button @click="openDialog" class="add-btn">Dodaj obraz do oceny</button>
    <!-- Przycisk odświeżania -->
    <button @click="fetchSamples" class="refresh-btn">Odśwież listę próbek</button>
    <button @click="sendReport" class="report-btn" :disabled="selectedSamples.length === 0">Zrób raport</button>
    <!-- Lista próbek -->
    <table class="samples-table">
      <thead>
        <tr>
          <th><input type="checkbox" @change="toggleAll($event)" :checked="allSelected" /></th>
          <th>Numer</th>
          <th>Data dodania</th>
          <th>Status</th>
          <th>Obraz</th>
          <th>Algorytm</th>
          <th>Obraz oceniony</th>
          <th>Pewność</th>
          <th>Data oceny</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sample in samples" :key="sample.number">
          <td><input type="checkbox" :value="sample.number" v-model="selectedSamples" /></td>
          <td>
            <a href="#" @click.prevent="showImage(sample)">{{ sample.number }}</a>
          </td>
          <td>{{ sample.date }}</td>
          <td>{{ sample.status }}</td>
          <td>
            <span class="icon" @click="showImage(sample)">🔍</span>
          </td>
          <td>{{ sample.algorithm }}</td>
          <td>
            <span v-if="sample.evaluated_image" class="icon" @click="showEvaluatedImage(sample)">🔍</span>
          </td>
          <td>{{ sample.confidence }}</td>
          <td>{{ sample.date_predicted }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Podgląd obrazu -->
    <div v-if="previewSample" class="dialog-overlay" @click.self="previewSample = null">
      <div class="dialog">
        <h3>Podgląd obrazu próbki {{ previewSample.number }}</h3>
        <img :src="previewSample.img" alt="Sample image" style="max-width:300px;max-height:200px;" />
        <div class="dialog-actions">
          <button @click="previewSample = null">Zamknij</button>
        </div>
      </div>
    </div>

    <!-- Podgląd obrazu ocenionego -->
    <div v-if="previewEvaluatedSample" class="dialog-overlay" @click.self="previewEvaluatedSample = null">
      <div class="dialog">
        <h3>Podgląd obrazu ocenionego próbki {{ previewEvaluatedSample.number }}</h3>
        <img :src="previewEvaluatedSample.evaluated_image" alt="Evaluated image" style="max-width:300px;max-height:200px;" />
        <div class="dialog-actions">
          <button @click="previewEvaluatedSample = null">Zamknij</button>
        </div>
      </div>
    </div>

    <div v-if="showDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>Dodaj obraz do oceny</h3>
        <input type="file" @change="onFileChange" accept="image/*" />
        <div>
          <label>Algorytm oceny:</label>
          <select v-model="selectedAlgorithm">
            <option value="Algorytm_1">Algorytm_1</option>
            <option value="Algorytm_2">Algorytm_2</option>
          </select>
        </div>
        <div class="dialog-actions">
          <button @click="addSample" :disabled="!selectedFile">Dodaj</button>
          <button @click="closeDialog">Anuluj</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data() {
    return {
      showDialog: false,
      selectedFile: null,
      selectedFileHash: null,
      selectedAlgorithm: 'Algorytm_1',
      previewSample: null,
      previewEvaluatedSample: null,
      samples: [],
      selectedSamples: [],
    };
  },
  computed: {
    allSelected() {
      return this.samples.length > 0 && this.selectedSamples.length === this.samples.length;
    }
  },
  async mounted() {
    await this.fetchSamples();
  },
  methods: {
    openDialog() {
      this.showDialog = true;
      this.selectedFile = null;
      this.selectedFileHash = null;
    },
    closeDialog() {
      this.showDialog = false;
      this.selectedFile = null;
      this.selectedFileHash = null;
    },
    async fetchSamples() {
      try {
        const res = await fetch('http://localhost:8082/samples');
        if (!res.ok) throw new Error('Błąd pobierania próbek');
        const data = await res.json();
        this.samples = data.map(s => ({
          number: s.sample_number,
          date: s.date_added ? new Date(s.date_added).toLocaleString('pl-PL') : '',
          status: s.status === 'in_progress' ? 'W trakcie oceny' : (s.status === 'positive' ? 'Ocena: Pozytywna' : (s.status === 'negative' ? 'Ocena: Negatywna' : s.status)),
          img: s.cropped_image || '',
          algorithm: s.algorithm ?? '',
          evaluated_image: s.evaluated_image ?? '',
          confidence: s.confidence ?? '',
          date_predicted: s.date_predicted ? new Date(s.date_predicted).toLocaleString('pl-PL') : '',
        }));
      } catch (e) {
        this.samples = [];
      }
    },
    onFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        this.selectedFile = file;
        const reader = new FileReader();
        reader.onload = async (event) => {
          const arrayBuffer = event.target.result;
          const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
          const hashArray = Array.from(new Uint8Array(hashBuffer));
          const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          this.selectedFileHash = hashHex;
        };
        reader.readAsArrayBuffer(file);
      }
    },
    async addSample() {
      if (!this.selectedFile) return;
      const waitForHash = async () => {
        if (!this.selectedFileHash) {
          await new Promise(resolve => setTimeout(resolve, 50));
          return waitForHash();
        }
      };
      await waitForHash();
      const file = this.selectedFile;
      const formData = new FormData();
      formData.append('file', file);
      formData.append('algorithm', this.selectedAlgorithm === 'Algorytm_1' ? 1 : 2);
      formData.append('hash', this.selectedFileHash || '');
      try {
        const response = await fetch('http://localhost:8084/upload', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`Błąd serwera: ${response.status} ${response.statusText}`);
        }

        await this.fetchSamples();

      } catch (err) {
        console.error('Błąd podczas dodawania obrazu:', err);
        alert('Nie udało się dodać obrazu. Sprawdź konsolę, aby uzyskać więcej informacji.');
      }
      
      this.showDialog = false;
      this.selectedFile = null;
      this.selectedFileHash = null;
    },
    showImage(sample) {
      if (sample.img && !sample.img.startsWith('data:image')) {
        this.previewSample = {
          ...sample,
          img: 'data:image/png;base64,' + sample.img
        };
      } else {
        this.previewSample = sample;
      }
    },
    showEvaluatedImage(sample) {
      if (sample.evaluated_image && !sample.evaluated_image.startsWith('data:image')) {
        this.previewEvaluatedSample = {
          ...sample,
          evaluated_image: 'data:image/png;base64,' + sample.evaluated_image
        };
      } else {
        this.previewEvaluatedSample = sample;
      }
    },
    toggleAll(e) {
      if (e.target.checked) {
        this.selectedSamples = this.samples.map(s => s.number);
      } else {
        this.selectedSamples = [];
      }
    },
    async sendReport() {
      try {
        const response = await fetch('http://localhost:8081/generate-report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ sample_ids: this.selectedSamples })
        });

        if (!response.ok) {
          throw new Error('Błąd podczas generowania raportu');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const disposition = response.headers.get('Content-Disposition');
        const filenameMatch = disposition && disposition.match(/filename="(.+)"/);
        link.download = filenameMatch ? filenameMatch[1] : 'raport.docx';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Wystąpił błąd podczas pobierania raportu:', error);
      }
    },
  }
}
</script>

<style scoped>
/* Style bez zmian */
.hello { max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif; }
.add-btn { margin-bottom: 20px; padding: 8px 18px; background: #42b983; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.refresh-btn { margin-bottom: 10px; padding: 6px 16px; background: #1976d2; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.report-btn { margin-bottom: 10px; padding: 6px 16px; background: #e67e22; color: #fff; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px; }
.samples-table { border-collapse: collapse; width: 100%; margin-top: 10px; }
.samples-table th, .samples-table td { border: 1px solid #aaa; padding: 6px 12px; text-align: center; }
.samples-table th { background: #f5f5f5; }
.icon { cursor: pointer; font-size: 18px; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: #fff; padding: 24px 28px; border-radius: 8px; min-width: 320px; box-shadow: 0 2px 16px rgba(0,0,0,0.2); }
.dialog-actions { margin-top: 18px; text-align: right; }
.dialog-actions button { margin-left: 10px; padding: 6px 14px; }
a { color: #42b983; text-decoration: underline; cursor: pointer; }
</style>