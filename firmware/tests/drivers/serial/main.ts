import Serial from 'embedded:io/serial'
import Timer from 'timer'
import Digital from "pins/digital";

let buffer = new ArrayBuffer(1);
let chars = new Uint8Array(buffer);
let blink =1;
let led = new Digital(17,Digital.Output);

chars[0] = 0x55;


let serial = new Serial(
{
transmit: 7,
receive: 6,
baud: 1000000,
port: 1
}
);


Timer.repeat(id => {
 serial.write(buffer);
 blink = blink ^1;
 led.write(blink);
 trace("send\n\r");
}, 1);

