declare const global: any

import config from 'mc/config'
import Modules from 'modules'
import { Robot, Driver, TTS, Renderer } from 'robot'
import { DynamixelDriver } from 'dynamixel-driver'
import { TTS as LocalTTS } from 'tts-local'
import { TTS as RemoteTTS } from 'tts-remote'
import { TTS as VoiceVoxTTS } from 'tts-voicevox'
import { TTS as ElevenLabsTTS } from 'tts-elevenlabs'
import defaultMod, { StackchanMod } from 'default-mods/mod'
import { Renderer as SimpleRenderer } from 'simple-face'
import { NetworkService } from 'network-service'
import Touch from 'touch'
import { loadPreferences, asyncWait } from 'stackchan-util'
import TextDecoder from 'text/decoder'

function createRobot() {
  const decoder = new TextDecoder()
  const ttsEngines = new Map<string, new (param: unknown) => TTS>([
    ['local', LocalTTS],
    ['remote', RemoteTTS],
    ['voicevox', VoiceVoxTTS],
    ['elevenlabs', ElevenLabsTTS],
  ])
  const renderers = new Map<string, new (param: unknown) => Renderer>([['simple', SimpleRenderer]])

  // TODO: select driver/tts/renderer by mod

  const errors: string[] = []

  // Servo Driver
  const driverPrefs = loadPreferences('driver')
  const driverKey = 'dynamixel'
  const Driver = DynamixelDriver

  // TTS
  const ttsPrefs = loadPreferences('tts')
  const ttsKey = ttsPrefs.type ?? 'local'
  const TTS = ttsEngines.get(ttsKey)

  // Renderer
  const rendererPrefs = loadPreferences('renderer')
  const rendererKey = rendererPrefs.type ?? 'simple'
  const Renderer = renderers.get(rendererKey)

  if (!TTS || !Renderer) {
    for (const [key, klass] of [
      [ttsKey, TTS],
      [rendererKey, Renderer],
    ]) {
      if (klass == null) {
        errors.push(`type "${key}" does not exist`)
      }
    }
    throw new Error(errors.join('\n'))
  }

  const driver = new DynamixelDriver(driverPrefs)
  const renderer = new Renderer(rendererPrefs)
  const tts = new TTS(ttsPrefs)
  const button = globalThis.button
  const touch = !global.screen.touch && config.Touch ? new Touch() : undefined
  return new Robot({
    driver,
    renderer,
    tts,
    button,
    touch,
    decoder,
  })
}

async function checkAndConnectWiFi() {
  const wifiPrefs = loadPreferences('wifi')
  if (wifiPrefs.ssid == null || wifiPrefs.password == null) {
    return
  }
  return new Promise((resolve, reject) => {
    globalThis.network = new NetworkService({
      ssid: wifiPrefs.ssid,
      password: wifiPrefs.password,
    })
    globalThis.network.connect(resolve, reject)
  })
}

async function main() {
  await asyncWait(100)
  await checkAndConnectWiFi().catch((msg) => {
    trace(`WiFi connection failed: ${msg}`)
  })
  let { onRobotCreated, onLaunch } = defaultMod
  if (Modules.has('mod')) {
    const mod = Modules.importNow('mod') as StackchanMod
    onRobotCreated = mod.onRobotCreated ?? onRobotCreated
    onLaunch = mod.onLaunch ?? onLaunch
  }
  const shouldRobotCreate = await onLaunch?.()
  if (shouldRobotCreate !== false) {
    const robot = createRobot()
    await onRobotCreated?.(robot, globalThis.device)
  }
}

main()
