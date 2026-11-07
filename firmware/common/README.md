# Shared firmware components

Reusable InkTag components include:

- `gui/`: drawing, fonts, calendar and lunar data.
- `epd/`: panel definitions, controller operations and display commands.
- `protocol/`: command formats, capabilities and validation.
- `storage/`: records and image storage.
- `lifecycle/`: reset and data-clear operations.
- `input/`, `ble/`, `power/`, `status/`, `security/`, `time/` and `ota/`: product services.

This repository selects the nRF52811 feature set at build time. Source availability does not imply every optional feature or panel is enabled; see the [hardware guide](../../docs/hardware.en.md).
