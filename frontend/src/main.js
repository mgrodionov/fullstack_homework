import { createApp } from "vue";
import axios from "axios";
import store from "./store";
import App from "./App.vue";
import router from "./router";

axios.defaults.baseURL = "http://localhost:8000/api/";

const app = createApp(App);
app.use(store);
app.use(router).mount("#app");
