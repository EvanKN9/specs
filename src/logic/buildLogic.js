import { builds, components } from '../data/mockData'

export function cloneBuild(build) {
  return { ...build, components: { ...build.components } }
}

export function generateMockBuild(preferences) {
  const build = cloneBuild(builds.balanced1440p)
  const budget = Number(preferences.budget || 1500)
  const workload = preferences.workload
  if (budget < 1300) {
    build.components.gpu = 'gpu03'
    build.components.cpu = 'cpu02'
  } else if (budget >= 1750) {
    build.components.gpu = 'gpu02'
  }
  if (workload === 'development') build.components.cpu = budget >= 1600 ? 'cpu01' : 'cpu02'
  if (workload === 'creation') build.components.cpu = 'cpu01'
  if (workload === 'productivity' || workload === 'general') {
    build.components.gpu = 'gpu03'
    build.components.cpu = 'cpu02'
  }
  if (Number(preferences.storageGb) >= 4000) build.components.storage = 'storage01'
  return { ...build, name: `${workload || 'balanced'} mock recommendation` }
}

export function getBuildMetrics(build) {
  const parts = Object.values(build.components).map((id) => components[id]).filter(Boolean)
  return {
    total: parts.reduce((sum, item) => sum + item.price, 0),
    powerWatts: parts.reduce((sum, item) => sum + item.power, 0),
    performanceScore: Math.round(parts.reduce((sum, item) => sum + item.performance, 0) / 2.1),
    upgradeabilityScore: Math.round(parts.reduce((sum, item) => sum + item.upgradeability, 0) / parts.length),
  }
}

export function getChangedCategories(originalBuild, currentBuild) {
  if (!originalBuild || !currentBuild) return []
  return Object.keys(currentBuild.components).filter((category) => originalBuild.components[category] !== currentBuild.components[category])
}

export function checkCompatibility(build) {
  const cpu = components[build.components.cpu]
  const board = components[build.components.motherboard]
  const memory = components[build.components.memory]
  const gpu = components[build.components.gpu]
  const psu = components[build.components.psu]
  const cooler = components[build.components.cooler]
  const storage = components[build.components.storage]
  const casePart = components[build.components.case]
  const metrics = getBuildMetrics(build)
  const checks = []
  const addCheck = (id, title, passed, explanation, responsible) => checks.push({ id, title, status: passed ? 'pass' : 'error', explanation, components: responsible })

  if (cpu && board) addCheck('socket', 'CPU and motherboard socket', cpu.socket === board.socket, cpu.socket === board.socket ? `Both components use the ${cpu.socket} socket.` : `${cpu.name} uses ${cpu.socket}, but ${board.name} uses ${board.socket}.`, `${cpu.name} · ${board.name}`)
  if (memory && board) addCheck('memory', 'Memory generation', memory.memory === board.memory, memory.memory === board.memory ? `The motherboard supports the ${memory.memory} memory kit selected.` : `${board.name} supports ${board.memory}, but this kit uses ${memory.memory}.`, `${board.name} · ${memory.name}`)
  if (board && casePart) addCheck('form-factor', 'Motherboard and case fit', board.formFactor === 'ATX' ? casePart.formFactor === 'ATX' : true, `${board.formFactor} motherboard fits the ${casePart.formFactor} case.`, `${board.name} · ${casePart.name}`)
  if (psu && gpu) addCheck('power', 'Power headroom', psu.watts >= metrics.powerWatts + 100, psu.watts >= metrics.powerWatts + 100 ? `${psu.watts} W provides room above the estimated ${metrics.powerWatts} W system draw.` : `${psu.name} leaves less than 100 W of headroom above the estimated ${metrics.powerWatts} W draw.`, `${psu.name} · ${gpu.name}`)
  if (gpu && casePart) addCheck('gpu-clearance', 'Graphics card clearance', gpu.length <= casePart.gpuClearance, gpu.length <= casePart.gpuClearance ? `${gpu.length} mm graphics card fits within ${casePart.gpuClearance} mm of case clearance.` : `${gpu.name} is ${gpu.length - casePart.gpuClearance} mm longer than the case allows.`, `${gpu.name} · ${casePart.name}`)
  if (cooler && casePart) addCheck('cooling', 'CPU cooling clearance', true, `The cooler height fits within the case's ${casePart.coolerClearance} mm limit.`, `${cooler.name} · ${casePart.name}`)
  if (storage && board) addCheck('storage', 'Storage interface', storage.interface === 'PCIe 4.0', `The motherboard supports the drive's ${storage.interface} interface.`, `${storage.name} · ${board.name}`)
  const errors = checks.filter((check) => check.status === 'error')
  return { status: errors.length ? 'incompatible' : 'compatible', checks, warnings: [], errors }
}

export function getReplacementOptions(category, build) {
  const currentId = build.components[category]
  return Object.values(components).filter((item) => item.category === category && item.id !== currentId).map((item) => ({ ...item, reason: item.reason || 'A considered alternative for this system.', tradeoff: item.tradeoff || 'Changes the balance of the build.' }))
}
