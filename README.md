# EcoFlow CanBus Reverse Engineering
This repository is a scratchpad for reverse engineering the canbus protocol of the EcoFlow PowerStream with the intention of being able to enable the use of any battery via a telemetry translation layer.

## Physical Layer

Work in progress

The ports on the PowerStream are difficult to identify while in circuit and without disassembly of the unit. Images i've gathered are from various sources across the internet of others that have disassembled broken units and are the starting points for trying to identify the purpose of each of the data pins.

The connector pins are unnumbered so for the purpose of research i'll be referencing them based on the above image from top left to bottom right.

![alt text](images/PS-Battery-port-tight.png)
| Pin   | Function          |
| ---   | --------          |
| 1     | Wake?             |
| 2     | CAN-H             |
| 3     | ?                 |
| 4     | Short to Pin 1    | 
| 5     | CAN-L             |
| 6     | GND               |



![alt text](images/EF-LFP-Battery-port-tight.png)
EcoFlow LFP Battery Port (Probably Delta Pro too?)
| Data Pin   | Function          |
| ---   | --------          |
| 1     | CAN-H             |
| 2     | CAN-L             |
| 3     | ?                 |
| 4     | ?                 | 
| 5     | ?                 |
| 6     | ?                 |

## CANBUS

The golden message that will make the powerstream show that a battery is connected and enable the battery port to function.

```
(1744711690.641741) can0 10003001#AA0384003C2EAC04
(1744711690.641891) can0 10103001#00000B3C03140101
(1744711690.642046) can0 10103001#032FAD28ACE19D9C
(1744711690.642187) can0 10103001#9EF69FEE98F6E999
(1744711690.642323) can0 10103001#E49C9A9C9D90ACA7
(1744711690.642464) can0 10103001#ACADE1AFADADBDAD
(1744711690.642598) can0 10103001#ACADAEADAEAC64AC
(1744711690.642752) can0 10103001#ACADACC27EACACFD
(1744711690.642887) can0 10103001#FAACACADACAE2224
(1744711690.643020) can0 10103001#A9EDA33666ACACE5
(1744711690.643175) can0 10103001#535353ACADACACAC
(1744711690.643316) can0 10103001#ADACACACADACACAC
(1744711690.643452) can0 10103001#ACACACACACACACAC
(1744711690.643586) can0 10103001#ACACACACACACACAC
(1744711690.643721) can0 10103001#ACACACACACACACAC
(1744711690.643875) can0 10103001#ACACACACACACACAC
(1744711690.644010) can0 10103001#ACACACACB9B9EC30
(1744711690.644145) can0 10103001#ACACD39EAEACD6AE
(1744711690.644291) can0 10203001#ACACC8A9ACC8DE06
```

Further understanding of the canbus message types and structure are best referenced by looking over the code for [wattzup](https://github.com/GridSpace/wattzup)

## Proof of Concept

[ef_poc.py](ef_poc.py)

A proof of concept script has been assembled to demostrate the ability to generate these 3C message types and control various attibute values displayed in the EcoFlow app. This script is sufficient to enable the battery port and allow it to be used with any voltage-compatible battery for both charging and discharging.

Testing was carried out with an EcoFlow BP2000 battery and a EcoFlow LFP Battery Polarity Adapter which allow the battery to be used standalone but also provides access to the CANBUS via RJ45 sockets. Testing of the script cut the battery from the canbus network and directly communicated with the PowerStream.

## Thanks

This project would of been considerably more difficult if it were not for the work done by @stewartoallen on his own project [wattzup](https://github.com/GridSpace/wattzup)