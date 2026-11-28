import test from 'node:test'
import assert from 'node:assert/strict'
import { getBuildMetrics, getInstalledPsuWatts } from './buildLogic.js'

const catalog = {
  'psu-1': { id: 'psu-1', category: 'psu', price: 99, specs: { wattage_w: 750 } },
  'cpu-1': { id: 'cpu-1', category: 'cpu', price: 200, specs: { tdp_w: 65 } },
}

const build = { components: { cpu: 'cpu-1', psu: 'psu-1' } }

test('summary metrics expose current price and draw without unsupported scores', () => {
  const metrics = getBuildMetrics(build, catalog)
  assert.equal(metrics.total, 299)
  assert.equal(metrics.installedPsuWatts, 750)
  assert.equal(metrics.estimatedSystemPowerWatts, null)
  assert.equal('performanceScore' in metrics, false)
  assert.equal('upgradeabilityScore' in metrics, false)
})

test('installed PSU capacity is unavailable when the selected PSU lacks wattage', () => {
  assert.equal(getInstalledPsuWatts({ components: { psu: 'missing' } }, catalog), null)
})
