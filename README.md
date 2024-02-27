第一次使用会下载chrome浏览器，生成jdck.ini配置文件，等待即可，后续无需等待
py脚本需要opencv-python、pyppeteer、Pillow、asyncio、aiohttp等依赖
版本：2024.2.27

注：此脚本不适合于青龙内部运行，因青龙大部分不支持opencv插件，仅支持linux以及windows运行，
建议使用windows版本，定时运行即可。

脚本说明：
1、脚本用于使用账号密码自动登录京东获取ck，自动更新ck到青龙
2、建议本地登录不使用代理，第一次使用手机验证码之后一般不需要验证码就可以密码登录
3、程序仅更新被禁用的ck
4、脚本有py源码以及windows版本exe程序


添加青龙变量
jdckpasswd = pt_pin+登录名+密码+备注      #多账户换行
例如：
jd_4fbbedd6a4d87#517****48#ya******595#备注
jd_ZVCWCTvxVxqo#15611167798#123456789#备注

AutoJDCK_DP = http://192.168.2.3:2233      #设置登录代理（不建议设置代理，要短信登录）

jdck.ini配置文件
Displaylogin=0  #是否显示登录操作，1显示，0不显示
qlip=http://192.168.1.1:5700  #填青龙的ip
client_id=*******    #填青龙对接应用的client_id
client_secret=*******     #填青龙对接应用的client_secret

免责声明
本脚本仅供学习参考，请在下载后24小时内删除，请勿用于非法用途。
作者不对因使用该脚本造成的任何损失或法律问题负责。
