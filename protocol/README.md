# nRF52811 protocol reference

当前应用协议字节为`0x10`，App版本0.2.1；Recovery独立软件版本1.0.1，兼容epoch1、物理布局N1V1/layout-v1。客户端应读取实际设备信息和能力，不通过文件名推断版本。

## App

| 项目 | 定义 |
| --- | --- |
| BLE service | `62750001-d828-918d-fb46-b6c11c675aec` |
| 命令／状态 characteristic | `62750002-d828-918d-fb46-b6c11c675aec` |
| 版本 characteristic | `62750003-d828-918d-fb46-b6c11c675aec` |
| 版本值 | `protocolByte,major,minor,patch` |
| 请求头 | `opcode,transactionId,versionTaggedFlags`，后接payload |
| 当前flags版本标签 | `(flags & 0xFC) == 0x10`，低2位为语义标志 |

命令与状态ID以[编译使用的协议头](../firmware/common/epd/inktag_protocol_v2.h)为准；固定格式长度见[格式常量](../firmware/common/protocol/inktag_release_v1.h)。屏幕记录为17 B，引脚块为16 B。GPIO和屏幕的实际可编辑范围由设备返回，不凭主板名称猜测。已分配ID不得重新分配为不同含义。

## Recovery

Recovery使用Nordic Secure DFU服务`0000fe59-0000-1000-8000-00805f9b34fb`。它与App协议属于不同服务，不能混用opcode。

只读固件版本请求为`0B 00`：标准FW_VERSION、image0。正常响应`60 0B 01`后为13 B：`type:u8,version:u32le,address:u32le,length:u32le`。type2为Bootloader；版本按`major<<16 | minor<<8 | patch`编码。该目标地址为`0x2A000`、分区长度为`0x4000`，长度不是原生BIN文件大小。

Recovery版本声明见[版本头](../firmware/common/ota/inktag_recovery_version.h)。Nordic settings里的`bootloader_version`在本实现用于待升级App状态，不能当作Recovery语义版本。维护CLI的用法见[使用指南](../docs/usage.md)。

## Source of truth

The compiled headers linked above define current IDs and record lengths. App protocol and Nordic Secure DFU are separate services. Read actual identity, version and capabilities before selecting an operation. This source build uses the checked-in headers directly; no JSON registry is needed during compilation.
