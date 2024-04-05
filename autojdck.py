# -*- coding: utf-8 -*-
'''

项目地址：https://github.com/dsmggm/svjdck/

脚本说明：
1、脚本用于使用账号密码自动登录京东获取ck，自动更新ck到青龙
2、建议本地登录，不建议使用代理，第一次使用手机验证码之后一般不需要验证码就可以密码登录
3、程序仅更新被禁用的ck
4、脚本有py源码以及windows版本exe程序
5、py脚本需要opencv-python、pyppeteer、Pillow、asyncio、aiohttp等依赖
6、linux需要桌面环境，比如gnome用于图形处理
7、第一次使用会下载chrome浏览器，生成jdck.ini配置文件，等待即可，后续无需等待
8、此脚本适合于青龙内部运行，因青龙大部分不支持opencv插件，仅支持linux以及windows运行，建议使用windows版本，定时运行即可。
9、脚本基于python3.12.1编写，目前3.11可以正常使用，其它版本未测试
10、脚本需要青龙应用权限——环境变量跟脚本管理

jdck.ini配置文件
Displaylogin=0  #是否显示登录操作，1显示，0不显示
qlip=http://192.168.1.1:5700  #填青龙的ip
client_id=*******    #填青龙对接应用的client_id
client_secret=*******     #填青龙对接应用的client_secret

登陆号码#密码#备注      #多账户换行
517123248#ya21udb95#我是备注1
15611167798#123456789#我是备注2

废案：AutoJDCK_DP = http://192.168.2.3:2233      #设置登录代理（不建议设置代理，基本上要验证码）


免责声明
本脚本仅供学习参考，请在下载后24小时内删除，请勿用于非法用途。
作者不对因使用该脚本造成的任何损失或法律问题负责。

'''
import asyncio  # 异步I/O操作库
import random  #用于模拟延迟输入
from re import T  # 随机数生成库
import cv2  # OpenCV库，用于图像处理
import os  #读取配置文件
from pyppeteer import launch  # pyppeteer库，用于自动化控制浏览器
import aiohttp   #用于请求青龙
from urllib import request  # 用于网络请求，这里主要用来下载图片
from PIL import Image  #用于图像处理
import platform  #判断系统类型
import zipfile  #用于解压文件
from datetime import datetime #获取时间




async def print_message(message):     #初始化异步print
    print(message)

async def ifconfigfile():                           #判断有没有配置文件
    global configfile            #配置文件全局变量
    configfile = 'jdck.ini'     #配置文件名称为
    if not os.path.exists(configfile):     #看看有没有配置文件
        configdata = [
'Displaylogin=0  #是否显示登录操作，1显示，0不显示\n',
'qlip=http://192.168.1.1:5700\n',
'client_id=*******\n',
'client_secret=*******\n',
'517123248#ya21udb95#我是备注1\n',
'15611167798#123456789#我是备注2\n',
]
        with open(configfile, 'w', encoding='utf-8') as file:     #打开配置文件
            file.writelines(configdata)       #写入configdata的内容到配置文件
            print('已在当前脚本目录下生成了配置文件，请修改后再运行')
            await asyncio.sleep(10)  # 等待10秒，等待
            raise SystemExit


async def download_file(url, file_path):        #初始化浏览器下载
    timeout = aiohttp.ClientTimeout(total=60000)  # 设置超时时间
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            with open(file_path, 'wb') as file:
                file_size = int(response.headers.get('Content-Length', 0))
                downloaded_size = 0
                chunk_size = 1024
                while True:
                    chunk = await response.content.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    progress = (downloaded_size / file_size) * 100
                    print(f'已下载{progress:.2f}%...', end='\r')
    print('下载完成，进行解压安装....')

async def init_web_display():                           #初始化浏览器显示配置
    global WebDisplay                             #设置为全局变量
    WebDisplay = True                             #默认不显示登录
    try:
        with open(configfile, 'r', encoding='utf-8') as file:
            for line in file:
                if 'Displaylogin=1' in line:                             #如果配置文件有Displaylogin=1这个东西
                    WebDisplay = False                             #就变更成显示登录操作
                    print('当前模式：显示web登录图形化界面')
                    break
        if WebDisplay:
            print("当前配置不显示web登录图形化界面，若要取消静默登陆，在配置文件中设置参数Displaylogin=1")
    except FileNotFoundError:
        print("读取配置文件时出错")

async def init_chrome():        #判断chrome是否存在，不存在则下载，仅针对windows
    if platform.system() == 'Windows':
        chrome_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'pyppeteer', 'pyppeteer', 'local-chromium', '588429', 'chrome-win32')
        chrome_exe = os.path.join(chrome_dir, 'chrome.exe')
        chmod_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'pyppeteer', 'pyppeteer', 'local-chromium', '588429', 'chrome-win32', 'chrome-win32')
        if os.path.exists(chrome_exe):
            return
        else:
            print('貌似第一次使用，未找到chrome，正在下载chrome浏览器....')

            chromeurl = 'http://npm.taobao.org/mirrors/chromium-browser-snapshots/Win_x64/588429/chrome-win32.zip'        #定义下载地址
            target_file = 'chrome-win.zip'                                                          #定义下载文件名
            await download_file(chromeurl, target_file)           #下载
            with zipfile.ZipFile(target_file, 'r') as zip_ref:
                zip_ref.extractall(chrome_dir)
            os.remove(target_file)
            for item in os.listdir(chmod_dir):              #移动所有文件
                source_item = os.path.join(chmod_dir, item)
                destination_item = os.path.join(chrome_dir, item)
                os.rename(source_item, destination_item)
            print('解压安装完成')
            await asyncio.sleep(1)  # 等待1秒，等待
    elif platform.system() == 'Linux':
        chrome_path = os.path.expanduser("~/.local/share/pyppeteer/local-chromium/1181205/chrome-linux/chrome")
        download_path = os.path.expanduser("~/.local/share/pyppeteer/local-chromium/1181205/")
        if os.path.isfile(chrome_path):
            pass
        else:
            print('貌似第一次使用，未找到chrome，正在下载chrome浏览器....')
            print('文件位于github，请耐心等待，如遇到网络问题可到项目地址手动下载')
            download_url = "https://github.com/dsmggm/svjdck/releases/download/jdck/chrome-linux.zip"
            if not os.path.exists(download_path):       #如果没有路径就创建路径
                os.makedirs(download_path, exist_ok=True)  # 创建下载路径
            target_file = os.path.join(download_path, 'chrome-linux.zip')  # 定义下载文件路径跟文件名
            await download_file(download_url, target_file)           #下载
            with zipfile.ZipFile(target_file, 'r') as zip_ref:
                zip_ref.extractall(download_path)
            os.remove(target_file)
            print('删包')
            os.chmod(chrome_path, 0o755)
            print('解压安装完成')
    elif platform.system() == 'Darwin':
        return 'mac'
    else:
        return 'unknown'

async def initql():        #初始化青龙并获取青龙的token
    global qlip  # 声明这个是全局变量
    client_id = None   #初始化变量
    client_secret = None   #初始化变量

    try:
        with open(configfile, 'r', encoding='utf-8') as file:    #用UTF-8编码方式打开配置文件
            lines = file.readlines()           #遍历每一行
            for line in lines:
                if 'qlip=' in line:
                    qlip = line.split('qlip=')[-1].strip()         #找配置文件中qlip=的值并赋予qlip
                elif 'client_id=' in line:
                    client_id = line.split('client_id=')[-1].strip()       #同上
                elif 'client_secret=' in line:
                    client_secret = line.split('client_secret=')[-1].strip()     #同上

        if not qlip or not client_id or not client_secret:         #如果没有三个参数变量没有值，就报下面的错误，单个检测报错
            if not qlip:
                print('青龙IP配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            if not client_id:
                print('青龙client_id配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            if not client_secret:
                print('青龙client_secret配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            raise SystemExit

        async with aiohttp.ClientSession() as session:                #获取青龙的token
            async with session.get(f"{qlip}/open/auth/token?client_id={client_id}&client_secret={client_secret}") as response:
                dicts = await response.json()
                print('已连接青龙容器...')
            return dicts['data']['token']
    except Exception as e:
        print(f"连接青龙发生异常，请确认配置文件：{e}")
        await asyncio.sleep(10)  # 等待10秒，等待
        raise SystemExit

async def qlenvs():   #获取青龙全部jdck变量
    try:
        async with aiohttp.ClientSession() as session:                              # 异步操作命令
            url = f"{qlip}/open/envs?searchValue="                   #设置设置连接
            headers = {'Authorization': 'Bearer ' + qltoken}                         #设置api的headers请求头
            async with session.get(url, headers=headers) as response:                              #获取变量请求
                rjson = await response.json()                             #解析返回的json数据
                if rjson['code'] == 200:                                #如果返回code200,根据青龙api文档
                    jd_cookie_data = [env for env in rjson['data'] if env.get('name') == 'JD_COOKIE']            #获取全部jd的变量
                    global notess      #把备注设置为全部变量
                    notess = [env['remarks'] for env in rjson['data'] if env.get('name') == 'JD_COOKIE' and env.get('status') == 0]             #找到所有name为JD_COOKIE，status为0的字典列表，然后把remarks的值放进notess
                    #global jdckpasswd      #把账号密码变量设为全局变量
                    #jdckpasswd = next((env['value'].strip().split('\n') for env in rjson['data'] if env.get('name') == 'jdckpasswd'), None)      #获取账号密码变量
                    global proxy_server      #把代理变量设为全局变量
                    proxy_server = next((env['value'].strip().split('\n') for env in rjson['data'] if env.get('name') == 'AutoJDCK_DP'), None)      #获取代理变量
                    return jd_cookie_data
                else:
                    print(f"获取环境变量失败：{rjson['message']}")
    except Exception as e:
        print(f"获取环境变量失败：{str(e)}")



async def push_message(qltoken, notes):
    js_file = 'JdckNotify.js'
    push_data = """
const notify = require('./sendNotify')
const message = ["{} 账号需要验证登录"];
notify.sendNotify(`JDCK登录验证通知`, message)
""".format(notes)       #脚本内容，{}是notes变量内容
    data = {
        "filename": js_file,
        "path": "./",
        "content": push_data    #脚本内容，如上push_data
    }
    async with aiohttp.ClientSession() as session:                             #推送运行脚本
        url = f"{qlip}/open/scripts/run"
        try:
            async with session.put(url, headers={'Authorization': 'Bearer ' + qltoken}, json=data) as response:            #更新变量的api
                rjson = await response.json()
                if rjson['code'] == 200:
                    print('推送验证通知')
                else:
                    print('推送验证通知失败,请检查青龙应用《脚本管理》权限')
        except Exception as e:
            print('推送验证通知失败,请检查青龙连接状态和应用《脚本管理》权限', e)







async def logon_main():             #读取配置文件账户密码，登录
    global qltoken   #初始化青龙获取青龙ck
    qltoken = await initql()      #初始化青龙token
    global envs               #青龙环境全局变量
    envs = await qlenvs()   #获取青龙环境变量(仅JC_COOKIE)
    await init_web_display()     #初始化WebDisplay
    global asgs
    asgs = await init_proxy_server()   #初始化登录代理（浏览器args的值）
    with open(configfile, 'r', encoding='utf-8') as jdckpasswd:
        for line in jdckpasswd:    # 去除行尾的换行符
            line = line.strip()    
            userdata = line.split('#')    # 使用'#'分割字符串
            if len(userdata) == 3:   #分为三段，如果不满足3段，则跳过此行
                usernum, passwd, notes= userdata     # 解包列表到四个变量，并按照指定格式打印
                if notes not in notess:        # 判断是否不存在 "notes" 在 notess 中
                    await validate_logon(usernum, passwd, notes)   #登录

async def get_user_choice():            #短信验证选择
    choice = None
    while choice not in ['1', '2']:
        try:
            choice = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, "需要进行短信验证，回1进行验证，回2不验证：  "),
                timeout=120
            )
            if choice not in ['1', '2']:
                print("无效输入，请只输入1或2，请重新输入：  ")
        except asyncio.TimeoutError:
            print("\n输入超时，跳过登陆")
            choice = '2'
            break
        except Exception as e:
            print("发生错误：", e)
    return choice

async def validate_logon(usernum, passwd, notes):                                         #登录操作
    print(f"正在登录 {notes} {usernum} 的账号")
    browser = await launch({
        'headless': WebDisplay,  # 设置为非无头模式，即可视化浏览器界面
        'args': asgs,
    })
    page = await browser.newPage()  # 打开新页面
    await page.setViewport({'width': 360, 'height': 640})  # 设置视窗大小
    await page.goto('https://plogin.m.jd.com/login/login?appid=300&returnurl=https%3A%2F%2Fm.jd.com%2F&source=wq_passport')  # 访问京东登录页面
    await typeuser(page, usernum, passwd)        #进行账号密码登录

    should_break = False  #定义下面不停循环
    while True:
        try:                              #找ck
            if await page.J ('#searchWrapper'):
                await SubmitCK(page, notes)  #提交ck
                await browser.close()  #关闭浏览器
                should_break = True
                break
        except Exception as e:
            pass

        try:                              #检查是不是要短信验证
            if await page.J('.sub-title'):       #<p data-v-4c407d20="" class="sub-title">选择认证方式</p>
                await push_message(qltoken, notes)          #推送需要验证登陆通知
                while True:
                    try:
                        choice = await get_user_choice()            #调用选择函数
                        if choice == '1':
                            print("正在发送短信验证")
                            await duanxin(page)    #调用短信登录函数
                            break
                        elif choice == '2':
                            await browser.close()  #关闭浏览器
                            print("不进行验证，跳过此账户登录")
                            should_break = True  
                            break
                        else:
                            print("无效的选择")
                    except asyncio.TimeoutError:
                        print("输入超时，跳过登陆")
                        should_break = True
                        break
        except Exception as e:
            pass

        try:                              #检测是否要过滑块
            if await page.xpath('//*[@id="small_img"]'):
                await verification(page)  #过滑块
        except Exception as e:
            pass

        try:
            if await page.xpath('//*[@id="captcha_modal"]/div/div[3]/button'):             #点击图片验证，无法过    
                await page.waitFor(3000)  # 等待3秒
                print("验证出错，正在重试……")
                await page.reload()                  #刷新浏览器
                await typeuser(page, usernum, passwd)        #进行账号密码登录
        except Exception as e:
            pass

        if should_break:  #检查是否停止循环
            break

async def typeuser(page, usernum, passwd):         #输入账户密码
    await page.waitForSelector('.J_ping.planBLogin')  # 等待元素出现
    await page.click('.J_ping.planBLogin')  # 点击密码登录
    await page.type('#username', usernum, {'delay': random.randint(60, 121)})  # 输入用户名，模拟键盘输入延迟
    await page.type('#pwd', passwd, {'delay': random.randint(100, 151)})  # 输入密码，模拟键盘输入延迟
    await page.waitFor(random.randint(100, 2000))      #随机等待1-2秒
    await page.click('.policy_tip-checkbox')  # 点击同意
    await page.waitFor(random.randint(100, 2000))      #随机等待1-2秒
    await page.click('.btn.J_ping.btn-active')  # 点击登录按钮
    await page.waitFor(random.randint(100, 2000))      #随机等待1-2秒
async def SubmitCK(page, notes):  #提交ck
    cookies = await page.cookies()                             #设置cookeis变量，用于下面的搜索
    pt_key = ''                             #初始化变量
    pt_pin = ''                             #初始化变量
    for cookie in cookies:                              #找所有网页所有的cookie数据
        if cookie['name'] == 'pt_key':                             #找到pt_key的值
            pt_key = cookie['value']                             #把值设置到变量pt_key
        elif cookie['name'] == 'pt_pin':                             #找到pt_pin的值
            pt_pin = cookie['value']                             #把值设置到变量pt_pin
    print('{} 登录成功 pt_key={};pt_pin={};'.format(notes, pt_key, pt_pin))    # 打印 pt_key 和 pt_pin 值
    with open('jdck.log', 'a+', encoding='utf-8') as file:    #打开文件
        content = '{}   {}   pt_key={};pt_pin={};\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, pt_key, pt_pin)   # 构造要写入文件的字符串
        file.write(content)  # 写入文件
    found_ddhhs = False                             #初始化循环变量，用于后面找不到变量的解决方式
    for env in envs:
        if notes in env["remarks"]:      #在所有变量值中找remarks，找到执行下面的更新ck
            envid = env["id"]                             #把找到的id设为envid的变量值
            remarks = env["remarks"]                             #同上
            found_ddhhs = True                             #把变量设为True，停下循环
            data = {
                'name': "JD_COOKIE",
                'value': f"pt_key={pt_key};pt_pin={pt_pin};",
                "remarks": remarks,
                "id": envid,
            }                             #提交青龙的数据
            async with aiohttp.ClientSession() as session:                             #下面是提交
                url = f"{qlip}/open/envs"
                async with session.put(url, headers={'Authorization': 'Bearer ' + qltoken}, json=data) as response:            #更新变量的api
                    rjson = await response.json()
                    if rjson['code'] == 200:
                        url2 = f"{qlip}/open/envs/enable"
                        data2 = [
                            envid
                        ]
                        async with session.put(url2, headers={'Authorization': 'Bearer ' + qltoken}, json=data2) as response:            #启用变量的api
                            rjson2 = await response.json()
                            if rjson2['code'] == 200:
                                print(f"更新{notes}环境变量成功")
                                return True
                            else:
                                print(f"启用{notes}环境变量失败：{rjson['message']}")
                                return False
                    else:
                        print(f"更新{notes}环境变量失败：{rjson['message']}")
                        return False
    if not found_ddhhs:          #如果没找到pt_pin，执行下面的新建ck，以下同上，只是新建不是更新
        data = [
            {
                'name': "JD_COOKIE",
                'value': f"pt_key={pt_key};pt_pin={pt_pin};",
                "remarks": notes,
            }
        ]
        async with aiohttp.ClientSession() as session:
            url = f"{qlip}/open/envs"
            async with session.post(url, headers={'Authorization': 'Bearer ' + qltoken}, json=data) as response:
                rjson = await response.json()
                if rjson['code'] == 200:
                    print(f"新建{notes}环境变量成功")
                    return True
                else:
                    print(f"新建{notes}环境变量失败：{rjson['message']}")
                    return False


async def get_verification_code():  # 交互输入验证码
    code = None
    while True:
        code = input("验证码已发送，请输入验证码: ")
        if len(code) == 6 and code.isdigit():
            break
        else:
            print("请输入6位数字作为验证码，请重新输入。")
    return code
async def duanxin(page):   #短信验证函数
        await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/span/a')   #等手机短信认证元素  //*[@id="app"]/div/div[2]
        await page.waitFor(random.randint(1, 3) * 1000)      #随机等待1-3秒
        elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/span/a')  # 选择元素
        await elements[0].click()  # 点击元素
        await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/button')   #等获取验证码元素
        await page.waitFor(random.randint(1, 3) * 1000)      #随机等待1-3秒
        elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/button')  # 选择元素
        await elements[0].click()  # 点击元素
        await page.waitFor(3000)  # 等待3秒，等待是否要滑块
        try:                              #检测是否要过滑块
            if await page.xpath('//*[@id="captcha_modal"]/div/div[3]/div'):
                await verification(page)  #过滑块
        except Exception as e:
            pass
        try:
            await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/div/input')   # 等待输入框元素出现
            code = await get_verification_code()   #交互输入验证码
            input_elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/div/input')    # 选择输入框元素
            await input_elements[0].type(code)       # 输入验证码
            await page.waitForXPath('//*[@id="app"]/div/div[2]/a[1]')   #等登录按钮元素
            await page.waitFor(random.randint(1, 3) * 1000)      #随机等待1-3秒
            elements = await page.xpath('//*[@id="app"]/div/div[2]/a[1]')  # 选择元素
            await elements[0].click()  # 点击元素
            await page.waitFor(random.randint(2, 3) * 1000)      #随机等待2-3秒
        except Exception as e:
            pass

async def verification(page):            #过滑块
    await page.waitForSelector('#cpc_img')
    image_src = await page.Jeval('#cpc_img', 'el => el.getAttribute("src")')  # 获取滑块背景图的地址
    request.urlretrieve(image_src, 'image.png')  # 下载滑块背景图
    width = await page.evaluate('() => { return document.getElementById("cpc_img").clientWidth; }')  #获取网页的图片尺寸
    height = await page.evaluate('() => { return document.getElementById("cpc_img").clientHeight; }')   #获取网页的图片尺寸
    image = Image.open('image.png')  #打开图像
    resized_image = image.resize((width, height))# 调整图像尺寸
    resized_image.save('image.png')# 保存调整后的图像
    template_src = await page.Jeval('#small_img', 'el => el.getAttribute("src")')  # 获取滑块图片的地址
    request.urlretrieve(template_src, 'template.png')  # 下载滑块图片
    width = await page.evaluate('() => { return document.getElementById("small_img").clientWidth; }')  #获取网页的图片尺寸
    height = await page.evaluate('() => { return document.getElementById("small_img").clientHeight; }')   #获取网页的图片尺寸
    image = Image.open('template.png')  #打开图像
    resized_image = image.resize((width, height))# 调整图像尺寸
    resized_image.save('template.png')# 保存调整后的图像
    await page.waitFor(100)  # 等待1秒，确保图片处理完成
    el = await page.querySelector("#captcha_modal > div > div.captcha_footer > div > img") # 定位到滑块按钮
    box = await el.boundingBox() #获取滑块按钮信息
    distance = await get_distance()  # 调用前面定义的get_distance函数计算滑块移动距离
    await page.mouse.move(box['x'] + 10 , box['y'] + 10)
    await page.mouse.down()  # 模拟鼠标按下
    await page.mouse.move(box['x'] + distance + random.uniform(8, 25), box['y'], {'steps': 10})  # 模拟鼠标拖动，考虑到实际操作中可能存在的轻微误差和波动，加入随机偏移量
    await page.waitFor(random.randint(100, 500))  # 随机等待一段时间，模仿人类操作的不确定性
    await page.mouse.move(box['x'] + distance, box['y'], {'steps': 10})  # 继续拖动滑块到目标位置
    await page.mouse.up()  # 模拟鼠标释放，完成滑块拖动
    await page.waitFor(3000)  # 等待3秒，等待滑块验证结果

async def get_distance():   #图形处理函数
    img = cv2.imread('image.png', 0)  # 读取全屏截图，灰度模式
    template = cv2.imread('template.png', 0)  # 读取滑块图片，灰度模式
    img = cv2.GaussianBlur(img, (5, 5), 0)  #图像高斯模糊处理
    template = cv2.GaussianBlur(template, (5, 5), 0)  #图像高斯模糊处理
    bg_edge = cv2.Canny(img, 100, 200)  #识别边缘
    cut_edge = cv2.Canny(template, 100, 200) #识别边缘
    img = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)  #转换图片格式，不知道是啥
    template = cv2.cvtColor(cut_edge, cv2.COLOR_GRAY2RGB) #转换图片格式，不知道是啥
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)  # 使用模板匹配寻找最佳匹配位置
    value = cv2.minMaxLoc(res)[3][0]  # 获取匹配结果的最小值位置，即为滑块起始位置
    distance = value + 10 # 计算实际滑动距离，这里根据实际页面比例进行调整，+10像素校准算法这傻逼玩意
    return distance


async def init_proxy_server():                                             #初始化代理
    if proxy_server:                 #如果有配置代理
        argszhi = '--no-sandbox', '--disable-setuid-sandbox', f'--proxy-server={proxy_server[0]}'        #设置浏览器参数加了个代理参数
        return argszhi
    else:
        argszhi = '--no-sandbox', '--disable-setuid-sandbox'
        return argszhi

async def get_latest_version():                                             #获取版本号函数
    url = f"https://api.github.com/repos/dsmggm/svjdck/releases/latest"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    tag_name = data["tag_name"]
                    print('最新版本：' + tag_name)
                else:
                    print('获取最新版本号失败')
    except aiohttp.ClientError as e:
        print(f'最新版本：你网络不行啊老弟，都连不上github，怎么获取最新版本号')


    

async def main():  # 打开并读取配置文件，主程序
    os.system('cls' if os.name == 'nt' else 'clear')    #清空屏幕
    await print_message('**********autojdck自动登陆京东获取ck程序**********')
    await print_message('注：账户密码已从青龙变量迁移到jdck.ini文件中，在配置文件中进行账密设置')
    await print_message('脚本需要青龙应用权限——环境变量跟脚本管理')
    await print_message('项目地址：https://github.com/dsmggm/svjdck')
    await print_message('当前版本：jdck20240405')
    await get_latest_version()       #获取最新版本
    await ifconfigfile()    #检测配置文件并初始化
    await init_chrome()     #检测初始化chrome
    await logon_main()    #登录操作，写入ck到文件
    os.remove('image.png') if os.path.exists('image.png') else None     #删除缓存照片
    os.remove('template.png') if os.path.exists('template.png') else None     #删除缓存照片
    await print_message('完成全部登录')
    await asyncio.sleep(10)  # 等待10秒，等待

asyncio.get_event_loop().run_until_complete(main())  #使用异步I/O循环运行main()函数，启动整个自动登录和滑块验证流程。

