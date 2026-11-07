# 更新记录 / Changelog

## App 0.2.1 / Recovery 1.0.1

### 中文

- SSD1683 全刷最长释放等待延长至 65,535 ms，调试日志不再额外触发边沿检测刷新前的温度／OTP 装载。

- 修复 Recovery 下载蓝灯在数据对象完成时重置闪烁节拍的问题；保留断线续传与安装、错误灯效。

- 新增 Windows `build.ps1` 入口，复用现有完整构建流程，支持 SDK／工具链路径与 optional／required 配置。

- 新增日历／时钟时间偏移与设置测试，以及芯片温度／供电电压读取测试；时间不再受2024年门槛限制，保留编码与时区安全检查。

- 新增 `python build.py` 一键生成配套完整刷机包；默认无需私钥。自编 Full 具有独立身份，使用工具0.2.1.0；官方签名发布流程保持独立。

- 原生 App 版本为 0.2.1，Recovery 为 1.0.1；保留兼容 epoch1 和 N1V1/layout-v1。
- 维护中的 CLI 可通过 `device recovery status` 读取 Recovery 软件版本。
- 日历与时钟顶部布局保持一致；方形及近方形尺寸使用按尺寸选择的矩形模板。
- 板级定义按固件家族集中维护，烧录预设使用 EL022HWRL 主板丝印；构建入口统一为 `make nrf52811-aesl`。
- 默认 Make 生成未签名 App、Recovery 和 GUI 资源；正式签包单独提供。
- 开源 Recovery 默认允许未签名 App OTA，提供独立的 `Makefile.signed` 强制验签入口和隔离的缓存／输出；带签名的包始终验签。新增无需私钥的 OTA 打包脚本，客户端按实际 Recovery 策略准入。
- 编译、烧录、使用和本更新记录提供中英文说明。

原生版本、发布标签和源码快照是不同标识。设备安装版本和可下载签包，以实际读回及发布附件为准。App 与 GUI 资源需保持配对。

### English

- Extended the SSD1683 full-refresh release wait to 65,535 ms and prevented debug logging from adding a temperature/OTP load before edge-qualified refreshes.

- Fixed Recovery download LED phase resets at data-object boundaries; retained resume, installation and error indications.

- Added a Windows `build.ps1` entry using the existing complete build flow, with SDK/toolchain paths and optional/required profiles.

- Added calendar/clock time shift/set and MCU-temperature/supply-voltage tests; removed the 2024 year cutoff while retaining representation and timezone checks.

- Added `python build.py` for a matching complete flashing package without private keys by default. Self-built Full uses a distinct identity and tools0.2.1.0; official signed production stays separate.

- Native App version is 0.2.1 and Recovery is 1.0.1; compatibility epoch1 and N1V1/layout-v1 are retained.
- A maintained CLI can read the Recovery software version with `device recovery status`.
- Calendar and clock headers use consistent geometry; square and near-square sizes use rectangular templates selected by size.
- Board definitions are concentrated by firmware family, flashing presets use the EL022HWRL PCB marking, and the build entry is `make nrf52811-aesl`.
- Default Make builds unsigned App, Recovery and GUI resources; official signed packages are supplied separately.
- Open-source Recovery allows unsigned App OTA by default and provides a separate `Makefile.signed` required-signature entry with isolated caches/output; supplied signatures are always verified. A key-free OTA packager is provided, with client admission based on the actual Recovery policy.
- Build, flashing, usage guides and this changelog include Chinese and English text.

Native versions, release tags and source snapshots are separate identifiers. Installed versions and available signed packages are determined by actual device readback and release attachments. Keep App and GUI resources paired.
