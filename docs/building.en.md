# Building from source

[中文](building.md) | English

This guide prepares the environment and generates the nRF52811 application, Recovery and `font-assets` GUI resources. The instructions use an **Intel/AMD 64-bit computer with Ubuntu 24.04 or Windows WSL2**. Flashing prebuilt firmware and GUI resources on Windows does not require WSL; see [flashing](../firmware/ports/nordic/nrf52811/FLASHING.en.md).

## 1. Prepare Linux

Linux users can open an Ubuntu terminal and continue with step 2. On Windows, open PowerShell from the Start menu, choose “Run as administrator”, and run:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart when prompted, open Ubuntu, and create a Linux username and password. For subsequent sessions, open Ubuntu from the Start menu or run this in PowerShell:

```powershell
wsl -d Ubuntu-24.04
```

Run the remaining `bash` commands in the **Ubuntu terminal**. For installation help, see [Microsoft's WSL guide](https://learn.microsoft.com/en-us/windows/wsl/install).

## 2. Install basic tools and obtain the source

```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-venv python3-cryptography curl unzip xz-utils ca-certificates
```

Windows users can keep the source on drive C for access by Windows flashing tools:

```bash
mkdir -p /mnt/c/Projects
cd /mnt/c/Projects
```

Linux users can use their own project directory, for example:

```bash
mkdir -p ~/Projects
cd ~/Projects
```

Clone the source and enter its directory. If you already have a checkout, enter its root instead:

```bash
git clone https://github.com/solar2ain/ink-tag-nrf52811.git
cd ink-tag-nrf52811
```

Run all subsequent commands from this root, which contains `Makefile`, `firmware` and `tools`. Keep source, SDK and toolchain paths free of spaces.

## 3. Install the Arm toolchain

Use **Arm GNU Toolchain 15.2.Rel1**, containing **GCC 15.2.1**. Download the Linux x86_64 `arm-none-eabi` package and extract it into the project's `.tools` directory:

```bash
mkdir -p .tools/arm-gnu-toolchain
curl -fL https://developer.arm.com/-/media/Files/downloads/gnu/15.2.rel1/binrel/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz -o .tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz
tar -xf .tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi.tar.xz -C .tools/arm-gnu-toolchain
.tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-gcc --version
```

The last command should report `15.2.1`. If the download fails, obtain the same file from the [official Arm downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads), then extract it and check its version. WSL also uses the Linux toolchain package.

## 4. Install the Nordic SDK and micro-ecc

Use **nRF5 SDK 17.1.0_ddde560**. This SDK ships with S112 7.2.0; this project requires a separate installation of **S112 7.3.0**.

```bash
mkdir -p .sdk/downloads .sdk/nordic
curl -fL https://files.nordicsemi.com/artifactory/nRF5-SDK/external/nRF5_SDK_v17.x.x/nRF5_SDK_17.1.0_ddde560.zip -o .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip
printf '%s\n' '5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061  .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip' | sha256sum -c -
unzip -q .sdk/downloads/nRF5_SDK_17.1.0_ddde560.zip -d .sdk/nordic
```

Proceed with extraction after the checksum reports `OK`. If this SDK version is already installed, skip downloading and extracting it and use step 5 to check its inputs.

Next, install S112 7.3.0:

1. Open [Nordic's S112 downloads](https://www.nordicsemi.com/Products/Development-software/S112/Download), select **7.3.0**, and download and extract the ZIP.
2. Locate `s112_nrf52_7.3.0_softdevice.hex` inside it.
3. Copy this file to `.sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/hex/` in your source checkout, preserving its filename.
4. Locate the matching header directory in the ZIP, containing files such as `ble.h` and `nrf_sdm.h`. Copy its contents and subdirectories to `.sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/headers/`, replacing files with the same names and preserving the directory structure.

For the drive-C example above, the destination in Windows is `C:\Projects\ink-tag-nrf52811\.sdk\nordic\nRF5_SDK_17.1.0_ddde560\components\softdevice\s112\hex\`. This step only prepares files and does not program a device.

The SDK also needs [micro-ecc](https://github.com/kmackay/micro-ecc) for signature verification. Use this fixed revision and line-ending setting to match the project's dependency checks:

```bash
git clone --config core.autocrlf=true --no-checkout https://github.com/kmackay/micro-ecc.git .sdk/nordic/nRF5_SDK_17.1.0_ddde560/external/micro-ecc/micro-ecc
git -C .sdk/nordic/nRF5_SDK_17.1.0_ddde560/external/micro-ecc/micro-ecc checkout --detach 541b3a78026420a3e369c4c9281c396b5e531113
```

If micro-ecc is already present, run the checks in step 5 first. A successful check means no reinstall is needed. Do not replace existing dependencies with the latest revision.

## 5. Check the environment

```bash
python3 --version
make --version
python3 tools/sdk/check-nordic-inputs.py --sdk-root .sdk/nordic/nRF5_SDK_17.1.0_ddde560
ls .sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/hex/s112_nrf52_7.3.0_softdevice.hex
grep -E '^#define SD_(MAJOR|MINOR|BUGFIX)_VERSION' .sdk/nordic/nRF5_SDK_17.1.0_ddde560/components/softdevice/s112/headers/nrf_sdm.h
```

The SDK check should print `Nordic validation / SHA-256 / micro-ecc inputs match locked hashes`. Resolve missing files or hash mismatches by checking the SDK path, version and micro-ecc installation before compiling.

The final command should show version numbers `7`, `3` and `0`. If it still reports `7`, `2` and `0`, update the S112 headers: return to step 4 and prepare both the HEX and matching headers.

## 6. Unsigned builds

Default public Make builds unsigned App, Recovery and GUI assets. No signing key, nrfutil, shared CLI, WebUI, private source checkout, candidate staging or hardware access is required. Use absolute SDK/compiler paths when stored elsewhere.

```bash
make -j4 SDK_ROOT="$PWD/.sdk/nordic/nRF5_SDK_17.1.0_ddde560" TOOLCHAIN_PATH="$PWD/.tools/arm-gnu-toolchain/arm-gnu-toolchain-15.2.rel1-x86_64-arm-none-eabi/bin"
```

`make nrf52811-aesl` builds both roles; `make nrf52811-aesl-bootloader` builds Recovery only. The corresponding `-unsigned` aliases also remain unsigned. Keep `.cache/` for incremental compilation. Default outputs are under `_build/nordic/nrf52811_aesl/optional/`; the required entry uses `required/`:

| Output | Meaning |
| --- | --- |
| `InkTag-nrf52811_aesl.bin` / `.hex` | Unsigned App |
| `bootloader/InkTag-nrf52811_aesl-bootloader.bin` / `.hex` | Recovery |
| `InkTag-nrf52811_aesl-font-assets.bin` | Automatically generated12,288-byte GUI/font/calendar resource |

See [solar-term resource generation](../tools/calendar/README.md) for pinned inputs and regeneration. Ordinary builds use the checked-in resource.

Fixed limits are69,632 bytes App and16,384 bytes Recovery. Overflow fails; partitions do not expand. Current verified source produces App 0.2.1 at 68,996 bytes and Recovery1.0.1 at16,372 bytes. These are offline sizes, not peak-stack, signing or installation qualification. `version.json` owns versions; Recovery identity is separate from the Nordic pending-App settings field. Epoch1 and N1V1/layout-v1 remain unchanged.

## 7. Offline checks

```bash
python3 tools/sdk/check-nordic-inputs.py --sdk-root "$PWD/.sdk/nordic/nRF5_SDK_17.1.0_ddde560"
```

The source directory supplies the `source-export.json` input manifest. Validate it directly:

```bash
python3 tools/source/validate-free.py --sdk-root /absolute/nRF5_SDK_17.1.0_ddde560 --toolchain-path /absolute/arm-gnu-toolchain/bin
```

A native host C compiler is required. Validation builds both roles, runs supplied tests and captures inputs/artifacts. Use a fresh clone or extraction instead of overwriting an existing `.validation/` directory.

## 8. Build outputs versus installation

Raw BIN/HEX outputs are not Full/OTA containers. Section10 builds explicitly identified self-built Full for tools0.2.1.0; ordinary release Full still requires signatures. Maintained programmers require explicit firmware and enforce its container signature policy together with identity, actual capacity, integrity, pairing and readback checks. Recovery1.0.1 installation requires an eligible Full package containing that version; check actual release attachments.

For released firmware installation, follow [flashing](../firmware/ports/nordic/nrf52811/FLASHING.en.md). Download tools and Full firmware separately; no SDK/compiler/WSL is needed. GUI assets are generated with the App and must match the Full pair; App OTA leaves them unchanged. See [license scope](../NOTICE.md) and [third-party notices](../THIRD_PARTY_NOTICES.md) for applicable terms.

| Problem | Action |
| --- | --- |
| Missing Make/host compiler | Install `build-essential` |
| Missing Arm GCC | Use Linux x86_64 Arm GNU15.2.Rel1 and correct `TOOLCHAIN_PATH` |
| Missing/changed pinned Nordic input | Check SDK, exact micro-ecc commit and CRLF bytes; do not skip hashes |
| S112 headers still7.2.0 | Install both7.3.0 HEX and matching headers |
| Programmer refuses a self-built file | Generate self-built Full with section10 and use tools0.2.1.0; raw BIN/HEX cannot become a container by renaming |

## 9. Recovery OTA signature policy

Open-source builds default to `INKTAG_NRF_REQUIRE_SIGNED_DFU=0`: unsigned App OTA packages are allowed, but any supplied signature is still verified with the Recovery public key. A bad signature cannot fall back to unsigned. micro-ecc and signature verification remain build dependencies. To require a valid signature on every OTA package, build explicitly:

```bash
make -f Makefile.signed -j4
```

`Makefile.signed` compiles signature-required Recovery without signing an App or using a private key. It rejects conflicting command-line/environment policy values. Official private production always explicitly selects `1` and asserts the effective Recovery compiler policy before signing. Optional, required and official builds use separate `optional/`, `required/` and `official-required/` cache/output subdirectories, including when custom build/output roots are supplied. Changing the option rebuilds Recovery without changing App/GUI, partitions or versions. **App OTA and WebUI/CLI updates cannot change the policy of an installed Recovery**; replacing Recovery requires a separate complete installation.

With unsigned-permitting Recovery already installed and matching GUI resources, package a self-built App as a standard Nordic OTA ZIP without a private key:

```bash
python3 tools/ota/package-nrf52811.py --app _build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl.bin --output _build/nordic/nrf52811_aesl/optional/my-app-ota.zip
```

Alternatively, `make nrf52811-aesl-ota` builds and packages it. The packager refuses to overwrite existing output. The package contains App only; it never replaces Recovery, SoftDevice or GUI. Compatible WebUI/CLI clients query the actual Recovery policy and admit unsigned packages only for an explicit unsigned-permitting response. Legacy, unknown and failed queries require signatures. Unsigned integrity checks do not authenticate the publisher; install only code from sources you trust. Target, size, SHA256/CRC, voltage, epoch anti-rollback and Bank0 confirmation checks remain. The official signed Full programmer admission rules are unchanged. See the exact [OTA policy and package fields](../protocol/nrf52811-ota-policy.json).

## 10. Build a complete flashing package

Prepare the documented SDK, S1127.3.0, micro-ecc and Arm GNU15.2.1, then run from the source root:

```powershell
.\build.ps1
```

The Windows PowerShell entry invokes WSL automatically; `python build.py` remains available. On Linux/WSL use `make full` or `python3 build.py`. The script builds the current App, Recovery and GUI, merges the pinned MBR/S112 and initializes both SDK17 Bank0/CRC settings pages. It never connects to a device, reads private keys, signs or selects an official candidate.

The default optional profile permits unsigned App packages and still verifies every supplied signature. Outputs:

- `_build/nordic/nrf52811_aesl/optional/InkTag-nrf52811_aesl-v0.2.1.0-self-built-full.zip`: pass to the complete programmer.
- The adjacent `-self-built-full.hex`: MCU image. The Full ZIP also contains matching external GUI assets; the HEX alone is not a complete installation.
- The adjacent `-self-built-ota.zip`: App only, for matching GUI resources and Recovery explicitly permitting unsigned OTA.

Override dependency paths in the same command (Windows paths on Windows, Linux paths on Linux):

```console
python build.py --sdk-root /absolute/nRF5_SDK_17.1.0_ddde560 --toolchain-path /absolute/arm-gnu-toolchain/bin
```

PowerShell accepts `-SdkRoot`, `-ToolchainPath` and `-Jobs`; use `-BuildRoot`/`-OutputRoot` for cache/output directories inside the source checkout, and `-Help` for help. It can be invoked from another working directory; relative paths are interpreted from the source root.

Alternatively set `SDK_ROOT`/`TOOLCHAIN_PATH`, or `sdkRoot`/`toolchainPath` in ignored local `.local/build-full-config.json`. That file is optional. The script never searches other source repositories, downloads SDKs or creates directory links. Failed builds retain previous Full outputs; logs are in `.local/full-builds/`.

A required-signature Full needs an already signed OTA whose App bytes and version exactly match the current build:

```console
python build.py --profile required --signed-ota /path/to/matching-signed-ota.zip
```

The PowerShell equivalent is `.\build.ps1 -OtaSignaturePolicy required -SignedApp C:/Firmware/matching-signed-ota.zip`; `-Profile`/`-SignedOta` aliases also work. The Make equivalent is `make -f Makefile.signed full SIGNED_OTA=/path/to/matching-signed-ota.zip`. Missing or mismatched signatures fail; no downgrade or private-key invocation occurs. Optional/required caches and outputs stay separate.

Self-built Full has a distinct `container_kind` and needs **programmer tools0.2.1.0** or newer; older tools reject it. It is not an official release. Full `publisherVerified` is always false, with App signature status reported separately. Official production retains its private required-signature pipeline. Existing ordinary signed Full retains its identity and verification rules.

Use the maintained programmer with explicit `-Firmware`; run `-DryRun` before following [flashing](../firmware/ports/nordic/nrf52811/FLASHING.en.md). Identity, actual capacity, layout, App/GUI pairing, integrity, voltage and independent readback checks remain. Complete installation rebuilds ordinary settings and invalidates old pictures. A successful build/inspection is not hardware or optical qualification.
