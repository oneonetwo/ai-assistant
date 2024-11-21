import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    plugins: [
      vue(),
      Components({
        resolvers: [VantResolver()]
      }),
      viteCompression(),
      visualizer()
    ],
    css: {
      preprocessorOptions: {
        scss: {
          sassOptions: {
            outputStyle: 'compressed'
          }
        }
      }
    },
    server: {
      port: 3000,
      proxy: {
        // 代理 API 请求
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
          ws: true,
          // 重写路径
          rewrite: (path) => path.replace(/^\/api/, ''),
          // 配置代理调试日志
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('proxy error', err)
            })
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('Sending Request:', req.method, req.url)
            })
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('Received Response:', proxyRes.statusCode, req.url)
            })
          }
        },
        // 代理 Swagger 文档
        '/docs': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false
        },
        // 代理 OpenAPI 文档
        '/openapi.json': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'ui': ['vant'],
            'markdown': ['marked', 'highlight.js']
          }
        }
      },
      chunkSizeWarningLimit: 1000,
      sourcemap: false,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      }
    }
  }
})
