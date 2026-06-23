import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1', // Принудительно запускаем на IPv4
    port: 5173,        // Стандартный порт
    open: true,        // Автоматически открывать браузер при запуске!
  }
})
