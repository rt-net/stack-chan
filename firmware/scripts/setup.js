import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync } from 'node:fs'
import { homedir, type as osType } from 'node:os'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const MODDABLE_VERSION = '4.9.5'
export const ESP_IDF_VERSION = 'v5.3'

const ESP_IDF_REPOSITORY = 'https://github.com/espressif/esp-idf.git'
const projectDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const xsDevCli = resolve(projectDirectory, 'node_modules', 'xs-dev', 'build', 'src', 'cli.js')

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd,
    encoding: 'utf8',
    env: options.env ?? process.env,
    stdio: options.capture ? ['ignore', 'pipe', 'inherit'] : 'inherit',
  })

  if (result.error) {
    throw result.error
  }
  if (result.status !== 0 && !options.allowFailure) {
    throw new Error(`Command failed with exit code ${result.status}: ${command} ${args.join(' ')}`)
  }

  return result
}

function getOption(args, optionName) {
  const assignment = args.find((arg) => arg.startsWith(`${optionName}=`))
  if (assignment) {
    return assignment.slice(optionName.length + 1)
  }

  const optionIndex = args.indexOf(optionName)
  return optionIndex === -1 ? undefined : args[optionIndex + 1]
}

export function getEspIdfPath(platform = osType().toLowerCase(), homeDirectory = homedir()) {
  const installDirectory =
    platform === 'windows_nt' ? resolve(homeDirectory, 'xs-dev') : resolve(homeDirectory, '.local', 'share')

  return resolve(installDirectory, 'esp32', 'esp-idf')
}

export function getXsDevArguments(args) {
  const device = getOption(args, '--device')
  const hasVersionOption = args.some(
    (arg) => arg === '--branch' || arg.startsWith('--branch=') || arg === '--release' || arg.startsWith('--release=')
  )

  if (device !== undefined || hasVersionOption) {
    return ['setup', ...args]
  }

  return ['setup', '--branch', MODDABLE_VERSION, ...args]
}

function isGitRepository(directory) {
  return (
    run('git', ['rev-parse', '--is-inside-work-tree'], {
      cwd: directory,
      capture: true,
      allowFailure: true,
    }).status === 0
  )
}

export function ensureEspIdf(idfPath = getEspIdfPath(), runCommand = run) {
  if (!existsSync(idfPath)) {
    mkdirSync(dirname(idfPath), { recursive: true })
    console.log(`Installing ESP-IDF ${ESP_IDF_VERSION} at ${idfPath}`)
    runCommand('git', [
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

  if (!isGitRepository(idfPath)) {
    throw new Error(`ESP-IDF path exists but is not a Git repository: ${idfPath}`)
  }

  let targetCommit = runCommand('git', ['rev-parse', '--verify', `refs/tags/${ESP_IDF_VERSION}^{commit}`], {
    cwd: idfPath,
    capture: true,
    allowFailure: true,
  })
  if (targetCommit.status !== 0) {
    runCommand('git', ['fetch', '--depth', '1', 'origin', 'tag', ESP_IDF_VERSION], { cwd: idfPath })
    targetCommit = runCommand('git', ['rev-parse', '--verify', `refs/tags/${ESP_IDF_VERSION}^{commit}`], {
      cwd: idfPath,
      capture: true,
    })
  }

  const currentCommit = runCommand('git', ['rev-parse', 'HEAD'], {
    cwd: idfPath,
    capture: true,
  })
  if (currentCommit.stdout.trim() === targetCommit.stdout.trim()) {
    console.log(`Using ESP-IDF ${ESP_IDF_VERSION} at ${idfPath}`)
    runCommand('git', ['submodule', 'sync', '--recursive'], { cwd: idfPath })
    runCommand('git', ['submodule', 'update', '--init', '--recursive', '--depth', '1'], { cwd: idfPath })
    return
  }

  const status = runCommand('git', ['status', '--porcelain'], {
    cwd: idfPath,
    capture: true,
  }).stdout.trim()
  if (status !== '') {
    throw new Error(
      `ESP-IDF has local changes. Commit or remove them before switching to ${ESP_IDF_VERSION}:\n${status}`
    )
  }

  console.log(`Switching ESP-IDF at ${idfPath} to ${ESP_IDF_VERSION}`)
  runCommand('git', ['checkout', '--detach', ESP_IDF_VERSION], {
    cwd: idfPath,
  })
  runCommand('git', ['submodule', 'sync', '--recursive'], { cwd: idfPath })
  runCommand('git', ['submodule', 'update', '--init', '--recursive', '--depth', '1'], { cwd: idfPath })
}

function authorizeLinuxPackageInstallation() {
  if (
    osType().toLowerCase() !== 'linux' ||
    process.getuid?.() === 0 ||
    process.env.STACK_CHAN_SETUP_SKIP_SUDO === '1'
  ) {
    return
  }

  console.log('Administrator privileges are required to install system packages.')
  run('sudo', ['--validate'])
}

export function main(args = process.argv.slice(2)) {
  if (!existsSync(xsDevCli)) {
    throw new Error('xs-dev is not installed. Run `npm install` first.')
  }

  const device = getOption(args, '--device')
  const showsHelp = args.includes('--help') || args.includes('-h')
  if (device === 'esp32' && !showsHelp) {
    ensureEspIdf()
  }

  if (!showsHelp) {
    authorizeLinuxPackageInstallation()
  }

  const childEnvironment = {
    ...process.env,
    ...(osType().toLowerCase() === 'linux' ? { CI: 'true' } : {}),
  }
  run(process.execPath, [xsDevCli, ...getXsDevArguments(args)], {
    cwd: projectDirectory,
    env: childEnvironment,
  })
}

const isMainModule = process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href

if (isMainModule) {
  try {
    main()
  } catch (error) {
    console.error(`Stack-chan setup failed: ${error instanceof Error ? error.message : String(error)}`)
    process.exitCode = 1
  }
}
