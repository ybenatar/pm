import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8000',
    headless: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Expects the Docker container to be running at port 8000
  webServer: {
    command: 'echo "Using Docker container at port 8000"',
    url: 'http://localhost:8000/api/health',
    reuseExistingServer: true,
    timeout: 10000,
  },
})
