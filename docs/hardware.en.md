# Hardware and features

[中文](hardware.md) | English

InkTag nRF52811 provides the basic functions for an e-paper calendar, clock and image display. Panel selection and orientation are configured and saved using the shared WebUI or CLI.

Square and near-square sizes, including152×152,200×200 and240×240, use rectangular templates selected by size. Controller, recipe, color and capacity must match the actual panel.

## Board

| Item | Description |
| --- | --- |
| Tested board | EL022HWRL; device-page model `nrf52811_asel22` |
| MCU | nRF52811, 192 KiB Flash and 24 KiB RAM |
| Image storage | 512 KiB external Flash, with approximately 472 KiB for images |
| Clock | 32.768 kHz low-frequency crystal |
| Panel interface | Hardware SPI at 4 MHz; panel power enable is switched off when idle |
| Status light | RGB LED |
| Bluetooth name | Application `IKT_NRF_XXXX`; Recovery `IKT_NRF_XXXX_OTA` |

EL029H2 has not completed independent hardware validation. Similar appearance does not establish the same test results as EL022HWRL.

## Tested panels

| Panel | Colors and dimensions | Verified scope |
| --- | --- | --- |
| Original 2.13-inch HEMA | Black/white/red, 128×250 with 122×250 visible | Pages, images, orientation and panel-temperature readback |
| Huawei 3.98-inch A0 | Black/white/red/yellow, 768×552 | Pages, images, orientation and colors |
| Huawei 3.98-inch A1 | Black/white/red/yellow, 768×552 | Images, orientation, colors and slideshow |

Panel-temperature availability depends on the controller's readback support. A0/A1 temperature adaptation still needs physical testing. Other selectable profiles do not imply validation on this board. SES 2.13/2.66 panels are excluded from this firmware.

## Approximate capacity and refresh time

| Panel configuration | Size per slot | Approximate image capacity | Estimated full refresh | Status |
| --- | --- | --- | --- | --- |
| Original 2.13-inch HEMA BWR | 8 KiB | About 59 images | About 15–30 seconds | Display tested; timing based on comparable panels |
| 4.2-inch BWR (400×300) | 32 KiB | About 14 images | About 15 seconds | Candidate; timing based on comparable panels |
| 4.2-inch BWRY (400×300) | 32 KiB | About 14 images | About 21 seconds | Candidate; timing based on comparable panels |
| Huawei A0/A1 BWRY | 104 KiB | About 4 images | About 16 seconds | Tested |

The 400×300 candidates still need display testing on this board. Match the specific controller and panel model when selecting a profile. Refresh times exclude Bluetooth connection, page drawing and image transfer, and vary with the panel, waveform and temperature. Reference specifications: [2.13-inch BWR](https://www.waveshare.com/2.13inch-e-Paper-HAT-B.htm), [400×300 BWR](https://www.waveshare.com/4.2inch-e-Paper-Module-B.htm) and [400×300 BWRY](https://www.waveshare.com/4.2inch-e-paper-module-g.htm).

## Images and settings

Image names allow up to 35 UTF-8 bytes. Set the name and type when uploading or replacing an image. Slot IDs remain stable and may contain gaps after deletion; the device reports the actual capacity.

The slot size includes the image, metadata such as its name, and alignment space. RLE compresses transfer data; storage slots are allocated for the complete image size.

Replacement writes directly to the selected slot. A power interruption can lose the previous image in that slot. Changing panel geometry or image-storage span invalidates old slots; upload images matching the new panel.

Panel type, orientation, time, time zone, device label and LED policy can be saved. The label does not change the Bluetooth advertising name. Panel temperature is sampled during a normal refresh and cached for 15 minutes. Queries do not wake the panel; missing valid data is shown as unavailable.
