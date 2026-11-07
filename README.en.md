# InkTag nRF52811

[中文](README.md) | English

InkTag nRF52811 is Bluetooth firmware for AESL/Hema e-paper shelf labels. Turn a panel into a desktop calendar, clock, picture frame or information sign. Configure the display, manage pictures and update firmware using the shared InkTag WebUI or Python CLI.

E-paper reflects ambient light and retains its image after a refresh. Battery life depends on capacity, refresh frequency, Bluetooth use and hardware. Full refreshes may flash and take several to tens of seconds; cold conditions can slow them or cause ghosting. Wait for the image to settle before another operation.

[Open WebUI](https://solar2ain.github.io/ink-tag/) · [Get standalone](https://github.com/solar2ain/ink-tag/tree/main/webui-standalone) · [Release files](https://github.com/solar2ain/ink-tag/releases) · [Illustrated manual](https://solar2ain.github.io/ink-tag-manual/)

The test page supports RGB, locate, calendar/clock time shift/set, MCU temperature and supply voltage. Time has no year cutoff within the 32-bit timestamp/timezone representation. See [test guidance](docs/usage.en.md#test-page).

## Main features

| Feature | What you can do |
| --- | --- |
| Calendar and clock | Show dates, lunar dates and time; configure week start, countdown and orientation |
| Device page | Show the Bluetooth name, board and connection QR code; set a device label |
| Panel and pins | Select a matching profile; read, save or restore display pin settings |
| Pictures | Display directly or select saved pictures by name or slot ID |
| Image management | List, download, replace and delete images; save names/types during upload |
| Slideshow | Rotate saved images at an interval, including after Bluetooth disconnects |
| Status LED | Use system scenes and select all, critical or off policy |
| Firmware updates | Install matching App OTA packages through WebUI/CLI under the Recovery signature policy |

## Board and panels

Targets the **EL022HWRL** board, also marked **CAL_VER06**, product model EL022H2. The nRF52811 has 192 KiB internal Flash and 24 KiB RAM. The release target is `nrf52811_aesl`; the native model shown by the device is `nrf52811_asel22`.

| Panel | Controller | Native dimensions and colors | Per slot | Approximate capacity | Verified scope |
| --- | --- | --- | --- | --- | --- |
| Original HEMA 2.13-inch | SSD1619 | RAM 128×250, visible 122×250, black/white/red | 8 KiB | 59 images | Pages, images, orientation and panel-temperature readback |
| Huawei 3.98-inch A0 | JD79665AA | 768×552, black/white/red/yellow | 104 KiB | 4 images | Pages, images, orientation and colors |
| Huawei 3.98-inch A1 | JD79665AA | 768×552, black/white/red/yellow | 104 KiB | 4 images | Images, orientation, colors and slideshow |

External Flash totals 512 KiB, with about **472 KiB** for images. Slots include a full frame, metadata and 4 KiB sector alignment. Transfer compression does not increase storage capacity; use the device's reported free slots. Preserve needed pictures before changing panel geometry, then upload images for the new dimensions.

Match controller, recipe, colors, native dimensions, visible area and wiring together. Size alone does not identify compatibility. Square and near-square canvases use rectangular templates selected by size. Replacement panels require matching wiring and electrical conditions; see [hardware](docs/hardware.en.md) for panels, power and qualification scope.

## Download, build and installation

Get shared clients, matching firmware and programming tools from the [InkTag distribution](https://github.com/solar2ain/ink-tag). Actual [Release attachments](https://github.com/solar2ain/ink-tag/releases) and manifests determine availability. This port does not fork WebUI or CLI.

- Compatible InkTag already installed: use WebUI or CLI App OTA after checking the package's installed-resource requirements.
- Stock device, Recovery upgrade or GUI replacement: follow [complete flashing](firmware/ports/nordic/nrf52811/FLASHING.en.md), using J-Link/SWD, a matching signed Full package and the actual board configuration.
- Source compilation: follow [building](docs/building.en.md) for Linux/WSL, pinned SDK, micro-ecc and Arm GCC. The build entry is `make nrf52811-aesl`.

After SDK/toolchain setup, run `.\build.ps1` on Windows (automatically invokes WSL), or `make full` on Linux/WSL, to build a matching complete flashing package in one command; `python build.py` remains available. No private key is needed by default. Output: `_build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl-v0.2.1.0-self-built-full.zip`. Self-built Full uses a distinct container and needs **programmer tools0.2.1.0 or newer**; existing official signed Full requirements are unchanged. See [one-command building](docs/building.en.md#10-build-a-complete-flashing-package).

Current source versions are **App 0.2.1 / Recovery 1.0.1**. Read the device to determine installed versions. Raw build outputs and official signed installation packages are separate files; renaming an unsigned BIN/HEX does not make an installable official OTA/Full package.

Default `make` allows unsigned App OTA and still verifies any supplied signature; `make -f Makefile.signed` builds signature-required Recovery without private keys; official builds require signatures. WebUI/CLI admission follows the installed Recovery policy, which App OTA cannot change. See [build options and unsigned packaging](docs/building.en.md#9-recovery-ota-signature-policy).

**App OTA does not update Recovery, SoftDevice or GUI/font resources.** This platform's App verifies its paired GUI. GUI changes require a matching complete installation; do not send an incompatible new App alone to an old-resource device. Complete flashing rebuilds ordinary settings and invalidates old image headers. Read the tool's cleanup scope and confirmation prompt first.

## WebUI

1. **Static website:** open [InkTag WebUI](https://solar2ain.github.io/ink-tag/), with no local service installation.
2. **Standalone:** obtain `webui-standalone/InkTag-WebUI.html` from the distribution, keep its adjacent `assets/` and other supplied files, and open it in a Web Bluetooth browser.

Enable system Bluetooth and grant browser access. Initial connection requires selecting and authorizing a device. See the [client guide](https://github.com/solar2ain/ink-tag/blob/main/docs/en/webui.md) for browser and operating-system support.

1. Connect to `IKT_NRF_XXXX` and check board/firmware identity; `_OTA` denotes Recovery.
2. Confirm the fitted panel, colors and orientation, then synchronize time after initial setup or battery replacement.
3. Display the calendar, clock or device page, or clear the screen.
4. Import a picture, adjust cropping/orientation/colors, and display it directly or save it to a slot.
5. Manage images in Resources and set a slideshow interval after saving compatible images.
6. Select a matching OTA package allowed by Recovery signature policy and wait for transfer, reconnect and identity verification.

An optional local WebUI service is available through the distribution instructions; use the address printed by its startup command. Before another client operates the same device, finish its current transfer/refresh and disconnect it from the current client. Other devices' pages and the entire service need not close.

## CLI

Install the shared client using the [CLI guide](https://github.com/solar2ain/ink-tag/blob/main/docs/en/cli.md). `inktag-cli` and `inktag` invoke the same program. Every command level supports `--help`.

Device selection follows the command group. `-n` accepts a unique name substring; use a more specific name or exact `-a` address when multiple devices match. On macOS, use the system identifier returned by scanning. Replace ABCD and example filenames with your device and files.

### Connection, time and pages

```console
inktag-cli device scan
inktag-cli device -n IKT_NRF_ABCD info
inktag-cli device -a AA:BB:CC:DD:EE:FF info
inktag-cli device -n IKT_NRF_ABCD setting screen show
inktag-cli device -n IKT_NRF_ABCD time sync
inktag-cli device -n IKT_NRF_ABCD display calendar
inktag-cli device -n IKT_NRF_ABCD display clock
inktag-cli device -n IKT_NRF_ABCD display device-info
inktag-cli device -n IKT_NRF_ABCD display clear
```

There is no independently powered RTC, so synchronize after power loss or restart. Normal clients wait for the same App to reconnect and verify its identity before synchronizing. To preserve device time explicitly:

```console
inktag-cli device -n IKT_NRF_ABCD --no-time-sync time show --no-time-sync
```

Group-level `--no-time-sync` disables implicit synchronization; explicit `time sync` still writes time. Clearing the display does not delete images.

### Pictures, slots and slideshow

```console
inktag-cli image -n IKT_NRF_ABCD upload photo.png --wire-encoding auto
inktag-cli image -n IKT_NRF_ABCD upload photo.png --slot next --name landscape --wire-encoding auto
inktag-cli device -n IKT_NRF_ABCD slot list
inktag-cli device -n IKT_NRF_ABCD slot show landscape
inktag-cli device -n IKT_NRF_ABCD slot download 0 --output landscape.png
inktag-cli device -n IKT_NRF_ABCD display slideshow start --interval 5m
inktag-cli device -n IKT_NRF_ABCD display slideshow stop
inktag-cli device -n IKT_NRF_ABCD setting device-name set "Desk"
```

Omitting `--slot` displays directly. `--slot next` stores in a free slot; an explicit ID replaces that image. `--store-only` saves without refreshing. Names are limited to 35 UTF-8 bytes and saved with types during upload/replacement. Slot IDs may have gaps; use `slot list` results. The device label does not change its Bluetooth name.

### OTA and Recovery

```console
inktag-cli device ota inspect firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD ota update firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD_OTA --no-time-sync recovery status
inktag-cli device -n IKT_NRF_ABCD_OTA recovery resume-app
```

OTA uses a matching Nordic application `.zip`; raw BIN/HEX and Full ZIP cannot substitute. Recovery and App retain the same device address. `status` reads the software version; `resume-app` returns only to a valid complete App, waits up to the default 90 seconds, then verifies App identity and normally synchronizes time. Recovery does not exit automatically. Operations with unknown outcomes are not replayed automatically. See [usage](docs/usage.en.md).

## Documentation and feedback

- [Usage](docs/usage.en.md): settings, pictures, slideshow, cleanup and Recovery.
- [Hardware](docs/hardware.en.md): boards, panels, capacity, pins and power.
- [Building](docs/building.en.md): dependencies, unsigned compilation and resource pairing.
- [Complete flashing](firmware/ports/nordic/nrf52811/FLASHING.en.md): initial installation, Full and Recovery upgrades.
- [Protocol](protocol/README.md), [changelog](CHANGELOG.md), [contributing](CONTRIBUTING.md) and [security reports](SECURITY.md).

## Community

[QQ group 418446983 (join)](https://qun.qq.com/universal-share/share?ac=1&busi_data=eyJncm91cENvZGUiOiI0MTg0NDY5ODMiLCJ0b2tlbiI6ImRPVW00UnZxcWNKTU41M1JXZTQrRGpDeDRqTzI5UDkrTkdPb2U0Y1JGbE00MlcreFRuNnpkSU9QWkF3d01lTEEifQ%3D%3D&data=vETdxuw2M9SvyY0uJLAPuFrwhYCMPMCkYfiu-HzwB4-vWHpF2Jo9CtUXgTsNHzOrklunriznP8R1fytCHQWXpQ&svctype=4&tempid=h5_group_info). Alternatively, search for **418446983** in QQ and request to join.

## Acknowledgements

Thanks to [EPD-nRF5](https://github.com/tsl0922/EPD-nRF5), Adafruit GFX, u8g2, and the upstream resource/tool authors. See [third-party notices](THIRD_PARTY_NOTICES.md) for sources and terms.

## LICENCE

InkTag-owned code uses [AGPL-3.0-only](LICENSE). Inherited third-party components retain their original licenses.
