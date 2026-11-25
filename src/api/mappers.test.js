import test from 'node:test'
import assert from 'node:assert/strict'
import { mapBackendComponent, mapCompatibilityResponse, mapRecommendationResponse, mergeRecommendationCatalog, toRecommendationRequest } from './mappers.js'
import { getCompatibilityRequestKey, getReplacementOptions } from '../logic/buildLogic.js'

const component = { id: 'abc', category: 'cpu_cooler', manufacturer: 'Noctua', model_name: 'NH-D15', specifications: { socket_support: ['AM5'], height_mm: 165 }, price: '99.00', currency: 'USD', price_source: 'demo', price_is_illustrative: true, source_name: 'supplemental', source_url: 'https://example.test' }

test('preserves backend identity, structured specs, provenance, and price labeling', () => {
  const mapped = mapBackendComponent(component)
  assert.equal(mapped.id, 'abc')
  assert.equal(mapped.category, 'cooler')
  assert.deepEqual(mapped.specifications, component.specifications)
  assert.equal(mapped.price, 99)
  assert.equal(mapped.priceIsIllustrative, true)
  assert.equal(mapped.sourceUrl, component.source_url)
})

test('maps recommendations without losing selected component IDs or details', () => {
  const selected = ['cpu', 'gpu', 'motherboard', 'memory', 'storage', 'psu', 'case', 'cpu_cooler'].map((category, index) => ({ ...component, id: `${category}-${index}`, category, model_name: `${category} model` }))
  const result = mapRecommendationResponse({ workload: 'gaming', budget_usd: '1500', estimated_total_price_usd: '1400', score: 80, scoring_summary: {}, explanations: {}, selected_components: selected, compatibility: { status: 'compatible', rules: [], explanations: [], missing_specifications: [] } })
  assert.equal(Object.keys(result.components).length, 8)
  assert.equal(result.estimatedTotalPrice, 1400)
  assert.equal(result.compatibility.status, 'compatible')
  assert.equal(result.components.cooler, 'cpu_cooler-7')
  assert.equal(result.componentDetails['cpu_cooler-7'].specifications.height_mm, 165)
})

test('renders nested cooler specifications as readable source data', () => {
  const mapped = mapBackendComponent({ ...component, category: 'cpu_cooler', specifications: { height_mm: 158, cooling: { design: 'single tower', heatpipes: 4, fans: 1 } } })
  assert.match(mapped.spec, /Cooling: Design: single tower, Heatpipes: 4, Fans: 1/)
  assert.doesNotMatch(mapped.spec, /\[object Object\]/)
})

test('merges recommendation records missing from the paged catalog response', () => {
  const selected = ['cpu', 'gpu', 'motherboard', 'memory', 'storage', 'psu', 'case', 'cpu_cooler'].map((category, index) => ({ ...component, id: `${category}-${index}`, category }))
  const recommendation = mapRecommendationResponse({ workload: 'gaming', budget_usd: '1500', estimated_total_price_usd: '1400', score: 80, scoring_summary: {}, explanations: {}, selected_components: selected, compatibility: { status: 'compatible', rules: [], explanations: [], missing_specifications: [] } })
  const catalog = mergeRecommendationCatalog({}, recommendation)
  assert.equal(Object.keys(catalog).length, 8)
  assert.equal(catalog[recommendation.components.cooler].name, 'Noctua NH-D15')
})

test('replacement candidates come from valid live catalog records', () => {
  const current = mapBackendComponent({ ...component, id: 'cooler-current', category: 'cpu_cooler' })
  const candidate = mapBackendComponent({ ...component, id: 'cooler-candidate', category: 'cpu_cooler', model_name: 'NH-U12S' })
  const options = getReplacementOptions('cooler', { components: { cooler: current.id } }, { [current.id]: current, [candidate.id]: candidate })
  assert.deepEqual(options.map((item) => item.id), ['cooler-candidate'])
  assert.equal(options[0].specifications.height_mm, 165)
})

test('compatibility request key changes when the build configuration changes', () => {
  const build = { components: { cpu: 'cpu-a', motherboard: 'board-a', gpu: 'gpu-a' } }
  assert.equal(getCompatibilityRequestKey({ ...build, components: { ...build.components } }), 'cpu-a|board-a|gpu-a')
  assert.notEqual(getCompatibilityRequestKey(build), getCompatibilityRequestKey({ components: { ...build.components, cpu: 'cpu-b' } }))
})

test('rejects incomplete recommendation payloads instead of producing a blank build', () => {
  assert.throws(() => mapRecommendationResponse({ selected_components: [component] }), /incomplete recommendation/)
})

test('normalizes unknown and incomplete rules as non-passing checks', () => {
  const result = mapCompatibilityResponse({ status: 'incomplete', rules: [{ rule: 'cooling', status: 'unknown', explanation: 'Need height', component_ids: ['abc'], missing_specifications: ['height_mm'] }] })
  assert.equal(result.checks[0].status, 'warning')
  assert.equal(result.errors.length, 1)
})

test('uses component names and power-rule details in compatibility results', () => {
  const result = mapCompatibilityResponse({ status: 'compatible', rules: [{ rule: 'psu_power_budget', status: 'compatible', explanation: 'PSU capacity 750W meets the estimated 600W requirement.', component_ids: ['cpu-id', 'psu-id'], missing_specifications: [], details: { estimated_system_power_w: 500, required_psu_w: 600 } }] }, { 'cpu-id': { name: 'AMD Ryzen 7' }, 'psu-id': { name: 'Corsair RM750' } })
  assert.equal(result.checks[0].title, 'PSU Power Budget')
  assert.equal(result.checks[0].components, 'AMD Ryzen 7 · Corsair RM750')
  assert.equal(result.checks[0].details.required_psu_w, 600)
})

test('maps frontend preferences to the backend contract', () => {
  assert.deepEqual(toRecommendationRequest({ budget: '1500', workload: 'creation', storageGb: '2000', wifiRequired: false, resolution: '1440p' }), { budget_usd: 1500, workload: 'content_creation', minimum_storage_gb: 2000, wifi_preference: 'any' })
})
