### EcoFlow Battery Impersonation Proof-of-Concept
###
### Script to generate 3C CAN bus messages that impersonate a battery
### connected to a PowerStream device.
###
### IMPORTANT: This script is intended for educational purposes only.
### It may pose a real danger to your safety or the functionality of your
### devices. No responsibility is accepted for damage to you or your
### equipment.
###
### The script replicates the 3C message types sent by genuine EcoFlow BP2000
### batteries and updates required bytes for various attributes. It appears
### sufficient to send these messages so that the PowerStream enables the
### battery port for charging and discharging.


import logging
import time
import argparse
import can
import random

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 1_000_000

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("can")

SEND_INTERVAL = 0.5

header = [
    0xaa, 0x03, 0x84, 0x00, 0x3c, 0x2e, 0xac, 0x04,
    0x00, 0x00, 0x0b, 0x3c, 0x03, 0x14, 0x01, 0x01,
    0x03, 0x2f
]

message = [
                0x01, 0x84, 0x00, 0x4d, 0x31, 0x30, 
    0x32, 0x5a, 0x33, 0x42, 0x34, 0x5a, 0x45, 0x35,
    0x48, 0x30, 0x36, 0x30, 0x31, 0x3c, 0x00, 0x0b,
    0x00, 0x01, 0x4d, 0x03, 0x01, 0x01, 0x11, 0x01,
    0x00, 0x01, 0x02, 0x01, 0x02, 0x00, 0xc8, 0x00,
    0x00, 0x01, 0x00, 0x6e, 0xd2, 0x00, 0x00, 0x51,
    0x56, 0x00, 0x00, 0x01, 0x00, 0x02, 0x8e, 0x88,
    0x05, 0x41, 0x0f, 0x9a, 0xca, 0x00, 0x00, 0x49,
    0xff, 0xff, 0xff, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x15, 0x15, 0x40, 0x9c,
    0x00, 0x00, 0x7f, 0x32, 0x02, 0x00, 0x7a, 0x02,
    0x00, 0x00, 0x64, 0x05, 0x00, 0x64
]

def crc16(data: bytes) -> int:
    CRC16 = [
         0, 49345, 49537,   320, 49921,   960,   640, 49729,
    50689,  1728,  1920, 51009, 1280, 50625, 50305,  1088,
    52225,  3264,  3456, 52545, 3840, 53185, 52865,  3648,
    2560, 51905, 52097,  2880, 51457,  2496,  2176, 51265,
    55297,  6336,  6528, 55617, 6912, 56257, 55937,  6720,
     7680, 57025, 57217,  8000, 56577,  7616,  7296, 56385,
     5120, 54465, 54657,  5440, 55041,  6080,  5760, 54849,
    53761,  4800,  4992, 54081, 4352, 53697, 53377,  4160,
    61441, 12480, 12672, 61761, 13056, 62401, 62081, 12864,
    13824, 63169, 63361, 14144, 62721, 13760, 13440, 62529,
    15360, 64705, 64897, 15680, 65281, 16320, 16000, 65089,
    64001, 15040, 15232, 64321, 14592, 63937, 63617, 14400,
    10240, 59585, 59777, 10560, 60161, 11200, 10880, 59969,
    60929, 11968, 12160, 61249, 11520, 60865, 60545, 11328,
    58369,  9408,  9600, 58689,  9984, 59329, 59009,  9792,
     8704, 58049, 58241,  9024, 57601,  8640,  8320, 57409,
    40961, 24768, 24960, 41281, 25344, 41921, 41601, 25152,
    26112, 42689, 42881, 26432, 42241, 26048, 25728, 42049,
    27648, 44225, 44417, 27968, 44801, 28608, 28288, 44609,
    43521, 27328, 27520, 43841, 26880, 43457, 43137, 26688,
    30720, 47297, 47489, 31040, 47873, 31680, 31360, 47681,
    48641, 32448, 32640, 48961, 32000, 48577, 48257, 31808,
    46081, 29888, 30080, 46401, 30464, 47041, 46721, 30272,
    29184, 45761, 45953, 29504, 45313, 29120, 28800, 45121,
    20480, 37057, 37249, 20800, 37633, 21440, 21120, 37441,
    38401, 22208, 22400, 38721, 21760, 38337, 38017, 21568,
    39937, 23744, 23936, 40257, 24320, 40897, 40577, 24128,
    23040, 39617, 39809, 23360, 39169, 22976, 22656, 38977,
    34817, 18624, 18816, 35137, 19200, 35777, 35457, 19008,
    19968, 36545, 36737, 20288, 36097, 19904, 19584, 35905,
    17408, 33985, 34177, 17728, 34561, 18368, 18048, 34369,
    33281, 17088, 17280, 33601, 16640, 33217, 32897, 16448
    ]
    crc = 0
    for b in data:
        crc = CRC16[(crc ^ b) & 0xff] ^ (crc >> 8)
    return crc


def send_data(bus: can.Bus, args: argparse) -> None:
    ## Add input args to the payload
    message[56] = args.soc
    message[57:59] = args.volt.to_bytes(2)
    message[114] = args.temp                                       #TODO: Doesn't work
    message[115] = args.temp                                       #TODO: Doesn't work
    message[3:19] = list(args.serial.encode('ascii'))
    message[124:128] = args.runtime.to_bytes(4, byteorder='little')
    
    ## Get random XOR key, add to header and encode payload
    header[6] = random.randint(0,255)
    encoded_payload = bytes([b ^ header[6] for b in message])
    msg = bytes(header) + encoded_payload
    
    ## Calc CRC16 and append
    crc = crc16(msg).to_bytes(2, byteorder='little')
    msg = msg + crc
    
    ## Prepare the messages and send
    data = can.Message()
    msg_len = round(len(msg)/8)
    for n in range(msg_len):
        idx = n * 8
        if n == 0:
            data = can.Message(arbitration_id=0x10003001, data=msg[idx:idx + 8])
        elif n < msg_len - 1:
            data =can.Message(arbitration_id=0x10103001, data=msg[idx:idx + 8])
        elif n == msg_len - 1:
            data = can.Message(arbitration_id=0x10203001, data=msg[idx:idx + 8])
        
        bus.send(data)

    
def main(args):
    with can.Bus() as bus:
        while True:
            send_data(bus, args)
            time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='ef_poc.py [options]',
                    description='Imposonation of an EcoFlow BP2000 Battery CANBUS message for presentation to a PowerStream'
                    )
    
    parser.add_argument('--soc', default=50, help='State of charge value %% (Default: 50)', type=int)
    parser.add_argument('--temp', default=20, help='Battery Temp (Default: 20)', type=int)
    parser.add_argument('--volt', default=51866, help='Battery Voltage (Default: 51866)', type=int)
    parser.add_argument('--serial', default='M102Z3B4ZE5H0000', help='Device serial to impersonate (Default: M102Z3B4ZE5H0000)', type=lambda s: s if len(s) == 16 else (_ for _ in ()).throw(argparse.ArgumentTypeError()))
    parser.add_argument('--runtime', default=60, help='Battery Runtime Remaining (Default: 60)', type=int)
    
    args = parser.parse_args()
    
    try:
        main(args)
    except KeyboardInterrupt:
        pass