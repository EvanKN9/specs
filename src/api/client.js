const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, status = 0, body = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...(options.headers || {}) },
    })
  } catch (error) {
    throw new ApiError('The backend is unavailable. Start FastAPI and try again.', 0, error)
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = typeof body?.detail === 'string' ? body.detail : body?.detail?.message
    throw new ApiError(detail || `Backend request failed (${response.status}).`, response.status, body)
  }
  return body
}

export const api = {
  async listComponents({ category, limit = 100 } = {}) {
    const params = new URLSearchParams({ limit: String(limit) })
    if (category && category !== 'all') params.set('category', category === 'cooler' ? 'cpu_cooler' : category)
    return request(`/components?${params}`)
  },
  getComponent(id) { return request(`/components/${id}`) },
  recommend(preferences) { return request('/builds/recommend', { method: 'POST', body: JSON.stringify(preferences) }) },
  checkCompatibility(componentIds) { return request('/compatibility/check', { method: 'POST', body: JSON.stringify({ component_ids: componentIds }) }) },
}

export { API_BASE_URL }
