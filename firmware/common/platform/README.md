# Platform interface

The platform interface covers GPIO, SPI, delay/time counters, power control, configuration storage and BLE command transport. Nordic-specific adapters are in `firmware/ports/nordic/`.

InkTag BLE uses these UUIDs:

| Interface | UUID |
| --- | --- |
| Service | `62750001-d828-918d-fb46-b6c11c675aec` |
| Command and status | `62750002-d828-918d-fb46-b6c11c675aec` |
| Application version | `62750003-d828-918d-fb46-b6c11c675aec` |

Wall-clock updates derive elapsed time from hardware counters. Timer callbacks provide sampling opportunities; their count does not define elapsed seconds.
