const categoryNames = { cpu_cooler: 'cooler' }
const formatSpecValue = (value) => Array.isArray(value) ? value.join(', ') : value && typeof value === 'object' ? Object.entries(value).map(([key, nestedValue]) => `${titleCase(key)}: ${formatSpecValue(nestedValue)}`).join(', ') : String(value)
const titleCase = (value) => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()).replace(/\bPsu\b/g, 'PSU').replace(/\bCpu\b/g, 'CPU').replace(/\bGpu\b/g, 'GPU')

export function mapBackendComponent(component) {
  if (!component || typeof component !== 'object' || !component.id || !component.category || !component.manufacturer || !component.model_name) {
    throw new Error('The backend returned a malformed component record. No build was displayed.')
  }
  const specs = component.specifications || {}
  const category = categoryNames[component.category] || component.category
  const price = component.price == null ? null : Number(component.price)
  const summary = Object.entries(specs).slice(0, 4).map(([key, value]) => `${titleCase(key)}: ${formatSpecValue(value)}`).join(' · ')
  return {
    ...component,
    id: String(component.id),
    category,
    backendCategory: component.category,
    name: `${component.manufacturer} ${component.model_name}`.trim(),
    spec: summary || 'Specifications not provided by source.',
    price,
    power: Number(specs.tdp_w || specs.tgp_w || specs.power_w || 0),
    performance: Number(specs.performance_score || 0),
    upgradeability: Number(specs.upgradeability_score || 0),
    specifications: specs,
    priceIsIllustrative: component.price_is_illustrative,
    priceSource: component.price_source,
    source: component.source_name || 'Unattributed source',
    sourceUrl: component.source_url,
  }
}

export function mapCatalogResponse(response) {
  return (response?.items || []).map(mapBackendComponent)
}

export function mapCompatibilityResponse(response, componentLookup = {}) {
  const rules = response?.rules || []
  const checks = rules.map((rule) => ({
    id: rule.rule,
    title: titleCase(rule.rule),
    status: rule.status === 'compatible' ? 'pass' : rule.status === 'incompatible' ? 'error' : 'warning',
    explanation: rule.explanation,
    components: rule.component_ids.join(' · '),
    componentIds: rule.component_ids,
    details: rule.details || {},
    missingSpecifications: rule.missing_specifications,
  }))
  return {
    ...response,
    checks: checks.map((check) => ({ ...check, components: check.componentIds.map((id) => componentLookup[id]?.name || id).join(' · ') })),
    errors: checks.filter((check) => check.status === 'error' || check.status === 'warning'),
    warnings: checks.filter((check) => check.status === 'warning'),
  }
}

export function mapRecommendationResponse(response) {
  const categories = new Set((response?.selected_components || []).map((item) => item?.category))
  const expectedCategories = new Set(['cpu', 'gpu', 'motherboard', 'memory', 'storage', 'psu', 'case', 'cpu_cooler'])
  if (!response || !Array.isArray(response.selected_components) || response.selected_components.length !== 8 || categories.size !== expectedCategories.size || [...expectedCategories].some((category) => !categories.has(category))) {
    throw new Error('The backend returned an incomplete recommendation. No build was displayed.')
  }
  const explanations = response.explanations || {}
  const selected = (response?.selected_components || []).map(mapBackendComponent).map((item) => ({ ...item, reason: explanations[item.category] || null }))
  const components = Object.fromEntries(selected.map((item) => [item.category, item.id]))
  const componentDetails = Object.fromEntries(selected.map((item) => [item.id, item]))
  return {
    id: `recommendation-${Date.now()}`,
    name: `${titleCase(response.workload)} Recommendation`,
    components,
    componentDetails,
    estimatedTotalPrice: Number(response.estimated_total_price_usd),
    score: response.score,
    scoringSummary: response.scoring_summary,
    explanations: response.explanations,
    metrics: {
      recommendationScore: Number.isFinite(Number(response.score)) ? Number(response.score) : null,
      performanceProxy: Number.isFinite(Number(response.scoring_summary?.performance_proxy)) ? Number(response.scoring_summary.performance_proxy) : null,
      upgradeabilityScore: null,
    },
    compatibility: mapCompatibilityResponse(response.compatibility, componentDetails),
    workload: response.workload,
    budget: Number(response.budget_usd),
  }
}

export function mergeRecommendationCatalog(catalog, recommendation) {
  return { ...catalog, ...(recommendation?.componentDetails || {}) }
}

export function toRecommendationRequest(preferences) {
  return {
    budget_usd: Number(preferences.budget),
    workload: preferences.workload === 'creation' ? 'content_creation' : preferences.workload,
    minimum_storage_gb: Number(preferences.storageGb),
    wifi_preference: preferences.wifiRequired ? 'required' : 'any',
    ...(preferences.workload === 'gaming' ? { gaming_resolution: preferences.resolution === '4K' ? '4k' : preferences.resolution } : {}),
  }
}
