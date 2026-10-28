# 资料覆盖情况

2026-10-28 更新。只统计已落地数据；型号、设备代号、零售名称和系统版本并不一一对应。

## 已整理记录

- 共 **76 条**：**58 条有条件参考**、**1 条一次用户反馈**、**17 条入口待确认**。相对36条基线新增40条。
- 点名 **61 个型号或设备标识**，包含板卡、模块、系统自报名称；不等于61个零售型号或逐台验证。
- 已整理记录出现49个品牌名称/别名/系列标签，中英文别名不能当作独立品牌相加。
- 只有TCL 65V6D有本项目会话中的一次用户反馈，且固件未知；本轮没有新增本项目真机测试。

## 机型资料来源索引

另有 **260 条来源目录记录、77 个原始品牌或系列标签**。全部是待逐条审查的元数据，不含操作步骤，不计为可用教程。两部分有重叠，不能把76和260相加宣传为支持机型数量。

固定来源：[CleanYourTV机型目录 ab7a89e7](https://github.com/Gathin23/cleanyourtv/blob/ab7a89e7/examples/README.md)。品牌标签原样保留，不合并子品牌、Fire TV或地区名称；型号详情见[索引数据](../data/research-index.json)和[查询页](../index.html)。已有ADB使用记录不保证写明首次开启入口。

| 来源品牌/系列标签 | 机型目录记录数 |
| --- | ---: |
| TCL | 57 |
| Sony | 32 |
| Xiaomi | 29 |
| Philips | 14 |
| Hisense | 10 |
| Skyworth | 9 |
| Amazon Fire TV | 7 |
| Thomson | 4 |
| BenQ | 3 |
| Google | 3 |
| Haier | 3 |
| OnePlus | 3 |
| Panasonic | 3 |
| XGIMI | 3 |
| Anker Nebula | 2 |
| BYINTEK | 2 |
| CHiQ | 2 |
| FFalcon | 2 |
| Formovie | 2 |
| Hitachi | 2 |
| Kalley | 2 |
| Motorola | 2 |
| Nokia | 2 |
| NVIDIA Shield | 2 |
| onn | 2 |
| RCA | 2 |
| Redmi | 2 |
| Sankey | 2 |
| SHARP | 2 |
| Toshiba | 2 |
| Vu | 2 |
| Acer | 1 |
| AiPro2K | 1 |
| AIWA | 1 |
| Artel | 1 |
| Caxium | 1 |
| Cecotec | 1 |
| Challenger | 1 |
| Compac | 1 |
| Dialog | 1 |
| EKO | 1 |
| Epson | 1 |
| Freebox | 1 |
| Gadnic | 1 |
| Grundig | 1 |
| HOTACK | 1 |
| INCLO | 1 |
| Insignia Fire TV | 1 |
| JMGO | 1 |
| JVC | 1 |
| Karbonn | 1 |
| Kogan | 1 |
| KTC | 1 |
| Liberton | 1 |
| Lumio | 1 |
| Magcubic | 1 |
| Master-G | 1 |
| MTC | 1 |
| Noblex | 1 |
| OK. | 1 |
| PEAQ | 1 |
| Polytron | 1 |
| Portronics | 1 |
| PRISM+ | 1 |
| RockTek | 1 |
| SANYO | 1 |
| Sber | 1 |
| Stellamore | 1 |
| Super General | 1 |
| Tele System | 1 |
| TiVo | 1 |
| Tornado | 1 |
| Turkcell | 1 |
| Verizon | 1 |
| Vidda | 1 |
| Vision | 1 |
| Wanbo | 1 |

## 本轮具体补充

- 明基E55-735/E55-750/GV32、Google两款Chromecast和GZRNL、海信65D62QH/HG9/75A53FUA/U9DG、两款SHIELD、两款onn.、松下4KTV-0SU、飞利浦四款、Redmi MiTV-MFTP0。
- 海尔H32S80EFX/HR9216EU/DVB2K、CHiQ GTVU65、坚果N1S/K80A、一加C00、夏普2T-C32GH3000I、东芝Cosmos170、万播X5 Pro、Anker D2426、爱普生LS800/HA90。
- 国内原始来源：天猫魔盒M13普通远程调试路径；当贝F3反馈冲突；极米Z7X的GMUI 6.11入口限制；小明Q2的额外软件依赖；乐视Q85/CV560-C75特殊菜单限制；大眼橙极光UI未明确型号的辅助APK线索。VIDAA助手普通授权与系统能力分开说明。
- 峰米MiProjM05、KTC台湾版和海尔DVB2K有资料但入口不足，保持待确认。常见中文品牌与英文检索词相通，别名不构成机型或固件授权。

## 仍需优先补充

1. 国内定制固件：TCL/雷鸟、海信/Vidda、创维/酷开、小米/Redmi、长虹、康佳、海尔、乐视、华为/荣耀；不能用海外Android TV菜单替代国内入口。
2. Android 4.4等旧机和运营商盒子：需要可核实的普通入口，不按品牌或Android版本猜测。
3. 当贝、极米、小明、大眼橙等缺普通入口的型号：查找可维护的合法方案；额外APK需独立审查，不直接导入。
4. 按上述优先级逐条审查260条来源；仅使用ADB却没说明开启方式的资料不转成教程，矛盾保留原报告差异。
5. 可公开且脱敏的真实反馈、地区与固件差异、获许可的图解。未获图片授权时不复制第三方截图。

已发布到[GitHub仓库](https://github.com/litaihei6666/tv-assistant-adb)；下载ZIP完整解压后可使用本地查询页和JSON资料。公开托管不代表资料已通过真机验证。
