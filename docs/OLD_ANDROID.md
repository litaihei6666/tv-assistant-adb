# Android 4.4等旧版设备：先核对入口和连接方式

Android 4.4本身并非“没有ADB”。Android官方文档覆盖Android 4.2及以上的开发者选项和USB调试，但厂商定制电视是否保留菜单、提供可用USB设备端接口或开放网络调试，仍须按型号与固件确认。[Android官方ADB说明](https://developer.android.com/tools/adb#Enabling)

## 在自己的电视上怎么判断

1. 在普通“关于”页面或铭牌确认完整型号，分别记下Android版本和电视固件。不要把电视软件号当成Android版本。
2. 先查本库对应型号，再核对实际菜单。平台通用的版本号七次点击只是参考；找不到时保持未知，不进入工厂或维修菜单。[开发者选项官方说明](https://developer.android.com/studio/debug/dev-options#enable)
3. 分清USB调试和网络调试。官方对Android 10及以下的通用网络连接流程需要先建立USB连接；部分厂商另有网络开关，其适用性必须另有证据，不能假定开启USB后就有网络入口。[旧版连接前提](https://developer.android.com/tools/adb#wireless-android10)
4. 开启提示不等于电脑已连接。应核对实际连接状态、本人授权和读到的设备身份；只知道IP、端口可达或页面写“已开启”都不够。
5. 找不到安全入口时停在待确认；本库不要求用root、刷机、恢复出厂或修改系统文件补救。结束后在电视端关闭不必要的调试，电脑断开不代表电视开关已关。

这不构成对所有Android 4.4电视的兼容承诺，也不证明新Launcher、HOME接管或精简命令能够在旧固件使用。本轮尚未获得Android 4.4具体机型与固件的充分普通入口证据；已有资料见[覆盖情况](COVERAGE.md)。
