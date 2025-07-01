import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@src': path.resolve(__dirname, './src'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@components': path.resolve(__dirname, './src/components'),
      '@video': path.resolve(__dirname, './public/video'),
      '@img': path.resolve(__dirname, './public/img'),
      '@svg': path.resolve(__dirname, './assets/svg'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', 
        changeOrigin: true,
        secure: false, // Ignorar HTTPS en caso de uso local
      },
    },
  },
});
