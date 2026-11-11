const { readFileSync, mkdirSync } = require('node:fs')
const { join } = require('node:path')
const { chromium } = require('../frontend/node_modules/playwright')

const palette = { field: '#1659a3', action: '#167047', warning: '#a85406', error: '#b42730' }

function callout([x, y, width, height, kind], index) {
  const color = palette[kind]
  const left = x > 20
  const badgeX = left ? x - 11 : x + width + 11
  const badgeY = Math.min(216, Math.max(9, y + height / 2))
  const edge = left ? x : x + width
  const direction = left ? -1 : 1
  return `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="2" fill="none" stroke="white" stroke-width="2.8"/>
  <rect x="${x}" y="${y}" width="${width}" height="${height}" rx="2" fill="none" stroke="${color}" stroke-width="1.4"/>
  <path d="M ${badgeX} ${badgeY} H ${edge} M ${edge + 3 * direction} ${badgeY - 2} L ${edge} ${badgeY} L ${edge + 3 * direction} ${badgeY + 2}" fill="none" stroke="${color}" stroke-width="1.4"/>
  <circle cx="${badgeX}" cy="${badgeY}" r="5.5" fill="${color}" stroke="white" stroke-width="0.8"/>
  <text x="${badgeX}" y="${badgeY + 2.4}" text-anchor="middle" font-family="Arial" font-size="7" font-weight="bold" fill="white">${index + 1}</text>`
}

async function main() {
  const [manifest, output] = process.argv.slice(2)
  const figures = JSON.parse(readFileSync(manifest, 'utf8'))
  mkdirSync(output, { recursive: true })
  const browser = await chromium.launch()
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
    for (const { id, path, width, height, marks } of figures) {
      const mime = /\.jpe?g$/i.test(path) ? 'jpeg' : 'png'
      const data = readFileSync(path).toString('base64')
      await page.setViewportSize({ width, height })
      await page.setContent(`<body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 324 225" preserveAspectRatio="none">
      <image width="324" height="225" preserveAspectRatio="none" href="data:image/${mime};base64,${data}"/>
      ${marks.map(callout).join('')}
      </svg></body>`)
      await page.locator('svg').screenshot({ path: join(output, `${id}.png`) })
    }
  } finally {
    await browser.close()
  }
}

main().catch(error => { console.error(error); process.exitCode = 1 })
