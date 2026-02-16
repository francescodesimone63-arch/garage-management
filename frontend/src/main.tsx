import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import itIT from 'antd/locale/it_IT'
import dayjs from 'dayjs'
import 'dayjs/locale/it'
import App from './App'
import './index.css'

// Configura dayjs in italiano
dayjs.locale('it')

// Bloccare completamente messaggi inutili dalla console
const shouldIgnore = (args: any[]): boolean => {
  const str = args
    .map(arg => {
      try {
        return String(arg)
      } catch {
        return ''
      }
    })
    .join(' ')
    .toLowerCase()

  return (
    str.includes('bundle.js') ||
    str.includes('appsync') ||
    str.includes('devtools') ||
    str.includes('download the react') ||
    str.includes('promise') ||
    str.includes('unauthorized') ||
    str.includes('graphql 401') ||
    str.includes('content.bundle') ||
    str.includes('websocket')
  )
}

// Override console methods
const noop = () => {}
const originalError = console.error
const originalWarn = console.warn
const originalLog = console.log

console.error = function (...args: any[]) {
  if (!shouldIgnore(args)) {
    originalError.apply(console, args)
  }
}

console.warn = function (...args: any[]) {
  if (!shouldIgnore(args)) {
    originalWarn.apply(console, args)
  }
}

console.log = function (...args: any[]) {
  if (!shouldIgnore(args)) {
    originalLog.apply(console, args)
  }
}

// Bloccare unhandled promise rejections
window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
  const reason = String(event.reason || '')
  if (reason.includes('appsync') || reason.includes('bundle')) {
    event.preventDefault()
  }
})

// Configura React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minuti
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={itIT}
        theme={{
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
          },
        }}
      >
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <App />
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>
)
