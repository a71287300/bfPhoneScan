import re
import requests
import datetime
import json
import tkinter as tk
from tkinter import messagebox
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#get login key
def getSkey(url):
    login_url = "https://tw.beanfun.com/beanfun_block/bflogin/default.aspx?service_code=999999&service_region=T0"
    login_page = url.get(login_url,verify = False)
    r = re.compile('var strSessionKey = (.*?);')
    skey = r.search(str(login_page.text)).group(1).replace('"','')
    print('GET skey')
    return skey
#check login
def login_pages(skey,url,ac,pw):
    id_pass_url = 'https://tw.newlogin.beanfun.com/login/id-pass_form.aspx?skey=%s'%(skey)
    bf_login = url.get(id_pass_url)
    client = {
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        '__VIEWSTATE':re.search(r'id="__VIEWSTATE" value="(.*?)"',bf_login.text).group(1),
        '__VIEWSTATEGENERATOR':re.search(r'id="__VIEWSTATEGENERATOR" value="(.*?)"',bf_login.text).group(1),
        '__EVENTVALIDATION':re.search(r'id="__EVENTVALIDATION" value="(.*?)"',bf_login.text).group(1),
        't_AccountID':ac,
        't_Password':pw,
        'btn_login':"登入"
    }

    bf_login = url.post(id_pass_url,data = client)
    try:
        akey = re.search(r'AuthKey.value = "(.*?)";',bf_login.text).group(1)
        data = {
                'SessionKey': skey,
                'AuthKey': akey
            }
        return_url = 'https://tw.beanfun.com/beanfun_block/bflogin/return.aspx'
        url.post(return_url, data=data)
        web_token = url.cookies['bfWebToken']
        print('GET Token')
        return web_token
    except:
        result_label.config(text=f"登入失敗, 請確認帳號密碼...")
        print('Login Failed')
        return False

def creatSession(account, password):
    #建立 Session
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    session = requests.Session()#Url
    # session.headers.update({'User-Agent':user_agent})
    skey = getSkey(session)
    result_label.config(text=f"取得登入Token中, 請稍等")
    root.update()
    web_token = login_pages(skey,session,account,password)
    if web_token == False:
        return False
    return session

def scanPhone(session, prefix, postfix):
    execute_button.config(state="disabled")
    found = False
    start_scan_time = datetime.datetime.now()
    for number in range(10000):
        numbers = f'{number:04}'
        phone = prefix + numbers + postfix
        phone_data = {
          'PhoneNo': phone
        }
        sms_url = 'https://tw.beanfun.com/GamaniaWeb/OTP/CheckSMSOTP'
        sms = session.post(sms_url, data=phone_data)
        sms = json.loads(sms.text)
        running_time = datetime.datetime.now() - start_scan_time
        if sms.get("Result") != 3:
            print(sms, phone)
            result_label.config(text=f"掃描成功: {phone} \n 耗時{running_time}")
            found = True
            break
        else:
            print("掃描進度:" + str(number), end='')
            print('\r', end='')
            result_label.config(text=f"掃描進度 {number}/9999 \n 耗時{running_time}")
            root.update()
    execute_button.config(state="normal")
    if found == False:
        result_label.config(text=f"沒有掃描到QQ...請確認資訊正確")
    root.update()

def execute_program():
    account = account_entry.get()
    password = password_entry.get()
    prefix = prefix_entry.get()
    postfix = postfix_entry.get()
    if account and password and validate_len(prefix, 4) and validate_len(postfix, 2):
        session = creatSession(account, password)
        if prefix[:2] != "09":
            messagebox.showwarning("Warning","您填寫的手機並非09開頭, 仍然會進行掃描, 為避免浪費時間請重複確認")
        if session != False:
            scanPhone(session, prefix, postfix)
    else:
        messagebox.showerror("Error", "資料不完善, 四項皆須填寫, 且符合格式")

def validate_len(data, length):
    if len(data) == length and data.isdigit():
        return True
    return False

if __name__ == "__main__":
    root = tk.Tk()
    root.title("BF進階認證手機查詢")
    root.geometry("280x270")
 
    account_label = tk.Label(root, text="帳號:")
    account_label.pack()
    account_entry = tk.Entry(root)
    account_entry.pack()

    password_label = tk.Label(root, text="密碼:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")  # 輸入密碼時顯示*
    password_entry.pack()

    phone_prefix = tk.Label(root, text="手機前四碼:")
    phone_prefix.pack()
    prefix_entry = tk.Entry(root)
    prefix_entry.pack()
    phone_postfix = tk.Label(root, text="手機後兩碼:")
    phone_postfix.pack()
    postfix_entry = tk.Entry(root)
    postfix_entry.pack()

    execute_button = tk.Button(root, text="開始掃描",  command=execute_program)
    execute_button.pack()

    result_label = tk.Label(root, text="僅支持純帳號密碼登錄\n不支持QRCode或手機驗證")
    result_label.pack()

    signed_label = tk.Label(root, text="非營利目的使用 by R.K")
    signed_label.pack(anchor="se", side='bottom')
    root.mainloop()