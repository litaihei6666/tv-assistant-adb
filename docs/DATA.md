# 数据格式 v1

`data/entries.json` 根对象含 `schema_version: 1` 和 `entries` 数组。每条数据包含稳定 `id`、`brands`、`title`、明确的 `scope`、已点名 `models`、`evidence`、`status`、带标题和 HTTPS 链接的 `sources`、有序 `steps`、`limitations`、`transport` 与 `reviewed_at`。型号清单是资料中点名的名称，不构成固件级适配授权，也不意味着全部型号逐台实测。

`evidence`: official / community / mixed / firsthand_report / unverified；`status`: reference / user_report / unresolved；`transport`: usb / wireless / unknown。未知路线 `unresolved` 不得包含步骤。不得以自动匹配或人工输入直接判定设备兼容，也不能将这些数据用于任何有风险操作的授权。

静态页面由脚本从 JSON 生成；通过 `python scripts/build.py --check` 检查提交的页面与数据一致。使用者应核验资料版本、范围及自己设备实际菜单。

可选 `context` 对象包含 `system`、`firmware`、`region` 三个非空字符串，记录的是来源中设备的系统、固件及地区，未知填“未知”。它不是程序实际检测结果，也不代表相同固件已在本项目验证。没有该字段的旧条目保持兼容；页面会显示已有信息并允许搜索固件字符串。
