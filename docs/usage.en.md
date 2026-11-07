# Usage

[中文](usage.md) | English

Install the maintained client from the [distribution repository](https://github.com/solar2ain/ink-tag/blob/main/docs/en/cli.md). Actual device capabilities govern availability.

Selection options follow their command group. `-n` accepts a unique name fragment; `-a` is an exact address or macOS CoreBluetooth identifier. Replace ABCD with your device. Every command level accepts `-h`.

```console
inktag-cli device scan
inktag-cli device -n IKT_NRF_ABCD info
inktag-cli device -a AA:BB:CC:DD:EE:FF --no-time-sync info
inktag-cli device -n IKT_NRF_ABCD time sync
inktag-cli device -n IKT_NRF_ABCD --no-time-sync time show
inktag-cli device -n IKT_NRF_ABCD setting screen show
inktag-cli device setting screen profiles
inktag-cli device -n IKT_NRF_ABCD setting pins show
inktag-cli device -n IKT_NRF_ABCD display calendar
inktag-cli device -n IKT_NRF_ABCD display clock
inktag-cli device -n IKT_NRF_ABCD display device-info
inktag-cli device -n IKT_NRF_ABCD display clear
inktag-cli device -n IKT_NRF_ABCD setting device-name set Desk
inktag-cli device -n IKT_NRF_ABCD led policy critical
```

Normal connections synchronize time; explicit `--no-time-sync` preserves the old time. Without a separately powered persistent RTC, time may be lost across restart/power loss. The maintained restart client waits for the same verified App and then performs normal synchronization unless disabled. No periodic Flash checkpoint is needed for this design limitation.

Disconnect power before replacing a panel. Use WebUI or `setting screen` to choose the actual controller, recipe, colors and dimensions; see [hardware](hardware.en.md). Square geometry uses rectangular templates without adding controller support. `setting pins -h` documents pin configuration;255 means disconnected. Wait for refresh completion before another operation.


## Test page

Use the maintained client's test page and the list returned by the device. Current sources support:

| Test | Scope |
| --- | --- |
| RGB channel / locate | Three color channels and locator start/stop |
| Time shift / set | Calendar or clock; shifts remain nonzero and within ±366 days |
| ADC read | MCU temperature and supply voltage; unavailable samples are marked invalid and the reference channel is explicitly unsupported |

Normal synchronization and time tests impose no year cutoff. Epoch zero renders 1970 rather than an unset-date fallback. UTC and local seconds must fit the existing unsigned 32-bit representation; time zones are within ±14 hours. Tests save time, while page/weekday hints affect the current runtime without rewriting ordinary page preferences. Disable automatic synchronization to retain a test time. Lunar/solar annotations may be unavailable outside their data coverage without making time setting fail. Older clients may still enforce a year cutoff; use an updated maintained client.

After an accepted time test, wait for its matching display completion event. Completion is separate from optical qualification of a new panel. Button simulation, buzzer, expansion GPIO, raw-register and unlisted tests are unsupported.

## Images and slideshow

```console
inktag-cli image -n IKT_NRF_ABCD upload picture.png --slot next --name landscape --wire-encoding auto
inktag-cli device -n IKT_NRF_ABCD slot list
inktag-cli device -n IKT_NRF_ABCD slot show landscape
inktag-cli device -n IKT_NRF_ABCD slot download 0 --output picture-0.png
inktag-cli device -n IKT_NRF_ABCD display slideshow start --interval 5m
inktag-cli device -n IKT_NRF_ABCD display slideshow stop
```

Slots can have gaps. Upload/replacement writes image, name and type together; metadata cannot be edited alone. Re-upload after changing screen geometry. RLE compresses transport, not physical slot allocation. Capacity depends on actual physical storage.

## Cleanup, OTA and Recovery

```console
inktag-cli device -n IKT_NRF_ABCD restart
inktag-cli device -n IKT_NRF_ABCD setting reset-settings
inktag-cli device -n IKT_NRF_ABCD setting clear-user-data
inktag-cli device ota inspect firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD ota update firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD --no-time-sync recovery enter
inktag-cli device -n IKT_NRF_ABCD_OTA --no-time-sync recovery status
inktag-cli device -n IKT_NRF_ABCD_OTA recovery resume-app
```

Restart, settings reset, user-data deletion and screen clearing are different operations; read each scope confirmation. OTA updates App only. Initial installation and Recovery replacement use [Full programming](../firmware/ports/nordic/nrf52811/FLASHING.en.md). Signature, compatibility epoch, layout and integrity checks remain.

A maintained client with `recovery status` reads the true1.0.1 identity. Confirmed old Recovery explicitly reporting unsupported is displayed as1.0.0 with a legacy source marker. Truncation, refusal and timeout fail. The query does not enter/exit Recovery, set PRN, transfer firmware or synchronize time. Existing published clients may predate this command.

`resume-app` and `exit` use a shared90-second return timeout, overridable by valid `--reconnect-wait`. Recovery must admit the unchanged App; no force return or automatic inactivity exit is provided. Do not replay an unknown mutation/exit result. Avoid using WebUI and CLI on the same device simultaneously.
