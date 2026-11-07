# 使用指南

中文 | [English](usage.en.md)

客户端使用 [InkTag发布库](https://github.com/solar2ain/ink-tag)的维护版本，安装见[客户端文档](https://github.com/solar2ain/ink-tag/blob/main/docs/zh-CN/cli.md)。功能以设备实际能力为准。

## 选择设备与校时

设备参数放在命令组后；`-n`是唯一蓝牙名片段，`-a`是精确地址（macOS用扫描结果中的CoreBluetooth标识）。示例ABCD替换为自己的设备。每级命令支持`-h`。

```console
inktag-cli device scan
inktag-cli device -n IKT_NRF_ABCD info
inktag-cli device -a AA:BB:CC:DD:EE:FF --no-time-sync info
inktag-cli device -n IKT_NRF_ABCD time sync
inktag-cli device -n IKT_NRF_ABCD --no-time-sync time show
```

普通连接默认校时；确需保留原时间时显式`--no-time-sync`。无独立持续供电RTC，掉电／重启后时间丢失是当前设计限制。维护客户端重启后等待同设备App重连、验身，再按正常流程校时；使用`--no-time-sync`则不校时。不要为此周期性写Flash。

## 屏幕、页面与设置

```console
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

更换屏幕前断电；通过WebUI或`setting screen`选择实际控制器、配方、颜色及尺寸。见[硬件范围](hardware.md)。方形及近方形使用矩形模板，不能据此宣称新增控制器支持。屏幕／LED引脚配置见`setting pins -h`；255表示未连接。等待刷新完成后再发新操作。


## 测试页面

使用维护客户端的测试页，并以设备返回的测试列表为准。当前源码支持：

| 测试 | 范围 |
| --- | --- |
| RGB 通道／定位灯 | 三色通道，以及定位灯启动／停止 |
| 时间偏移／设置 | 日历或时钟；偏移仍为非零且不超过±366天 |
| ADC 读取 | 芯片温度、供电电压；无有效采样时报告不可用，参考通道明确不支持 |

普通校时和测试时间均不设置年份门槛；0秒表示1970年起点，不会替换为默认日期。UTC 和本地时间必须能用现有32位无符号秒表示，时区为±14小时。测试会保存时间，页面与星期起始提示仅作用于本次运行，不重写普通页面偏好；需要保留测试时间时先关闭客户端自动校时。日期超出农历／节气数据覆盖时，相应信息可能不可用，不代表时间设置失败。旧客户端可能仍限制年份，需配合更新后的维护客户端。

时间测试收到成功响应后还需等待对应的刷新完成事件；收到完成事件不等于新面板已通过光学验证。按键模拟、蜂鸣器、扩展GPIO、裸寄存器及未列出的测试不支持。

## 图片和轮播

```console
inktag-cli image -n IKT_NRF_ABCD upload picture.png --slot next --name landscape --wire-encoding auto
inktag-cli device -n IKT_NRF_ABCD slot list
inktag-cli device -n IKT_NRF_ABCD slot show landscape
inktag-cli device -n IKT_NRF_ABCD slot download 0 --output picture-0.png
inktag-cli device -n IKT_NRF_ABCD display slideshow start --interval 5m
inktag-cli device -n IKT_NRF_ABCD display slideshow stop
```

`--slot next`保存到空闲槽；替换指定槽会更新图片、名称和类型。仅名称／类型不能单独修改。实际槽ID可能有空位；更换屏幕几何后应重新上传对应图片。RLE压缩用于传输，Flash仍按完整图片及元数据分配。可存数量取决于实际存储容量。

## 清理、OTA和Recovery

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

重启、清除设置、清除用户数据和清屏用途不同；查看确认范围再操作。OTA更新App，不更新Recovery或GUI资源。首次安装和Recovery本身更新使用[完整烧录](../firmware/ports/nordic/nrf52811/FLASHING.md)。签名、兼容epoch、布局和完整性检查保持。

新版维护CLI的`recovery status`只读版本：新Recovery1.0.1返回真实版本，明确不支持查询的已确认旧Recovery显示1.0.0并标记来源。超时、短帧和拒绝不当作旧版。此命令不进入／退出Recovery、不传图、不设置PRN或校时。客户端是否包含该命令须以实际版本为准。

`resume-app`与`exit`默认等待同一App返回90秒，显式有效`--reconnect-wait`覆盖默认。退出仍需Recovery确认App有效；没有自动超时退出。未知写入／退出结果不自动重放。WebUI与CLI不要同时占用同一设备。
