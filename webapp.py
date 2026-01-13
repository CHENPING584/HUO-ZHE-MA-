from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于会话加密

# 授权码
AUTHORIZATION_CODE = "LYY996"

# 邮件配置
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')  # 从环境变量获取
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # 从环境变量获取
SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 0))

# 从config.ini读取邮件配置作为备份
import configparser
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

if not SMTP_USERNAME:
    SMTP_USERNAME = config.get('Email', 'sender_email', fallback='')
if not SMTP_PASSWORD:
    SMTP_PASSWORD = config.get('Email', 'sender_password', fallback='')

# 自动推断SMTP服务器和端口
if not SMTP_SERVER:
    SMTP_SERVER = config.get('Email', 'smtp_server', fallback='')
    if not SMTP_SERVER and SMTP_USERNAME:
        domain = SMTP_USERNAME.split('@')[-1].lower()
        if 'qq.com' in domain:
            SMTP_SERVER = 'smtp.qq.com'
        elif '163.com' in domain:
            SMTP_SERVER = 'smtp.163.com'
        elif '126.com' in domain:
            SMTP_SERVER = 'smtp.126.com'
        elif 'gmail.com' in domain:
            SMTP_SERVER = 'smtp.gmail.com'

if not SMTP_PORT:
    try:
        SMTP_PORT = int(config.get('Email', 'smtp_port', fallback='0'))
    except ValueError:
        SMTP_PORT = 0
    
    if SMTP_PORT == 0 and SMTP_SERVER:
        if 'qq.com' in SMTP_SERVER:
            SMTP_PORT = 465  # QQ邮箱推荐使用SSL
        elif '163.com' in SMTP_SERVER or '126.com' in SMTP_SERVER:
            SMTP_PORT = 465  # 网易邮箱推荐使用SSL
        else:
            SMTP_PORT = 587  # 其他通常使用TLS

# 数据库配置
# 根据环境配置数据库路径
if os.environ.get('VERCEL'):
    # Vercel环境
    DATABASE = "/tmp/sign_in.db"
else:
    # 本地环境，确保使用正确的路径分隔符
    DATABASE = os.path.join(os.getcwd(), "sign_in.db")
print(f"数据库路径: {DATABASE}")

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建签到记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sign_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sign_date TEXT NOT NULL,
        sign_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        consecutive_missed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# 确保在 Vercel 环境下每次启动都检查数据库表是否存在
if os.environ.get('VERCEL'):
    try:
        init_db()
        print("Vercel环境: 数据库表初始化完成")
    except Exception as e:
        print(f"Vercel环境: 数据库初始化失败 - {str(e)}")

# 检查用户是否已签到
def is_signed_in_today(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM sign_records WHERE user_id = ? AND sign_date = ?", (user_id, today))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

# 获取连续未签到天数
def get_consecutive_missed_days(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 获取最近的签到记录
    cursor.execute("SELECT sign_date FROM sign_records WHERE user_id = ? ORDER BY sign_date DESC", (user_id,))
    records = cursor.fetchall()
    
    today = datetime.date.today()
    
    if not records:
        # 如果没有签到记录，检查当前日期是否是系统启用后的第一天
        return 0
    
    # 获取最近一次签到日期
    last_sign_date = datetime.datetime.strptime(records[0][0], "%Y-%m-%d").date()
    
    # 计算从最后一次签到到今天的天数差
    days_diff = (today - last_sign_date).days
    
    # 如果今天已经签到，未签到天数为0
    if is_signed_in_today(user_id):
        return 0
    
    # 连续未签到天数 = 天数差 - 1（因为当天还没结束）
    consecutive_missed = days_diff
    
    conn.close()
    return consecutive_missed

# 获取连续签到天数
def get_consecutive_days(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 获取最近的签到记录
    cursor.execute("SELECT sign_date FROM sign_records WHERE user_id = ? ORDER BY sign_date DESC", (user_id,))
    records = cursor.fetchall()
    
    if not records:
        return 0
    
    consecutive = 0
    today = datetime.date.today()
    
    for record in records:
        sign_date = datetime.datetime.strptime(record[0], "%Y-%m-%d").date()
        expected_date = today - datetime.timedelta(days=consecutive)
        
        if sign_date == expected_date:
            consecutive += 1
        else:
            break
    
    conn.close()
    return consecutive

# 发送邮件函数
def send_email(to_email, subject, body):
    try:
        # 检查必要的邮件配置
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("邮件发送失败: 未配置SMTP用户名或密码")
            return False
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        print(f"正在连接SMTP服务器: {SMTP_SERVER}:{SMTP_PORT}")
        server = None
        
        try:
            # 根据端口选择连接方式
            if SMTP_PORT == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
            else:
                # TLS连接
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                server.starttls()
            
            print(f"正在登录SMTP服务器: {SMTP_USERNAME}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            print(f"正在发送邮件到: {to_email}")
            server.sendmail(SMTP_USERNAME, to_email, text)
            server.quit()
            
            print(f"邮件发送成功: {to_email}")
            return True, "邮件发送成功"
        except Exception as e:
            if server:
                try:
                    server.quit()
                except:
                    pass
            raise e
    except smtplib.SMTPAuthenticationError:
        print("邮件发送失败: SMTP认证失败，请检查用户名和密码")
        return False, "SMTP认证失败"
    except smtplib.SMTPConnectError:
        print(f"邮件发送失败: 无法连接到SMTP服务器 {SMTP_SERVER}:{SMTP_PORT}")
        return False, "无法连接到SMTP服务器"
    except smtplib.SMTPServerDisconnected:
        print("邮件发送失败: SMTP服务器连接断开")
        return False, "SMTP服务器连接断开"
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: SMTP错误 - {str(e)}")
        return False, f"SMTP错误: {str(e)}"
    except Exception as e:
        print(f"邮件发送失败: 其他错误 - {str(e)}")
        return False, f"发送失败: {str(e)}"

# 检查所有用户并发送未签到提醒
def check_and_send_reminders():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 获取所有用户
        cursor.execute("SELECT user_id, username, email FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, email = user
            
            # 计算连续未签到天数
            consecutive_missed = get_consecutive_missed_days(user_id)
            
            print(f"检查用户 {username}: 连续未签到 {consecutive_missed} 天")
            
            # 如果连续两天未签到，发送提醒
            if consecutive_missed >= 2:
                print(f"用户 {username} 连续 {consecutive_missed} 天未签到，发送提醒")
                
                # 发送内容
                subject = "紧急提醒 - 活着吗"
                body = f"您的好友{username}已连续 {consecutive_missed} 天未签到。\n\n发送时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 发送邮件（只发送已配置的联系方式）
                if email:
                    send_email(email, subject, body)
        
        conn.close()
    except Exception as e:
        print(f"检查并发送提醒失败: {str(e)}")

# 获取最长连续签到天数
def get_longest_streak(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 获取所有签到日期，按日期排序
    cursor.execute("SELECT sign_date FROM sign_records WHERE user_id = ? ORDER BY sign_date", (user_id,))
    records = cursor.fetchall()
    
    if not records:
        return 0
    
    longest_streak = 1
    current_streak = 1
    
    for i in range(1, len(records)):
        prev_date = datetime.datetime.strptime(records[i-1][0], "%Y-%m-%d").date()
        curr_date = datetime.datetime.strptime(records[i][0], "%Y-%m-%d").date()
        
        if (curr_date - prev_date).days == 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1
    
    conn.close()
    return longest_streak

# 授权码验证页面
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if code == AUTHORIZATION_CODE:
            session["authorized"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="授权码错误")
    return render_template("login.html")

# 主页面
@app.route("/home", methods=["GET", "POST"])
def home():
    if not session.get("authorized"):
        return redirect(url_for("login"))
    
    # 检查所有用户并发送未签到提醒
    check_and_send_reminders()
    
    # 检查用户是否已登录
    user_id = session.get("user_id")
    username = session.get("username", "")
    email = session.get("email", "")
    
    consecutive_days = 0
    longest_streak = 0
    signed_in_today = False
    
    if user_id:
        consecutive_days = get_consecutive_days(user_id)
        longest_streak = get_longest_streak(user_id)
        signed_in_today = is_signed_in_today(user_id)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "save_user":
            try:
                # 保存用户信息
                username = request.form.get("username")
                email = request.form.get("email")
                
                if not username or not email:
                    return render_template("home.html", username=username, email=email, error="用户名和邮箱不能为空")
                
                print(f"保存用户信息: username={username}, email={email}")
                print(f"数据库路径: {DATABASE}")
                
                # 确保数据库目录存在
                db_dir = os.path.dirname(DATABASE)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    print(f"创建数据库目录: {db_dir}")
                
                # 确保数据库表存在
                print("调用init_db()")
                init_db()
                print("init_db()调用完成")
                
                print("连接数据库")
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                print("数据库连接成功")
                
                # 检查用户是否已存在
                print(f"检查用户是否存在: {username}")
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cursor.fetchone()
                print(f"查询结果: {existing_user}")
                
                if existing_user:
                    # 更新用户信息
                    print(f"更新用户信息: user_id={existing_user[0]}, email={email}")
                    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (email, existing_user[0]))
                    user_id = existing_user[0]
                    print(f"更新成功")
                else:
                    # 添加新用户
                    print(f"添加新用户: username={username}, email={email}")
                    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
                    user_id = cursor.lastrowid
                    print(f"插入成功，user_id={user_id}")
                
                print("提交事务")
                conn.commit()
                print("事务提交成功")
                conn.close()
                print("数据库连接关闭")
                
                # 更新会话
                session["user_id"] = user_id
                session["username"] = username
                session["email"] = email
                print(f"会话更新成功: user_id={user_id}")
                
                # 刷新数据
                print("刷新数据")
                consecutive_days = get_consecutive_days(user_id)
                print(f"连续天数: {consecutive_days}")
                longest_streak = get_longest_streak(user_id)
                print(f"最长连续: {longest_streak}")
                signed_in_today = is_signed_in_today(user_id)
                print(f"今日已签到: {signed_in_today}")
                
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success="用户信息已保存")
            except Exception as e:
                # 打印详细的错误信息到日志
                import traceback
                print(f"保存用户信息错误: {str(e)}")
                print("错误堆栈:")
                traceback.print_exc()
                # 返回友好的错误信息给用户
                return render_template("home.html", username=username, email=email, error="保存用户信息失败，请稍后重试")
        
        elif action == "sign_in":
            try:
                # 执行签到
                if not user_id:
                    return render_template("home.html", username=username, email=email, error="请先保存用户信息")
                
                if signed_in_today:
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error="您今日已签到")
                
                # 确保数据库表存在
                init_db()
                
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                
                # 添加签到记录
                today = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO sign_records (user_id, sign_date) VALUES (?, ?)", (user_id, today))
                
                conn.commit()
                conn.close()
                
                # 刷新数据
                consecutive_days = get_consecutive_days(user_id)
                longest_streak = get_longest_streak(user_id)
                signed_in_today = True
                
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success="签到成功")
            except Exception as e:
                # 打印错误信息到日志
                print(f"签到错误: {str(e)}")
                # 返回友好的错误信息给用户
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error="签到失败，请稍后重试")
        
        elif action == "send_email":
            try:
                if not user_id:
                    return render_template("home.html", username=username, email=email, error="请先保存用户信息")
                
                if not email:
                    return render_template("home.html", username=username, email=email, error="请先设置紧急联系人邮箱")
                
                # 发送内容
                subject = "紧急提醒 - 活着吗"
                body = f"您的好友{username}已连续两天未签到。\n\n发送时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 发送邮件
                email_result, email_msg = False, "未配置邮箱"
                
                if email:
                    email_result, email_msg = send_email(email, subject, body)
                
                # 构建返回消息
                messages = []
                if email:
                    messages.append(f"邮件: {email_msg}")
                
                full_msg = " | ".join(messages)
                
                if email_result:
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success=f"紧急联系人已设置。通知发送结果: {full_msg}")
                else:
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error=f"发送通知失败: {full_msg}")
            except Exception as e:
                print(f"发送通知错误: {str(e)}")
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error=f"系统错误: {str(e)}")
    
    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today)

# 退出登录
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    
    # 启动时检查所有用户并发送未签到提醒
    check_and_send_reminders()
    
    # 生产环境配置
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host=host, port=port, debug=debug)
