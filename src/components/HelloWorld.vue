<template>
  <div class="hello">
    <button @click="showDialog = true" class="add-btn">Dodaj obraz do oceny</button>

    <!-- Dialog dodawania -->
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
          <button @click="showDialog = false">Anuluj</button>
        </div>
      </div>
    </div>

    <!-- Lista próbek -->
    <table class="samples-table">
      <thead>
        <tr>
          <th>Numer</th>
          <th>Data dodania</th>
          <th>Status</th>
          <th>Obraz</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sample in samples" :key="sample.number">
          <td>
            <a href="#" @click.prevent="showImage(sample)">{{ sample.number }}</a>
          </td>
          <td>{{ sample.date }}</td>
          <td>{{ sample.status }}</td>
          <td>
            <span class="icon" @click="showImage(sample)">🔍</span>
          </td>
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
  </div>
</template>

<script>
function getStatusText(status) {
  if (status === 'pending') return 'W trakcie oceny';
  if (status === 'positive') return 'Ocena: Pozytywna';
  if (status === 'negative') return 'Ocena: Negatywna';
  return status;
}

export default {
  name: 'HelloWorld',
  data() {
    return {
      showDialog: false,
      selectedFile: null,
      selectedAlgorithm: 'Algorytm_1',
      previewSample: null,
      samples: [
        {
          number: '84758',
          date: '19.05.2025 13:10',
          status: getStatusText('positive'),
          img: '',
        },
        {
          number: '12384',
          date: '19.05.2025 13:10',
          status: getStatusText('negative'),
          img: '',
        },
        {
          number: '71889',
          date: '19.05.2025 13:10',
          status: getStatusText('pending'),
          img: '', 
        },
      ],
    };
  },
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },
    addSample() {
      // Symulacja wyciągania numeru próbki z obrazu
      const number = Math.floor(Math.random() * 90000 + 10000).toString();
      const date = new Date().toLocaleString('pl-PL', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
      const status = 'W trakcie oceny';

      // Odczyt obrazu jako dataURL
      const reader = new FileReader();
      reader.onload = (e) => {
        this.samples.unshift({
          number,
          date,
          status,
          img: e.target.result,
        });
        this.showDialog = false;
        this.selectedFile = null;
      };
      reader.readAsDataURL(this.selectedFile);
    },
    showImage(sample) {
      this.previewSample = sample;
    }
  }
}
</script>

<style scoped>
.hello {
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}
.desc {
  margin-bottom: 24px;
}
.add-btn {
  margin-bottom: 20px;
  padding: 8px 18px;
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.samples-table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 10px;
}
.samples-table th, .samples-table td {
  border: 1px solid #aaa;
  padding: 6px 12px;
  text-align: center;
}
.samples-table th {
  background: #f5f5f5;
}
.icon {
  cursor: pointer;
  font-size: 18px;
}
.dialog-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog {
  background: #fff;
  padding: 24px 28px;
  border-radius: 8px;
  min-width: 320px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
}
.dialog-actions {
  margin-top: 18px;
  text-align: right;
}
.dialog-actions button {
  margin-left: 10px;
  padding: 6px 14px;
}
a {
  color: #42b983;
  text-decoration: underline;
  cursor: pointer;
}
</style>
