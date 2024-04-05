  
# 脚本说明：  
1、脚本用于使用账号密码自动登录京东获取ck，自动更新ck到青龙  
2、建议本地登录，不建议使用代理，第一次使用手机验证码之后一般不需要验证码就可以密码登录  
3、程序仅更新被禁用的ck  
4、脚本有py源码以及windows版本exe程序  
5、py脚本需要opencv-python、pyppeteer、Pillow、asyncio、aiohttp等依赖  
6、linux需要桌面环境，比如gnome用于图形处理  
7、第一次使用会下载chrome浏览器，生成jdck.ini配置文件，等待即可，后续无需等待  
8、此脚本适合于青龙内部运行，因青龙大部分不支持opencv插件，仅支持linux以及windows运行，建议使用windows版本，定时运行即可。  
9、脚本基于3.12开发，其它版本python自行测试  
10、脚本需要青龙应用权限——环境变量跟脚本管理  

  
# windows使用说明
运行exe即可，无需安装依赖等  
如果windows有python环境，可能会遇到问题  
windows定时任务参考https://blog.csdn.net/renluborenlubo/article/details/128655711  

# linux使用说明(仅x86，其它架构自行测试)  
## 已知问题：一直要短信验证，不建议用  
#### 设置pip源  
```
pip config set global.extra-index-url "http://mirrors.aliyun.com/pypi/simple/ https://pypi.tuna.tsinghua.edu.cn/simple/"
```

#### 安装python依赖
```
pip install --break-system-packages pyppeteer Pillow asyncio aiohttp opencv-python
`````

#### 在无桌面环境下运行 Pyppeteer 时，会出现报错的情况。这是因为无头浏览器 Chrome 需要在有可视化界面的环境下运行。在无桌面环境下，缺少了图形渲染所需的相关库和设备驱动，导致无法正常启动 Chrome。  
！！！！安装完之后要重启系统！！！！  
或者调用桌面相关的服务  
    
#### 安装桌面环境：
Ubuntu/Debian 分支
```
apt install -y  gnome
```
CentOS/Fedora/RedHat 分支
```
yum install -y gnome
```
也可以使用其它桌面环境,自行选择  

### 定时运行  
```
echo "*/30 * * * * python3.11 /root/autojdck.py" | crontab -  #半小时运行一次，python命令改成自己的，py脚本路径也改自己的
```
注意：这种方式会覆盖当前用户的全部定时任务，所以请确保你已经包含了所有需要保留的定时任务。  

### chrome浏览器手动下载地址(非必要)
https://github.com/517939148yjf/svjdck/releases/download/jdck/chrome-linux.zip  
解压到~/.local/share/pyppeteer/local-chromium/1181205/  
确保1181205/chrome-linux/chrome有执行权限之后再运行脚本  


# jdck.ini配置文件位于脚本/程序同目录下
Displaylogin=0  #是否显示登录操作，1显示，0不显示  
qlip=http://192.168.1.1:5700  #填青龙的ip  
client_id=*******    #填青龙对接应用的client_id  
client_secret=*******     #填青龙对接应用的client_secret  

登陆号码#密码#备注          #多账户换行  
例如：  
517123248#ya21udb95#我是备注1  
15611167798#123456789#我是备注2  


### 废案：
```
代理登陆变量  
AutoJDCK_DP = http://192.168.2.1:22332    #设置登录代理（不建议设置代理，基本上要验证码）  
```

# 打赏  
如果你觉得作者很棒，你可以打赏他  
如果你觉得他很菜，你可以扫码支持他  
![给点钱花花](get_me_some_money.jpg)

# 免责声明  
本脚本仅供学习参考，请在下载后24小时内删除，请勿用于非法用途。  
作者不对因使用该脚本造成的任何损失或法律问题负责。  
