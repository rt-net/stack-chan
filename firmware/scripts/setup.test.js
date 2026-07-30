import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import test from 'node:test'

import { ESP_IDF_VERSION, MODDABLE_VERSION, ensureEspIdf, getEspIdfPath, getXsDevArguments } from './setup.js'

function git(directory, args) {
  const result = spawnSync('git', args, {
    cwd: directory,
    encoding: 'utf8',
  })
  assert.equal(result.status, 0, result.stderr)
  return result.stdout.trim()
}

test('pins the Moddable version for the host setup', () => {
  assert.deepEqual(getXsDevArguments([]), ['setup', '--branch', MODDABLE_VERSION])
})

test('passes device options through without applying the Moddable branch', () => {
  assert.deepEqual(getXsDevArguments(['--device=esp32']), ['setup', '--device=esp32'])
  assert.deepEqual(getXsDevArguments(['--device', 'esp32']), ['setup', '--device', 'esp32'])
})

test('uses the same Linux installation path as xs-dev', () => {
  assert.equal(getEspIdfPath('linux', '/tmp/test-home'), '/tmp/test-home/.local/share/esp32/esp-idf')
})

test('clones the pinned ESP-IDF version when it is not installed', () => {
  const temporaryDirectory = mkdtempSync(resolve(tmpdir(), 'stack-chan-setup-test-'))
  const idfPath = resolve(temporaryDirectory, 'esp32', 'esp-idf')
  const calls = []

  try {
    ensureEspIdf(idfPath, (command, args) => {
      calls.push([command, args])
      return { status: 0, stdout: '' }
    })

    assert.equal(calls.length, 1)
    assert.equal(calls[0][0], 'git')
    assert.equal(calls[0][1][0], 'clone')
    assert.equal(calls[0][1][calls[0][1].indexOf('--branch') + 1], ESP_IDF_VERSION)
    assert.ok(calls[0][1].includes('--recurse-submodules'))
    assert.ok(calls[0][1].includes('--shallow-submodules'))
    assert.equal(calls[0][1].at(-1), idfPath)
  } finally {
    rmSync(temporaryDirectory, { recursive: true, force: true })
  }
})

test('switches an existing clean ESP-IDF repository to the pinned tag', () => {
  const temporaryDirectory = mkdtempSync(resolve(tmpdir(), 'stack-chan-setup-test-'))
  const idfPath = resolve(temporaryDirectory, 'esp-idf')
  mkdirSync(idfPath)

  try {
    git(idfPath, ['init', '--quiet'])
    git(idfPath, ['config', 'user.name', 'Stack-chan Setup Test'])
    git(idfPath, ['config', 'user.email', 'setup-test@example.com'])
    git(idfPath, ['commit', '--quiet', '--allow-empty', '-m', 'ESP-IDF v5.3'])
    git(idfPath, ['tag', ESP_IDF_VERSION])
    const expectedCommit = git(idfPath, ['rev-parse', 'HEAD'])
    git(idfPath, ['commit', '--quiet', '--allow-empty', '-m', 'Newer ESP-IDF'])

    ensureEspIdf(idfPath)

    assert.equal(git(idfPath, ['rev-parse', 'HEAD']), expectedCommit)
  } finally {
    rmSync(temporaryDirectory, { recursive: true, force: true })
  }
})
