# Security / 安全报告

请勿在公开Issue或讨论中上传签名私钥、凭据、设备完整备份或可直接利用的未修复漏洞细节。启用GitHub私密漏洞报告时优先使用该入口；否则先联系仓库维护者约定私密通道。

报告请提供受影响源码／固件版本、准确主板、复现步骤、预期与实际行为，以及去除敏感信息后的日志。不要为复现擅自操作他人的设备、绕过签名检查或公开真实密钥。

Use GitHub private vulnerability reporting when enabled, or contact the maintainer to arrange a private channel. Include affected versions, board identity, reproduction and redacted logs. Do not post private keys, credentials or complete device backups publicly.

## 已知限制 / Known limitation

SDK 的 micro-ecc 在某些特殊自定义 P-256 公钥下可能误拒绝有效签名，已用公开测试私钥值 `2` 对应的公钥复现。此上游限制尚未修复；固定测试夹具的调整不代表该问题已修复，也不放宽固件验签策略。

The SDK's micro-ecc can reject valid signatures for certain special custom P-256 public keys, reproduced with the public test scalar `2`. This upstream limitation remains unresolved. Changing the fixed test fixture does not fix it or relax firmware signature checks.
