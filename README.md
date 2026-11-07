# InkTag nRF52811

中文 | [English](README.en.md)

InkTag nRF52811 是面向 AESL／盒马电子价签的蓝牙固件，可以把电子纸变成桌面日历、时钟、电子相框和信息牌。使用共享的 InkTag WebUI 或 Python CLI，配置屏幕、管理图片和更新固件。

电子纸通过反射环境光显示，刷新后可以保持画面。续航取决于电池容量、刷新频率、蓝牙使用和硬件。全屏刷新可能闪烁并持续数秒至数十秒；低温可能使刷新变慢或产生残影，请等待画面稳定后再操作。

[打开 WebUI](https://solar2ain.github.io/ink-tag/) · [获取 standalone](https://github.com/solar2ain/ink-tag/tree/main/webui-standalone) · [发行文件](https://github.com/solar2ain/ink-tag/releases) · [图文手册](https://solar2ain.github.io/ink-tag-manual/)

测试页支持RGB、定位灯、日历／时钟时间偏移与设置、芯片温度和供电电压读取。时间没有年份门槛，仍需符合32位时间戳与时区表示范围。详见[测试说明](docs/usage.md#测试页面)。

## 主要功能

| 功能 | 使用方式 |
| --- | --- |
| 日历与时钟 | 显示日期、农历和时间，设置每周起始日、倒计时和显示方向 |
| 设备信息 | 显示蓝牙名称、主板型号和连接二维码，设置设备备注 |
| 屏幕与引脚 | 选择匹配屏参，读取、保存或恢复屏幕引脚配置 |
| 图片展示 | 直接传图，或按图片名称、图槽 ID 显示已保存图片 |
| 图片管理 | 查看、下载、替换和删除图片，上传时保存名称与类型 |
| 自动轮播 | 按间隔切换已保存图片，断开蓝牙后继续播放 |
| 状态灯 | 使用系统灯效，选择全部、关键或关闭策略 |
| 固件更新 | 通过 WebUI／CLI 安装匹配的 App OTA 包，签名要求由 Recovery 决定 |

## 主板与屏幕

面向 **EL022HWRL** 主板，备注丝印 **CAL_VER06**，产品型号 EL022H2；主控 nRF52811，192 KiB 内部 Flash、24 KiB RAM。发布目标为 `nrf52811_aesl`；设备信息中的原生型号为 `nrf52811_asel22`。

| 屏幕 | 控制器 | 原生尺寸与颜色 | 单个图槽 | 参考容量 | 已验证范围 |
| --- | --- | --- | --- | --- | --- |
| 原装 HEMA 2.13 英寸 | SSD1619 | RAM 128×250，可视 122×250，黑白红 | 8 KiB | 约 59 张 | 页面、图片、方向与屏温回读 |
| 华为 3.98 英寸 A0 | JD79665AA | 768×552，黑白红黄 | 104 KiB | 约 4 张 | 页面、图片、方向与颜色 |
| 华为 3.98 英寸 A1 | JD79665AA | 768×552，黑白红黄 | 104 KiB | 约 4 张 | 图片、方向、颜色与轮播 |

外置 Flash 共 512 KiB，图片区约 **472 KiB**。单槽包含完整帧、元数据和 4 KiB 扇区对齐空间；传输压缩不增加图片容量，以设备报告的可用槽为准。更换屏幕尺寸前先保存需要保留的图片，再上传匹配新尺寸的图片。

屏幕必须同时匹配控制器、配方、颜色、原生尺寸、可视区域与实际接线，不能只看英寸数。方形及近方形画面使用按尺寸选择的矩形模板。换装屏需确认接线和电气条件；更多屏型、供电及验证范围见[硬件说明](docs/hardware.md)。

## 获取、编译与安装

从 [InkTag 发布库](https://github.com/solar2ain/ink-tag)获取共享客户端、匹配固件和烧录工具，可下载版本以实际 [Release 附件](https://github.com/solar2ain/ink-tag/releases)及清单为准。本库不分叉 WebUI 或 CLI。

- 已安装兼容 InkTag：使用 WebUI 或 CLI 进行 App OTA，先核对包与现装资源的兼容要求。
- 原厂设备、Recovery 升级或 GUI 资源更换：按[完整烧录说明](firmware/ports/nordic/nrf52811/FLASHING.md)，使用 J-Link／SWD、匹配的签名 Full 包及实际主板配置。
- 从源码编译：按[编译说明](docs/building.md)准备 Linux／WSL、固定 SDK、micro-ecc 与 Arm GCC，构建入口为 `make nrf52811-aesl`。

准备好 SDK／工具链后，Windows 运行 `.\build.ps1`（自动使用 WSL），Linux／WSL 运行 `make full`，即可一键编译并生成配套的完整刷机包；`python build.py` 仍可用。默认无需私钥，输出为 `_build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl-v0.2.1.0-self-built-full.zip`。自编 Full 使用独立容器身份，需要 **0.2.1.0 或更新的烧录工具**；现有正式签名 Full 的工具要求不变。详见[一键构建](docs/building.md#10-一键生成完整刷机固件)。

当前源码版本为 **App 0.2.1 / Recovery 1.0.1**。已安装版本以设备读回为准；源码构建输出与正式签名安装包分开。未签名 BIN／HEX 不能通过改名变为可安装的官方 OTA／Full 包。

默认 `make` 允许未签名 App OTA，有签名时仍验证；`make -f Makefile.signed` 无需私钥即可构建强制验签的 Recovery；官方构建保持要求签名。WebUI／CLI 按实际 Recovery 策略准入，App OTA 不会更改已安装的策略。自编打包和构建开关见[编译说明](docs/building.md#9-recovery-的-ota-签名策略)。

**App OTA 不更新 Recovery、SoftDevice 或 GUI／字体资源。** 本平台 App 校验其配对 GUI；GUI 改变时需使用匹配的完整安装包，不能先给旧资源设备单独发送不匹配的新 App。完整烧录会重建普通设置并使旧图片头失效，操作前阅读工具的清理范围和确认提示。

## 使用 WebUI

1. **静态网页**：打开 [InkTag WebUI](https://solar2ain.github.io/ink-tag/)，无需安装本地服务。
2. **standalone**：从发布库获取 `webui-standalone/InkTag-WebUI.html`，保留旁边的 `assets/` 等配套文件，用支持 Web Bluetooth 的浏览器打开。

开启系统蓝牙并允许浏览器访问。首次连接需在设备列表中选择并授权；具体浏览器和系统支持范围见[客户端说明](https://github.com/solar2ain/ink-tag/blob/main/docs/zh-CN/webui.md)。

1. 点击连接，选择 `IKT_NRF_XXXX`，核对主板和固件身份；名称带 `_OTA` 表示 Recovery。
2. 确认实际安装的屏幕、颜色和方向，首次使用或换电池后校时。
3. 选择日历、时钟、设备信息页，或清屏。
4. 导入图片，调整裁剪、方向和颜色，直接显示或保存到图槽。
5. 在资源页管理图片；准备兼容图片后设置轮播间隔。
6. 更新时选择匹配且符合 Recovery 签名策略的 OTA 包，等待传输、重连和验身完成。

也可按发布库文档安装本地 WebUI 服务，使用启动命令显示的地址。同一设备的传输或刷新完成后，再断开当前客户端并切换到另一个客户端；无需关闭其他设备的页面或整个服务。

## 使用 CLI

按发布库的 [CLI 安装说明](https://github.com/solar2ain/ink-tag/blob/main/docs/zh-CN/cli.md)安装共享客户端。`inktag-cli` 和 `inktag` 调用同一程序，各级支持 `--help`。

设备选择参数放在命令组后。`-n` 匹配唯一蓝牙名称片段，多台匹配时使用更完整名称或 `-a` 精确地址；macOS 使用扫描返回的系统标识。示例中的 ABCD 与文件名请替换为自己的设备和文件。

### 连接、校时与页面

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

没有独立持续供电 RTC，掉电／重启后需重新校时；正常客户端重启流程等待同设备重连、验身后校时。需要保持原时间时，显式使用：

```console
inktag-cli device -n IKT_NRF_ABCD --no-time-sync time show --no-time-sync
```

组级 `--no-time-sync` 关闭隐式校时，不会阻止显式 `time sync`。清屏只改变画面，不删除图槽。

### 图片、图槽与轮播

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

不指定 `--slot` 时直接显示；`--slot next` 保存到空闲槽，指定 ID 可替换图片。`--store-only` 只保存、不立即刷新。图片名称最多 35 个 UTF-8 字节，与类型一起在上传或替换时保存；图槽 ID 可以有空位，以 `slot list` 返回值为准。设备备注不改变蓝牙广播名。

### OTA 与 Recovery

```console
inktag-cli device ota inspect firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD ota update firmware-ota.zip
inktag-cli device -n IKT_NRF_ABCD_OTA --no-time-sync recovery status
inktag-cli device -n IKT_NRF_ABCD_OTA recovery resume-app
```

OTA 使用匹配的 Nordic 应用 `.zip`，不能用 raw BIN／HEX 或 Full ZIP 代替。Recovery 与 App 保持同一设备地址；`status` 只读版本，`resume-app` 在 App 完整有效时安全返回，默认等待 90 秒，再确认 App 身份并按正常流程校时。没有自动超时退出；未知操作结果不自动重放。详见[使用指南](docs/usage.md)。

## 文档与反馈

- [使用指南](docs/usage.md)：设置、图片、轮播、数据清理与 Recovery。
- [硬件说明](docs/hardware.md)：主板、屏幕、容量、引脚与供电。
- [编译说明](docs/building.md)：依赖、未签名构建与资源配对。
- [完整烧录](firmware/ports/nordic/nrf52811/FLASHING.md)：首次安装、Full 与 Recovery 升级。
- [协议参考](protocol/README.md)、[更新记录](CHANGELOG.md)、[贡献说明](CONTRIBUTING.md)与[安全报告](SECURITY.md)。

## 交流群

[QQ 交流群：418446983（点击加群）](https://qun.qq.com/universal-share/share?ac=1&busi_data=eyJncm91cENvZGUiOiI0MTg0NDY5ODMiLCJ0b2tlbiI6ImRPVW00UnZxcWNKTU41M1JXZTQrRGpDeDRqTzI5UDkrTkdPb2U0Y1JGbE00MlcreFRuNnpkSU9QWkF3d01lTEEifQ%3D%3D&data=vETdxuw2M9SvyY0uJLAPuFrwhYCMPMCkYfiu-HzwB4-vWHpF2Jo9CtUXgTsNHzOrklunriznP8R1fytCHQWXpQ&svctype=4&tempid=h5_group_info)。也可在 QQ 中搜索群号 **418446983** 申请加入。

## 致谢

感谢 [EPD-nRF5](https://github.com/tsl0922/EPD-nRF5)、Adafruit GFX、u8g2 及各上游资源与工具作者。具体来源及许可见[第三方说明](THIRD_PARTY_NOTICES.md)。

## LICENCE

InkTag 自有代码使用 [AGPL-3.0-only](LICENSE)，继承的第三方组件保留原许可。
