# 第一次使用会有进度条加载，等待即可，后续无需等待
# 需要opencv-python、pyppeteer、Pillow、asyncio、aiohttp依赖
# 版本：2024.2.20
import asyncio  # 异步I/O操作库
import random  #用于模拟延迟输入
from re import T  # 随机数生成库
import cv2  # OpenCV库，用于图像处理
from pyppeteer import launch  # pyppeteer库，用于自动化控制浏览器
import aiohttp   #用于请求青龙
from urllib import request  # 用于网络请求，这里主要用来下载图片
from PIL import Image  #用于图像处理
import os  #读取配置文件
import platform  #判断系统类型

async def initql(configfile):        #初始化青龙并获取青龙的token
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
            return dicts['data']['token']
    except Exception as e:
        print(f"连接青龙发生异常，请确认配置文件：{e}")
        await asyncio.sleep(10)  # 等待10秒，等待
        raise SystemExit

async def qlenvs(qltoken):   #获取青龙全部ck
    try:
        async with aiohttp.ClientSession() as session:                              # 异步操作命令
            url = f"{qlip}/open/envs?searchValue="                   #设置设置连接
            headers = {'Authorization': 'Bearer ' + qltoken}                         #设置api的headers请求头
            async with session.get(url, headers=headers) as response:                              #获取变量请求
                rjson = await response.json()                             #解析返回的json数据
                if rjson['code'] == 200:                                #如果返回code200,根据青龙api文档
                    jd_cookie_data = [env for env in rjson['data'] if env.get('name') == 'JD_COOKIE']      #选出所有JD_COOKIE的名的变量
                    return jd_cookie_data                              #返回选出来的值给整个函数
                else:
                    print(f"获取环境变量失败：{rjson['message']}")
    except Exception as e:
        print(f"获取环境变量失败：{str(e)}")

async def SubmitCK(page, notes, qltoken):  #提交ck函数
    cookies = await page.cookies()                             #设置cookeis变量，用于下面的搜索
    pt_key = ''                             #初始化变量
    pt_pin = ''                             #初始化变量
    for cookie in cookies:                              #找所有网页所有的cookie数据
        if cookie['name'] == 'pt_key':                             #找到pt_key的值
            pt_key = cookie['value']                             #把值设置到变量pt_key
        elif cookie['name'] == 'pt_pin':                             #找到pt_pin的值
            pt_pin = cookie['value']                             #把值设置到变量pt_pin
    print('{} 登录成功 pt_key={};pt_pin={};'.format(notes, pt_key, pt_pin))    # 打印 pt_key 和 pt_pin 值
    found_ddhhs = False                             #初始化循环变量，用于后面找不到变量的解决方式
    for env in envs:
        if pt_pin in env["value"]:      #在所有变量值中找pt_pin，找到执行下面的更新ck
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

async def verification(page, notes, usernum, passwd, browser):
    try:
        await page.waitForSelector('#cpc_img')
        image_src = await page.Jeval('#cpc_img', 'el => el.getAttribute("src")')  # 获取滑块背景图的地址
        request.urlretrieve(image_src, 'image.png')  # 下载滑块背景图
        await page.waitFor(100)  # 等待1秒，确保图片下载完成
        width = await page.evaluate('() => { return document.getElementById("cpc_img").clientWidth; }')  #获取网页的图片尺寸
        height = await page.evaluate('() => { return document.getElementById("cpc_img").clientHeight; }')   #获取网页的图片尺寸
        image = Image.open('image.png')  #打开图像
        resized_image = image.resize((width, height))# 调整图像尺寸
        resized_image.save('image.png')# 保存调整后的图像
        await page.waitFor(100)  # 等待1秒，确保图片处理完成
        template_src = await page.Jeval('#small_img', 'el => el.getAttribute("src")')  # 获取滑块图片的地址
        request.urlretrieve(template_src, 'template.png')  # 下载滑块图片
        await page.waitFor(100)  # 等待1秒，确保图片下载完成
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
    except Exception as e:
        print(f"滑块验证出错，1秒后自动关闭重试")
        await page.waitFor(1000)  # 等1秒
        await browser.close()  #关闭浏览器
        await validate_logon(notes, usernum, passwd)
        raise e  # 将异常重新抛出，以便上层代码处理

async def duanxin(page, notes, usernum, passwd, browser):   #短信验证函数
    if await page.J('.mode-btn.voice-mode'):  #检查是不是要短信验证
        await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/span/a')   #等手机短信认证元素
        elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/span/a')  # 选择元素
        await elements[0].click()  # 点击元素
        await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/button')   #等获取验证码元素
        elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/button')  # 选择元素
        await elements[0].click()  # 点击元素
        await verification(page, notes, usernum, passwd, browser)    #过滑块
        code = input("请输入验证码: ")   #交互输入验证码
        await page.waitForXPath('//*[@id="app"]/div/div[2]/div[2]/div/input')   # 等待输入框元素出现
        input_elements = await page.xpath('//*[@id="app"]/div/div[2]/div[2]/div/input')    # 选择输入框元素
        await input_elements[0].type(code)       # 输入验证码
        await page.waitForXPath('//*[@id="app"]/div/div[2]/a[1]')   #等登录按钮元素
        elements = await page.xpath('//*[@id="app"]/div/div[2]/a[1]')  # 选择元素
        await elements[0].click()  # 点击元素
        await page.waitFor(2000)  # 等2秒

async def validate_logon(notes, usernum, passwd, qltoken):
    print(f"正在登录{notes}的账号")
    browser = await launch({
        'headless': WebDisplay,  # 设置为非无头模式，即可视化浏览器界面
        'args': ['--no-sandbox', '--disable-setuid-sandbox'],  # 启动参数，禁用沙箱模式，设置窗口大小
    })
    page = await browser.newPage()  # 打开新页面
    await page.setViewport({'width': 360, 'height': 640})  # 设置视窗大小
    await page.goto('https://plogin.m.jd.com/login/login?appid=300&returnurl=https%3A%2F%2Fm.jd.com%2F&source=wq_passport')  # 访问京东登录页面
    await page.waitFor(1000)  # 等待1秒，等待页面加载
    await page.click('.J_ping.planBLogin')  # 点击密码登录
    await page.type('#username', usernum, {'delay': random.randint(60, 121)})  # 输入用户名，模拟键盘输入延迟
    await page.type('#pwd', passwd, {'delay': random.randint(100, 151)})  # 输入密码，模拟键盘输入延迟
    await page.waitFor(100)  # 等待
    await page.click('.policy_tip-checkbox')  # 点击同意
    await page.waitFor(141)  # 等待
    await page.click('.btn.J_ping.btn-active')  # 点击登录按钮
    await page.waitFor(1000)  # 等待3秒，等待滑块验证出现

    should_break = False  #定义下面不停循环
    while True:
        if await page.J ('#searchWrapper'):  # 检查是否登录成功
            await SubmitCK(page, notes, qltoken)  #提交ck
            await browser.close()  #关闭浏览器
            break
        else:
            if await page.J('.mode-btn.voice-mode'):  #检查是不是要短信验证
                while True:
                    choice = input("需要进行短信验证，回1进行验证，回2不验证：\n")
                    if choice == '1':
                        await duanxin(page, notes, usernum, passwd, browser)    #调用短信登录函数
                        break
                    elif choice == '2':
                        print("不进行验证，跳过此账户登录")
                        should_break = True
                        break
                    else:
                        ("无效的选择")
            else:
                await verification(page, notes, usernum, passwd, browser)  #检测是否要过滑块
        if should_break:  #检查是否停止循环
            break
                
async def main():  # 打开并读取配置文件，主程序
    configfile = 'jdck.ini'     #配置文件名称为
    if not os.path.exists(configfile):     #看看有没有配置文件
        configdata = [
    'Displaylogin=0  #是否显示登录操作，1显示，0不显示\n',
    'qlip=http://192.168.1.1:5700\n',
    'client_id=*******\n',
    'client_secret=*******\n',
    '\n',
    '********上面是配置参数，下面保存账户密码********\n',
    '\n',
    '备注1#登录账号1#登录密码\n',
    '备注2#登录账号2#登录密码\n',
    '备注3#登录账号3#登录密码\n'
    '账号格式以此类推\n',
]
        with open(configfile, 'w', encoding='utf-8') as file:     #打开配置文件
            file.writelines(configdata)       #写入configdata的内容到配置文件
            print('已在当前脚本目录下生成了配置文件，请修改后再运行')
            await asyncio.sleep(10)  # 等待6秒，等待
    else:
        global envs
        qltoken = await initql(configfile)   #初始化青龙获取青龙ck
        envs = await qlenvs(qltoken)   #获取青龙环境变量(仅JC_COOKIE)
        with open(configfile, 'r', encoding='utf-8') as file:   # 对于文件中的每一行
            for line in file:    # 去除行尾的换行符
                line = line.strip()    
                userdata = line.split('#')    # 使用'#'分割字符串
                if len(userdata) == 3:   #分为三段，如果不满足3段，则跳过此行
                    notes, usernum, passwd = userdata     # 解包列表到三个变量，并按照指定格式打印
                    try:
                        global WebDisplay                             #设置为全局变量
                        WebDisplay = True                             #默认不显示登录
                        with open(configfile, 'r', encoding='utf-8') as file:
                            for line in file:
                                if 'Displaylogin=1' in line:                             #如果配置文件有Displaylogin=1这个东西
                                    WebDisplay = False                             #就变更成显示登录操作
                                    print('当前模式：显示登录操作')
                                    break
                    except FileNotFoundError:
                        print("当前配置不显示登录操作，如果需要显示在配置文件中增加参数Displaylogin=1")
                    await validate_logon(notes, usernum, passwd, qltoken)    #登录操作，写入ck到文件
            print("完成全部登录")
            os.remove('image.png') if os.path.exists('image.png') else None     #删除缓存照片
            os.remove('template.png') if os.path.exists('template.png') else None     #删除缓存照片
            await asyncio.sleep(10)  # 等待10秒，等待

asyncio.get_event_loop().run_until_complete(main())  #使用异步I/O循环运行main()函数，启动整个自动登录和滑块验证流程。
