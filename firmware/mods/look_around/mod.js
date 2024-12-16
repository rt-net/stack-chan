import Timer from 'timer'
import { randomBetween, asyncWait } from 'stackchan-util'

export function onRobotCreated(robot) {
  let isFollowing = false
  robot.button.a.onChanged = function () {
    if (this.read()) {
      trace('pressed A\n')
      isFollowing = !isFollowing
      const text = isFollowing ? 'looking' : 'stop'
      robot.showBalloon(text)
    }
  }
  robot.button.b.onChanged = function () {
    if (this.read()) {
      trace('pressed B\n')
    }
  }
  let flag = false
  robot.button.c.onChanged = function () {
    if (this.read()) {
      trace('pressed C\n')
      if (flag) {
        robot.setColor('primary', 0xff, 0xff, 0xff)
        robot.setColor('secondary', 0x00, 0x00, 0x00)
      } else {
        robot.setColor('primary', 0x00, 0x00, 0x00)
        robot.setColor('secondary', 0xff, 0xff, 0xff)
      }
      flag = !flag
    }
  }

  const targetLoop = () => {
    if (!isFollowing) {
      robot.lookAway()
      return
    }
    const x = randomBetween(0.4, 1.0)
    const y = randomBetween(-0.4, 0.4)
    const z = randomBetween(-0.02, 0.2)
    trace(`looking at: [${x}, ${y}, ${z}]\n`)
    robot.lookAt([x, y, z])
  }
  Timer.repeat(targetLoop, 5000)
}
