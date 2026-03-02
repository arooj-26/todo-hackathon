/**
 * Runtime configuration for API URLs
 *
 * This module provides runtime URL detection for Kubernetes/Minikube deployments.
 * Since NEXT_PUBLIC_* env vars are baked at build time, we need runtime detection.
 *
 * How it works:
 * 1. If running in browser, detect based on current hostname
 * 2. For Minikube: use the same hostname with backend NodePort
 * 3. For port-forward: use localhost with forwarded port
 * 4. For local dev: use localhost:8000
 */

/**
 * Get the backend API URL based on the current environment
 */
export function getApiBaseUrl(): string {
  // Use env var if explicitly set (works both server-side and client-side in Next.js)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }

  // Server-side rendering fallback
  if (typeof window === 'undefined') {
    return 'http://localhost:8000'
  }

  // Check for manually configured URL in localStorage (for Windows/special setups)
  const configuredUrl = localStorage.getItem('backend_api_url')
  if (configuredUrl) {
    return configuredUrl
  }

  const hostname = window.location.hostname
  const protocol = window.location.protocol

  // Local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Check if we're using port-forward (frontend on 3000, backend on 8000)
    if (window.location.port === '3000') {
      return 'http://localhost:8000'
    }
    return `${protocol}//localhost:8000`
  }

  // Minikube IP detection (usually 192.168.x.x or similar)
  // Backend NodePort is 31850
  if (hostname.match(/^192\.168\.\d+\.\d+$/) ||
      hostname.match(/^10\.\d+\.\d+\.\d+$/) ||
      hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+$/)) {
    return `${protocol}//${hostname}:31850`
  }

  // Default: assume same host with backend on port 8000
  return `${protocol}//${hostname}:8000`
}

/**
 * Get the chatbot API URL based on the current environment
 * Chatbot backend runs on port 8001 (NodePort 31851)
 */
export function getChatbotApiUrl(): string {
  // Use env var if explicitly set (works both server-side and client-side in Next.js)
  if (process.env.NEXT_PUBLIC_CHATBOT_API_URL) {
    return process.env.NEXT_PUBLIC_CHATBOT_API_URL
  }

  // Server-side rendering fallback
  if (typeof window === 'undefined') {
    return 'http://localhost:8001'
  }

  // Check for manually configured URL in localStorage
  const configuredUrl = localStorage.getItem('chatbot_api_url')
  if (configuredUrl) {
    return configuredUrl
  }

  const hostname = window.location.hostname
  const protocol = window.location.protocol

  // Local development - chatbot on port 8001
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8001'
  }

  // Minikube IP detection - Chatbot NodePort is 31851
  if (hostname.match(/^192\.168\.\d+\.\d+$/) ||
      hostname.match(/^10\.\d+\.\d+\.\d+$/) ||
      hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+$/)) {
    return `${protocol}//${hostname}:31851`
  }

  // Default: assume same host with chatbot on port 8001
  return `${protocol}//${hostname}:8001`
}

/**
 * Configure backend URL manually (useful for Windows/WSL setups)
 * Call this from browser console: window.configureBackendUrl('http://localhost:8000')
 */
if (typeof window !== 'undefined') {
  (window as any).configureBackendUrl = (url: string) => {
    localStorage.setItem('backend_api_url', url)
    console.log(`Backend URL configured: ${url}`)
    console.log('Refresh the page to apply changes.')
  };

  (window as any).clearBackendUrl = () => {
    localStorage.removeItem('backend_api_url')
    console.log('Backend URL cleared. Will use auto-detection.')
    console.log('Refresh the page to apply changes.')
  };

  (window as any).getBackendUrl = () => {
    return getApiBaseUrl()
  };
}

export default { getApiBaseUrl }
