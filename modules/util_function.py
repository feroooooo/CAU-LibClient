import requests
from PySide6.QtCore import QThread, Signal


# 获取验证码
class CodeThread(QThread):
    signal = Signal(str, bytes)
    def __init__(self):
        super().__init__()
        
    def run(self):
        headers = {
            "Host":"libwx.cau.edu.cn",
            "User-Agent":f"Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/119.0.0.0",
        }
        response = requests.get("http://libwx.cau.edu.cn/remote/static/authIndex", headers=headers)
        try:
            tmp_str = response.headers["Set-Cookie"]
            cookie = tmp_str[:tmp_str.find(";")]
        except:
            self.signal.emit('', bytes())
            return
        
        headers = {
            "Host":"libwx.cau.edu.cn",
            "User-Agent":f"Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/119.0.0.0",
            "Cookie":cookie
        }
        response = requests.get("http://libwx.cau.edu.cn/remote/static/code/image", headers=headers)

        img_data = response.content        
        self.signal.emit(cookie, img_data)


# 登录请求 
class LoginThread(QThread):
    signal = Signal(int,str,str,str)
    def __init__(self, cookie, number, password, code):
        super().__init__()
        self.cookie = cookie
        self.number = number
        self.password = password
        self.code = code
        
    def run(self):
        headers = {
            "Host":"libwx.cau.edu.cn",
            "User-Agent":f"Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/119.0.0.0",
            "Content-Length":"47",
            "Content-Type":"application/x-www-form-urlencoded",
            "Referer":"http://libwx.cau.edu.cn/remote/static/authIndex",
            "Origin":"http://libwx.cau.edu.cn",
            "Cache-Control":"max-age=0",
            "Cookie":self.cookie
        }
        payload = {
            "uname":self.number,
            "upass":self.password,
            "codeImage":self.code
        }
        response = requests.post("http://libwx.cau.edu.cn/remote/static/phoneloginHandler", headers=headers, data=payload)
        
        ret = 0
        account = ''
        upass = ''
        ticketCode = ''
        
        if response.text.find("account") != -1:
            ret = 1
            account = response.text[response.text.find("account")+8:response.text.find("account")+40]
            upass = response.text[response.text.find("upass")+6:response.text.find("upass")+38]
            ticketCode = response.text[response.text.find("ticketCode")+11:response.text.find("ticketCode")+43]
        elif response.text.find("验证码错误") != -1:
            ret = 2
        elif response.text.find("认证失败，用户名或密码错误") != -1:
            ret = 3
        
        self.signal.emit(ret, account, upass, ticketCode)
        

# 获取登录态Cookie
class CookieThread(QThread):
    signal = Signal(str)
    def __init__(self, account, upass, ticketCode):
        super().__init__()
        self.account = account
        self.upass = upass
        self.ticketCode = ticketCode
        
    def run(self):
        # 登录，获取Cookie
        headers = {
            "Host":"libwx.cau.edu.cn",
            "User-Agent":f"Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/119.0.0.0",
            "Referer":"http://libwx.cau.edu.cn/remote/static/phoneloginHandler"
        }
        params = {
            'type':'discuss',
            'openid':'',
            'account':self.account,
            'upass':self.upass,
            'ticketCode':self.ticketCode,
            'nickname':'',
            'isFlag':'',
            'headimgurl':'',
            'sign':''
        }
        response = requests.get("http://libwx.cau.edu.cn/space/static/dowechatlogin?type=discuss", headers=headers, params=params)
        cookie = response.request.headers['Cookie']
        
        self.signal.emit(cookie)


# 功能函数
class UtilFunction:
    def verify(number, password, code):
        flag = False
        if number.isdigit() and password.isdigit() and code.isdigit():
            if len(number) == 13 and len(password) == 6 and len(code) == 4:
                flag = True
        return flag