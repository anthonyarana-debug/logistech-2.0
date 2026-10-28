import { defineConfig } from '@playwright/test'

// A private local CA is verified separately with its trust chain. Never suppress
// certificate validation against an Internet deployment.
if (process.env.PW_REHEARSAL_TLS === 'true' &&
    new URL(process.env.PW_BASE_URL || 'http://127.0.0.1:5173').hostname !== 'localhost')
  throw new Error('Private-CA browser override is restricted to localhost rehearsal.')

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
    ignoreHTTPSErrors: process.env.PW_REHEARSAL_TLS === 'true',
    baseURL: process.env.PW_BASE_URL || 'http://127.0.0.1:5173',
    viewport: { width: 1440, height: 1000 },
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
})
