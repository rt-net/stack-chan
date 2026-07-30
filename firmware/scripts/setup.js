import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync } from 'node:fs'
import { homedir, type as osType } from 'node:os'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const MODDABLE_VERSION = '4.9.5'
const ESP_IDF_VERSION = 'v5.3'

const ESP_IDF_REPOSITORY = 'https://github.com/espressif/esp-idf.git'
const projectDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const xsDevCli = resolve(projectDirectory, 'node_modules', 'xs-dev', 'build', 'src', 'cli.js')

function run(command, args, cwd = projectDirectory, capture = false) {
  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    stdio: capture ? ['ignore', 'pipe', 'inherit'] : 'inherit',
  })

  if (result.status !== 0) {
    throw new Error(`Command failed with exit code ${result.status}: ${command} ${args.join(' ')}`)
  }

  return result
}

function getEspIdfPath() {
  const installDirectory =
    osType().toLowerCase() === 'windows_nt' ? resolve(homedir(), 'xs-dev') : resolve(homedir(), '.local', 'share')

  return resolve(installDirectory, 'esp32', 'esp-idf')
}

function ensureEspIdf() {
  const idfPath = getEspIdfPath()
  if (!existsSync(idfPath)) {
    mkdirSync(dirname(idfPath), { recursive: true })
    console.log(`Installing ESP-IDF ${ESP_IDF_VERSION} at ${idfPath}`)
    run('git', [
      'clone',
      '--depth',
      '1',
      '--single-branch',
      '--branch',
      ESP_IDF_VERSION,
      '--recurse-submodules',
      '--shallow-submodules',
      ESP_IDF_REPOSITORY,
      idfPath,
    ])
    return
  }

  const status = run('git', ['status', '--porcelain'], idfPath, true).stdout.trim()
  if (status !== '') {
    throw new Error(
      `ESP-IDF has local changes. Commit or remove them before switching to ${ESP_IDF_VERSION}:\n${status}`
    )
  }

  console.log(`Switching ESP-IDF at ${idfPath} to ${ESP_IDF_VERSION}`)
  run('git', ['fetch', '--depth', '1', 'origin', 'tag', ESP_IDF_VERSION], idfPath)
  run('git', ['checkout', '--detach', ESP_IDF_VERSION], idfPath)
  run('git', ['submodule', 'update', '--init', '--recursive', '--depth', '1'], idfPath)
}

function main() {
  const args = process.argv.slice(2)
  if (!existsSync(xsDevCli)) {
    throw new Error('xs-dev is not installed. Run `npm install` first.')
  }

  const deviceOption = args.findIndex((arg) => arg === '--device')
  const assignedDevice = args.find((arg) => arg.startsWith('--device='))?.slice('--device='.length)
  const device = assignedDevice ?? (deviceOption === -1 ? undefined : args[deviceOption + 1])
  const showsHelp = args.includes('--help') || args.includes('-h')
  if (device === 'esp32' && !showsHelp) {
    ensureEspIdf()
  }

  const xsDevArguments = device === undefined ? ['setup', '--branch', MODDABLE_VERSION, ...args] : ['setup', ...args]
  run(process.execPath, [xsDevCli, ...xsDevArguments])
}

try {
  main()
} catch (error) {
  console.error(`Stack-chan setup failed: ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
}
