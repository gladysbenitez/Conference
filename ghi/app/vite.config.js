import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3001,
    // // add the next lines if you're using windows and hot reload doesn't work
    // watch: {
    //     usePolling: true
    // }
  }
})
