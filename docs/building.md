# 源码构建

中文 | [English](building.en.md)

本指南说明如何准备编译环境，生成 nRF52811 应用、Recovery 和 `font-assets` GUI 资源。以下按 **Intel/AMD 64 位电脑、Ubuntu 24.04 或 Windows WSL2** 编写。Windows 直接烧录已编译的固件和 GUI 资源无需 WSL，见[烧录说明](../firmware/ports/nordic/nrf52811/FLASHING.md)。

## 1. 准备 Linux 环境

Linux 用户打开 Ubuntu 终端，继续第 2 步。Windows 用户在开始菜单中找到 PowerShell，选择“以管理员身份运行”，执行：

```powershell
wsl --install -d Ubuntu-24.04
```

按提示重启电脑，打开 Ubuntu，创建 Linux 用户名和密码。以后可以从开始菜单打开 Ubuntu，也可以在 PowerShell 中执行：

```powershell
wsl -d Ubuntu-24.04
```

接下来的 `bash` 命令都在 **Ubuntu 终端**中运行。安装问题见 [Microsoft WSL 安装说明](https://learn.microsoft.com/en-us/windows/wsl/install)。

## 2. 安装基础工具并获取源码

```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-venv python3-cryptography curl unzip xz-utils ca-certificates
```

Windows 用户可以将源码放在 C 盘，便于之后使用 Windows 烧录工具：

```bash
mkdir -p /mnt/c/Projects
cd /mnt/c/Projects
```

Linux 用户可以使用自己的项目目录，例如：

```bash
mkdir -p ~/Projects
cd ~/Projects
```

下载源码并进入项目目录；已有源码时，直接进入它的根目录即可：

```bash
git clone https://github.com/solar2ain/ink-tag-nrf52811.git
cd ink-tag-nrf52811
```

以下命令均从这个根目录执行。目录内应能看到 `Makefile`、`firmware` 和 `tools`。源码、SDK 和工具链路径不要包含空格。

## 3. 安装 Arm 编译工具链

使用 **Arm GNU Toolchain 15.2.Rel1**，其中 GCC 版本为 **15.2.1**。下载 Linux x86_64 的 `arm-none-eabi` 版本，解压到项目的 `.tools` 目录：

```bash
mkdir -p .tools/arm-gnu-toolchain
curl -fL https://developer.arm.com/-/media/Files/downloads/gnu/15.2.rel1/binrel/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz -o .tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz
tar -xf .tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz -C .tools/arm-gnu-toolchain
.tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-gcc --version
```

最后一条命令应显示 `15.2.1`。下载失败时，可从 [Arm 官方下载页](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)获取同名文件，再执行解压和版本检查。Windows WSL 中也使用 Linux 版本的工具链。

## 4. 安装 Nordic SDK 和 micro-ecc

本项目使用 **nRF5 SDK 17.1.0_ddde560**。该 SDK 自带 S112 7.2.0，本项目需要另外安装 **S112 7.3.0**。

```bash
mkdir -p .sdk/downloads .sdk/nordic
curl -fL https://files.nordicsemi.com/artifactory/nRF5-SDK/external/nRF5_SDK_v17.x.x/nRF5_SDK_17.1.0_ddde560.zip -o .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip
printf '%s\n' '5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061  .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip' | sha256sum -c -
unzip -q .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip -d .sdk/nordic
```

校验应显示 `OK` 后再解压。如果已经安装同版本 SDK，可以跳过下载、解压，使用第 5 步的检查确认依赖。

接着安装 S112 7.3.0：

1. 打开 [Nordic S112 下载页](https://www.nordicsemi.com/Products/Development-software/S112/Download)，选择 **7.3.0**，下载并解压 ZIP。
2. 找到其中的 `s112_nrf52_7.3.0_softdevice.hex`。
3. 将该文件复制到源码目录的 `.sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/hex/`，保留原文件名。
4. 找到 ZIP 中配套的头文件目录（包含 `ble.h`、`nrf_sdm.h` 等），将其内容及子目录复制到 `.sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/headers/`，覆盖同名文件，保留目录结构。

按前面的 C 盘示例，该目标目录在 Windows 中是 `C:\Projects\ink-tag-nrf52811\.sdk\nordic\nRF5_SDK_17.1.0_ddde560\components\softdevice\s112\hex\`。这一步只准备文件，不会向设备写入固件。

SDK 还需要补充 [micro-ecc](https://github.com/kmackay/micro-ecc)，用于签名验证。使用以下固定版本和换行设置，以匹配项目依赖校验：

```bash
git clone --config core.autocrlf=true --no-checkout https://github.com/kmackay/micro-ecc.git .sdk/nordic/nRF5_SDK_17.1.0_ddde560/external/micro-ecc/micro-ecc
git -C .sdk/nordic/nRF5_SDK_17.1.0_ddde560/external/micro-ecc/micro-ecc checkout --detach 541b3a78026420a3e369c4c9281c396b5e531113
```

如果该目录已有 micro-ecc，先执行第 5 步校验；通过后无需重复安装。不要直接用最新版本替换已有依赖。

## 5. 检查环境

```bash
python3 --version
make --version
python3 tools/sdk/check-nordic-inputs.py --sdk-root .sdk/nordic/nRF5_SDK_17.1.0_ddde560
ls .sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/hex/s112_nrf52_7.3.0_softdevice.hex
grep -E '^#define SD_(MAJOR|MINOR|BUGFIX)_VERSION' .sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/headers/nrf_sdm.h
```

SDK 检查应显示 `Nordic validation / SHA-256 / micro-ecc inputs match locked hashes`。看到缺少文件或哈希不匹配时，先修正 SDK 路径、版本或 micro-ecc 安装，确认检查通过后再编译。

最后一条命令显示的版本号应依次为 `7`、`3`、`0`。如果仍显示 `7`、`2`、`0`，说明 S112 头文件尚未更新，回到第 4 步同时准备 HEX 和头文件。

## 6. 编译未签名固件

公开源码入口默认只生成未签名 App、Recovery 和 GUI 资源。无需生产私钥、nrfutil、共享 CLI、本地 WebUI 或其他私有源码库；不会签包、暂存候选或连接设备。SDK／工具链置于其他目录时传入绝对路径。

```bash
make -j4 SDK_ROOT="$PWD/.sdk/nordic/nRF5_SDK_17.1.0_ddde560" TOOLCHAIN_PATH="$PWD/.tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi/bin"
```

`make nrf52811-aesl` 同样构建 App 和 Recovery；`make nrf52811-aesl-bootloader` 仅构建 Recovery。带 `-unsigned` 的相应入口保持未签名语义。保留 `.cache/` 以便增量编译；默认输出在 `_build/nordic/nrf52811_aesl/optional/`；强制签名入口使用 `required/`。

| 文件 | 用途 |
| --- | --- |
| `InkTag-nrf52811_aesl.bin` / `.hex` | 未签名 App |
| `bootloader/InkTag-nrf52811_aesl-bootloader.bin` / `.hex` | Recovery |
| `InkTag-nrf52811_aesl-font-assets.bin` | 自动生成的12,288 B GUI／字体／日历资源 |

节气数据的固定来源和重新生成方法见[节气资源生成](../tools/calendar/README.md)。普通编译使用仓库内的生成资源。

App 与 Recovery 的固定限额分别为69,632 B和16,384 B；超限即失败，不扩大分区。当前已验证源码的 App0.2.1 为68,996 B、Recovery1.0.1 为16,372 B。此数字不是运行栈峰值，也不是新签名或安装资格。版本从 `version.json` 生成；Recovery版本独立于Nordic settings的待升级App标记。epoch1、N1V1/layout-v1保持；不兼容镜像不能靠改显示版本来放行。

## 7. 离线验证

下面的 SDK 检查不会连接硬件：

```bash
python3 tools/sdk/check-nordic-inputs.py --sdk-root "$PWD/.sdk/nordic/nRF5_SDK_17.1.0_ddde560"
```

源码目录带有 `source-export.json` 输入清单，可直接验证本目录：

```bash
python3 tools/source/validate-free.py --sdk-root /absolute/nRF5_SDK_17.1.0_ddde560 --toolchain-path /absolute/arm-gnu-toolchain/bin
```

验证需要宿主C编译器，会构建App／Recovery、运行所附测试并固定输入／产物。请在全新克隆或解压目录运行；已有 `.validation/` 的目录不会覆盖。

## 8. 自编输出与设备安装

原始 BIN／HEX 不等于 Full／OTA 容器。第10节的一键脚本可生成明确标记的自编 Full，使用工具0.2.1.0；普通发行 Full 继续要求签名。维护工具始终要求显式固件输入，并按其容器策略执行签名、身份、实际容量、配对和回读检查。安装Recovery1.0.1需要包含该版本的合格Full包；实际可下载版本以发布附件为准。用户只需安装已发布固件时，按[烧录说明](../firmware/ports/nordic/nrf52811/FLASHING.md)获取独立工具和对应Full包，无需SDK、编译器或WSL。

GUI资源由App构建生成，首次完整安装应与App／Recovery配对；App OTA不改写GUI资源。许可及第三方条款见[许可范围](../NOTICE.md)和[第三方声明](../THIRD_PARTY_NOTICES.md)。

## 常见问题

| 提示 | 处理 |
| --- | --- |
| 缺少Make或宿主C编译器 | 安装 `build-essential` |
| 缺少Arm GCC | 使用Linux x86_64 Arm GNU15.2.Rel1，并检查 `TOOLCHAIN_PATH` |
| `Missing/Changed pinned Nordic input` | 检查SDK、micro-ecc固定提交及CRLF换行；不跳过哈希检查 |
| S112仍为7.2.0 | 同时准备7.3.0的HEX和配套头文件 |
| 自编文件被烧录器拒绝 | 用第10节脚本生成 self-built Full，并配套工具0.2.1.0；原始 BIN／HEX 不能改名冒充容器 |

## 9. Recovery 的 OTA 签名策略

开源构建默认 `INKTAG_NRF_REQUIRE_SIGNED_DFU=0`：允许未签名的 App OTA 包；包中带签名时仍使用 Recovery 内的公钥验证，坏签名不能降级通过。micro-ecc 和验签代码因此仍是构建依赖。要求每个 OTA 包都有有效签名时，显式构建：

```bash
make -f Makefile.signed -j4
```

`Makefile.signed` 只编译要求验签的 Recovery，不替 App 签名，也不需要私钥；冲突的命令行／环境策略值会直接报错。官方私有生产入口固定使用 `1`，并在签发前断言 Recovery 实际编译参数。optional、required 与官方构建分别使用 `optional/`、`required/`、`official-required/` 缓存和输出子目录；自定义构建／输出根目录时仍保持隔离。切换该选项会重新编译 Recovery，不改变 App／GUI、分区或版本。**已安装的 Recovery 策略不会随 App OTA 或 WebUI／CLI 升级而改变**；替换 Recovery 需要单独完整安装。

已安装允许无签名的 Recovery、且 GUI 与 App 匹配时，可将自编 App 打成无需私钥的标准 Nordic OTA ZIP：

```bash
python3 tools/ota/package-nrf52811.py --app _build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl.bin --output _build/nordic/nrf52811_aesl/optional/my-app-ota.zip
```

也可用 `make nrf52811-aesl-ota` 编译并打包；输出文件已存在时打包器拒绝覆盖。包只有 App，不更新 Recovery、SoftDevice 或 GUI。兼容的 WebUI／CLI 会查询实际 Recovery 策略；只有明确返回允许无签名时才接收未签名包，旧版、未知策略或查询失败按要求签名处理。未签名只提供完整性校验，不证明发布者身份；只安装自己信任来源的代码。型号、大小、SHA256／CRC、电压、epoch 防回退和 Bank0 确认检查仍保留。正式签名 Full 工具的准入规则保持不变。精确协议和包字段见 [OTA 策略](../protocol/nrf52811-ota-policy.json)。

## 10. 一键生成完整刷机固件

先按前文准备 SDK、S1127.3.0、micro-ecc 和 Arm GNU15.2.1。在源码根目录执行：

```powershell
.\build.ps1
```

Windows PowerShell 入口自动转到 WSL；`python build.py` 仍可用。Linux／WSL 执行 `make full` 或 `python3 build.py`。脚本编译当前源码的 App、Recovery 和 GUI，合并固定的 MBR／S112，并初始化两份 SDK17 Bank0／CRC 状态页；不连接设备、不读取私钥、不签发、不选择官方候选。

默认是 optional 配置：没有签名的 App 可用，已有签名始终验证。输出：

- `_build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl-v0.2.1.0-self-built-full.zip`：交给完整烧录工具。
- 同目录的 `-self-built-full.hex`：对应 MCU 合并镜像；配套外置 GUI 已包含在 Full ZIP 中，单独 HEX 不能替代完整安装。
- 同目录的 `-self-built-ota.zip`：仅 App，供匹配 GUI 且明确允许未签名的 Recovery 使用。

SDK／工具链不在默认位置时，可在同一条命令中指定（Windows 使用 Windows 路径，Linux 使用 Linux 路径）：

```console
python build.py --sdk-root /absolute/nRF5_SDK_17.1.0_ddde560 --toolchain-path /absolute/arm-gnu-toolchain/bin
```

PowerShell 对应参数为 `-SdkRoot`、`-ToolchainPath`、`-Jobs`；`-BuildRoot`／`-OutputRoot` 可指定源码目录内的缓存／输出目录，`-Help` 查看帮助。脚本可从其他工作目录调用，相对路径按源码根目录解释。

也可通过 `SDK_ROOT`／`TOOLCHAIN_PATH`，或本地忽略文件 `.local/build-full-config.json` 的 `sdkRoot`／`toolchainPath` 配置路径；没有这个本地文件也能构建。脚本不会自动寻找其他源码库、下载 SDK 或建立目录链接。构建失败时保留之前的 Full 输出，日志在 `.local/full-builds/`。

强制验签的完整包需要已经签好的、与本次构建 App 字节及版本完全相同的 OTA 输入：

```console
python build.py --profile required --signed-ota /path/to/matching-signed-ota.zip
```

PowerShell 对应入口为 `.\build.ps1 -OtaSignaturePolicy required -SignedApp C:/Firmware/matching-signed-ota.zip`；也接受 `-Profile`／`-SignedOta` 别名。对应 Make 入口为 `make -f Makefile.signed full SIGNED_OTA=/path/to/matching-signed-ota.zip`。没有匹配签名就失败，不会自动降级或调用私钥。缓存／输出仍按 optional、required 隔离。

自编 Full 具有独立的 `container_kind`，最低烧录工具为 **0.2.1.0**；旧工具会拒绝它。它不等于官方发布物，完整包的 `publisherVerified` 始终为 false；其中 App 的签名状态单独报告。官方发布仍使用私有的 required 签发流程。现有普通签名 Full 保持原身份和校验规则。

烧录仍使用维护的工具和显式 `-Firmware`，先做 `-DryRun`，再按[烧录说明](../firmware/ports/nordic/nrf52811/FLASHING.md)操作。工具保留身份、实际容量、布局、App／GUI 配对、完整性、电压及回读检查；完整安装会重建普通设置并使旧图片失效。单独构建、验包成功不代表已做硬件或光学验证。
