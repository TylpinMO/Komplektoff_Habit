import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

test('production build contains the dashboard shell', async () => {
	const html = await readFile(new URL('../dist/index.html', import.meta.url), 'utf8')
	assert.match(html, /<div id="root"><\/div>/)
	assert.match(html, /Komplektoff Habit/)
})
