export const preferences = {
  budget: '1500',
  workload: 'gaming',
  resolution: '1440p',
  storageGb: '2000',
  wifiRequired: true,
}

export const components = {
  cpu01: { id: 'cpu01', category: 'cpu', name: 'AMD Ryzen 7 7700', price: 279, spec: '8 cores · AM5 socket', power: 65, performance: 82, upgradeability: 88, socket: 'AM5' },
  cpu02: { id: 'cpu02', category: 'cpu', name: 'AMD Ryzen 5 7600', price: 199, spec: '6 cores · AM5 socket', power: 65, performance: 76, upgradeability: 88, socket: 'AM5', reason: 'Saves budget while preserving the same AM5 upgrade path.', tradeoff: 'Lower multi-core performance for creation workloads.' },
  cpu03: { id: 'cpu03', category: 'cpu', name: 'Intel Core i5-14600K', price: 319, spec: '14 cores · LGA1700 socket', power: 125, performance: 91, upgradeability: 68, socket: 'LGA1700', reason: 'Adds strong mixed-use performance.', tradeoff: 'Incompatible with the current AM5 motherboard.' },
  cooler01: { id: 'cooler01', category: 'cooler', name: 'QuietFlow 120 Air Cooler', price: 39, spec: '120 mm tower · 155 mm height', power: 0, performance: 0, upgradeability: 78, socket: 'AM5' },
  board01: { id: 'board01', category: 'motherboard', name: 'B650 Wi-Fi Creator', price: 169, spec: 'ATX · DDR5 · Wi-Fi 6E', power: 35, performance: 0, upgradeability: 90, socket: 'AM5', formFactor: 'ATX', wifi: true, memory: 'DDR5', reason: 'Matches the CPU, adds Wi-Fi, and leaves room for upgrades.', tradeoff: 'Full ATX footprint uses more case space.' },
  board02: { id: 'board02', category: 'motherboard', name: 'B650M Compact Wi-Fi', price: 139, spec: 'Micro ATX · DDR5 · Wi-Fi 6', power: 30, performance: 0, upgradeability: 76, socket: 'AM5', formFactor: 'Micro ATX', wifi: true, memory: 'DDR5', reason: 'Cuts cost and footprint without changing the socket.', tradeoff: 'Fewer expansion slots for future add-ons.' },
  board03: { id: 'board03', category: 'motherboard', name: 'B760 DDR5 Wi-Fi', price: 159, spec: 'ATX · DDR5 · LGA1700', power: 35, performance: 0, upgradeability: 70, socket: 'LGA1700', formFactor: 'ATX', wifi: true, memory: 'DDR5', reason: 'A capable Intel platform alternative.', tradeoff: 'Incompatible with the current AM5 CPU.' },
  memory01: { id: 'memory01', category: 'memory', name: '32 GB DDR5-6000 Kit', price: 99, spec: '2 × 16 GB · DDR5-6000', power: 8, performance: 78, upgradeability: 82, memory: 'DDR5', reason: 'Enough capacity for modern games and multitasking.', tradeoff: 'Uses two of four memory slots.' },
  memory02: { id: 'memory02', category: 'memory', name: '32 GB DDR5-5600 Kit', price: 84, spec: '2 × 16 GB · DDR5-5600', power: 8, performance: 75, upgradeability: 82, memory: 'DDR5', reason: 'Saves a little budget with a small speed trade-off.', tradeoff: 'Slightly lower memory bandwidth.' },
  memory03: { id: 'memory03', category: 'memory', name: '32 GB DDR4-3200 Kit', price: 59, spec: '2 × 16 GB · DDR4-3200', power: 8, performance: 66, upgradeability: 55, memory: 'DDR4', reason: 'A lower-cost memory generation option.', tradeoff: 'Incompatible with the selected DDR5 motherboard.' },
  gpu01: { id: 'gpu01', category: 'gpu', name: 'Radeon RX 7800 XT', price: 489, spec: '16 GB · 1440p class · 263 W', power: 263, performance: 92, upgradeability: 80, length: 303, reason: 'Puts the largest share of budget toward 1440p performance.', tradeoff: 'Higher power draw than the efficiency-focused alternatives.' },
  gpu02: { id: 'gpu02', category: 'gpu', name: 'GeForce RTX 4070 Super', price: 599, spec: '12 GB · RT capable · 220 W', power: 220, performance: 96, upgradeability: 84, length: 305, reason: 'Adds stronger ray-tracing performance for demanding 1440p games.', tradeoff: 'Costs more and has less VRAM.' },
  gpu03: { id: 'gpu03', category: 'gpu', name: 'Radeon RX 7700 XT', price: 399, spec: '12 GB · 1440p class · 245 W', power: 245, performance: 84, upgradeability: 77, length: 280, reason: 'Frees budget while keeping a strong 1440p target.', tradeoff: 'Lower frame-rate headroom at higher settings.' },
  gpu04: { id: 'gpu04', category: 'gpu', name: 'Oversize XTX Prototype', price: 549, spec: '24 GB · 1440p class · 355 mm', power: 320, performance: 98, upgradeability: 82, length: 355, reason: 'A deliberate fit test for the compatibility engine.', tradeoff: '20 mm longer than the current case clearance.' },
  storage01: { id: 'storage01', category: 'storage', name: '2 TB NVMe Gen4 SSD', price: 119, spec: '7,000 MB/s · PCIe 4.0', power: 6, performance: 80, upgradeability: 88, interface: 'PCIe 4.0', capacity: 2000 },
  psu01: { id: 'psu01', category: 'psu', name: '750 W Gold Modular PSU', price: 109, spec: '750 W · 80+ Gold · modular', power: 0, performance: 0, upgradeability: 87, watts: 750, reason: 'Provides healthy headroom for the GPU and future upgrades.', tradeoff: 'Costs more than a basic Bronze unit.' },
  psu02: { id: 'psu02', category: 'psu', name: '850 W Gold Modular PSU', price: 139, spec: '850 W · 80+ Gold · modular', power: 0, performance: 0, upgradeability: 94, watts: 850, reason: 'Creates more room for a future graphics card upgrade.', tradeoff: 'Adds cost without increasing current frame rates.' },
  psu03: { id: 'psu03', category: 'psu', name: '600 W Bronze PSU', price: 69, spec: '600 W · 80+ Bronze · fixed cable', power: 0, performance: 0, upgradeability: 61, watts: 600, reason: 'Reduces cost for a lower-power configuration.', tradeoff: 'Can become tight with the current high-draw GPU.' },
  case01: { id: 'case01', category: 'case', name: 'Northline Airflow ATX Case', price: 89, spec: 'ATX mid tower · 340 mm GPU clearance', power: 0, performance: 0, upgradeability: 86, formFactor: 'ATX', gpuClearance: 340, coolerClearance: 165 },
}

export const builds = {
  balanced1440p: {
    id: 'balanced1440p',
    name: 'Balanced 1440p Gaming Build',
    components: { cpu: 'cpu01', cooler: 'cooler01', motherboard: 'board01', memory: 'memory01', gpu: 'gpu01', storage: 'storage01', psu: 'psu01', case: 'case01' },
  },
}
