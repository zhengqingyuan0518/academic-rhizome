import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 将所有以 /api 开头的请求，代理到 http://127.0.0.1:5000
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true, // 必须设置为 true
      },
    }
  }
})
