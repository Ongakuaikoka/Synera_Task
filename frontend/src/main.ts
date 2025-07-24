import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { ChatClient, ChatClientKey } from './infrastructure/chat-client'
import axios from 'axios'

const app = createApp(App)

const httpClient = axios.create({
    baseURL: '/api',
})

app.provide(ChatClientKey, new ChatClient(httpClient))

app.mount('#app')
