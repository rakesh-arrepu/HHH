import React from 'react'
import { createRoot } from 'react-dom/client'
import { ApolloProvider } from '@apollo/client/react'
import App from './App'
import { client } from './lib/apollo'
import './index.css'

const rootEl = document.getElementById('root')
if (!rootEl) {
  throw new Error('Root element not found')
}
createRoot(rootEl).render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>
)
