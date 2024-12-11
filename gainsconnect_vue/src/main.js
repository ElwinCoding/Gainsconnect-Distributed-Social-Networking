import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Toast, { POSITION } from 'vue-toastification';
import { createPinia } from 'pinia';
import 'vue-toastification/dist/index.css';

const app = createApp(App);
const pinia = createPinia();

const options = {
    position: POSITION.TOP_CENTER,
    transition: "Vue-Toastification__bounce",
    timeout: 3000,
    closeButton: true,
    draggable: true,
    closeOnClick: true,
    pauseOnHover: true,
    hideProgressBar: false,
    toastClassName: "text-white bg-purple-600",
};

app.use(Toast, options);
app.use(pinia);
app.use(router);
app.mount('#app');
