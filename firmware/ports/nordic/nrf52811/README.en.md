# nRF52811 firmware

[中文](README.md) | English

Firmware for EL022H2 electronic shelf labels, using nRF52811, S112 and external image storage. Configure the panel, orientation and display content through the InkTag WebUI or CLI.

- [Project overview](../../../../README.en.md)
- [Usage](../../../../docs/usage.en.md)
- [Hardware and features](../../../../docs/hardware.en.md)
- [Building](../../../../docs/building.en.md)
- [Flashing](FLASHING.en.md)

## Build targets

Default `make` or `make nrf52811-aesl` builds unsigned App, Recovery and GUI assets without signing, staging or hardware access; `make nrf52811-aesl-bootloader` builds unsigned Recovery only. Specify dependency paths with `SDK_ROOT` and `TOOLCHAIN_PATH`. Artifacts are written to `_build/nordic/nrf52811_aesl/`.

## Device configuration

The device page identifies the board as `nrf52811_asel22`. The application advertises as `IKT_NRF_XXXX`; Recovery uses the same device address and appends `_OTA` to the name. The user label is independent of the advertising name.

Panel power enable is off while idle. Display transfers use hardware SPI at 4 MHz. Timekeeping uses a 32.768 kHz low-frequency crystal. EL029H2 and other untested panels do not inherit EL022H2 test results.
