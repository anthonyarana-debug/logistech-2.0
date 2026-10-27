import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  workers: 2,
  retries: 0,
  timeout: 90000,
  expect: { timeout: 12000 },
  reporter: [
    ['list'],
    [
      'json',
      { outputFile: process.env.PW_REPORT || '../docs/evidencias/local/fase5-playwright.json' },
    ],
  ],
  use: {
    baseURL: process.env.PW_BASE_URL || 'http://127.0.0.1:5173',
    viewport: { width: 1440, height: 1000 },
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
})
