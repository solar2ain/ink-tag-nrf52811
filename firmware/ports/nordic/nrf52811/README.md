# nRF52811 固件

中文 | [English](README.en.md)

面向 EL022H2 电子价签，使用 nRF52811、S112 和外置图片存储。屏幕型号、方向和显示内容通过 InkTag WebUI 或 CLI 配置。

- [项目介绍](../../../../README.md)
- [使用指南](../../../../docs/usage.md)
- [硬件与功能](../../../../docs/hardware.md)
- [构建说明](../../../../docs/building.md)
- [烧录说明](FLASHING.md)

## 构建目标

默认 `make` 或 `make nrf52811-aesl` 生成未签名App、Recovery和GUI资源，不签包、不暂存、不访问硬件；`make nrf52811-aesl-bootloader` 仅生成未签名Recovery。SDK 和工具链路径通过 `SDK_ROOT`、`TOOLCHAIN_PATH` 指定，输出位于 `_build/nordic/nrf52811_aesl/`。

## 设备配置

设备页主板型号为 `nrf52811_asel22`。应用广播名称为 `IKT_NRF_XXXX`，Recovery 使用相同设备地址，名称追加 `_OTA`。用户备注独立于广播名。

屏幕空闲时关闭电源使能，显示时使用 4 MHz 硬件 SPI。计时采用 32.768 kHz 低频晶振。EL029H2 和其他未测屏幕不继承 EL022H2 的实测结论。
