import { test, expect } from '@playwright/test'

test.describe('Kanban Board', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('loads with 5 columns and dummy cards', async ({ page }) => {
    const columns = page.locator('[id^="column-"]')
    await expect(columns).toHaveCount(5)

    // At least one card should be visible
    const cards = page.locator('.card')
    await expect(cards.first()).toBeVisible()
  })

  test('renames a column', async ({ page }) => {
    // Click the first column name to enter edit mode
    const firstColName = page.locator('.column-name').first()
    await firstColName.click()

    // Type new name in the input
    const input = page.locator('.column-name-input').first()
    await input.clear()
    await input.fill('Sprint 1')
    await input.press('Enter')

    // Column should now show the new name
    await expect(page.locator('.column-name').first()).toHaveText('Sprint 1')
  })

  test('adds a card to a column', async ({ page }) => {
    // Get the first column and click its add button
    const firstCol = page.locator('[id^="column-"]').first()
    const colId = await firstCol.getAttribute('id').then(id => id?.replace('column-', ''))

    const addBtn = page.locator(`#add-card-btn-${colId}`)
    await addBtn.click()

    // Fill the form
    await page.locator(`#new-card-title-${colId}`).fill('My new test card')
    await page.locator(`#new-card-details-${colId}`).fill('Test details')
    await page.locator(`#submit-card-${colId}`).click()

    // Card should now appear in the column
    await expect(firstCol.locator('.card-title').filter({ hasText: 'My new test card' })).toBeVisible()
  })

  test('deletes a card', async ({ page }) => {
    const firstCol = page.locator('[id^="column-"]').first()
    // Hover first card to reveal delete button
    const firstCard = firstCol.locator('.card').first()
    const cardTitle = await firstCard.locator('.card-title').textContent()

    await firstCard.hover()
    await firstCard.locator('.card-delete').click()

    // Card should be gone
    await expect(firstCol.locator('.card-title').filter({ hasText: cardTitle! })).toHaveCount(0)
  })

  test('drags a card from one column to another', async ({ page }) => {
    // Grab the first card from column 1
    const col1 = page.locator('[id^="column-"]').nth(0)
    const col2 = page.locator('[id^="column-"]').nth(1)

    const card = col1.locator('.card').first()
    const cardTitle = await card.locator('.card-title').textContent()

    const col1CountBefore = await col1.locator('.card').count()
    const col2CountBefore = await col2.locator('.card').count()

    // Drag to column 2
    const target = col2.locator('.card-list')
    await card.dragTo(target)

    // Column 1 should have one fewer card, column 2 one more
    await expect(col1.locator('.card')).toHaveCount(col1CountBefore - 1)
    await expect(col2.locator('.card')).toHaveCount(col2CountBefore + 1)

    // The dragged card should now be in column 2
    await expect(col2.locator('.card-title').filter({ hasText: cardTitle! })).toBeVisible()
  })
})
