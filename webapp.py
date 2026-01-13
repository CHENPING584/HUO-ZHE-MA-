from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
from datetime import timedelta
import os
import smtplib
import random
import quotes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
# 使用固定密钥以保持会话（仅用于演示，生产环境应使用环境变量）
app.secret_key = os.environ.get('SECRET_KEY', 'huo-zhe-ma-secret-key-2024')
app.permanent_session_lifetime = timedelta(days=3650) # 10年过期，实现"一次输入永久有效"

# 邮件配置
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')  # 从环境变量获取
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # 从环境变量获取
SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 0))

# 管理员密码 (简单硬编码，实际应使用环境变量)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '200599XC')

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
    
    # 检查并添加 auth_code 列
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'auth_code' not in columns:
        print("Migrating database: Adding auth_code column to users table")
        try:
            # SQLite不支持在已有数据的非空列上直接添加UNIQUE约束，所以先添加普通列
            # 但这里我们希望它是唯一的，对于新列（全是NULL），这是允许的，或者我们可以先允许NULL
            cursor.execute("ALTER TABLE users ADD COLUMN auth_code TEXT")
            # 创建唯一索引以确保唯一性
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_auth_code ON users(auth_code)")
            
            # 为现有用户生成随机授权码
            cursor.execute("SELECT user_id FROM users WHERE auth_code IS NULL")
            users_without_code = cursor.fetchall()
            
            import string
            chars = string.ascii_uppercase + string.digits
            
            for (uid,) in users_without_code:
                while True:
                    new_code = ''.join(random.choice(chars) for _ in range(6))
                    # 检查冲突
                    cursor.execute("SELECT 1 FROM users WHERE auth_code = ?", (new_code,))
                    if not cursor.fetchone():
                        cursor.execute("UPDATE users SET auth_code = ? WHERE user_id = ?", (new_code, uid))
                        break
            print(f"Migrated {len(users_without_code)} existing users with new auth codes")
            
        except Exception as e:
            print(f"Migration warning: {e}")
            
    # 检查并添加 setup_completed 列
    if 'setup_completed' not in columns:
        print("Migrating database: Adding setup_completed column to users table")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN setup_completed INTEGER DEFAULT 0")
            # 现有用户（非未激活）视为已完成设置
            cursor.execute("UPDATE users SET setup_completed = 1 WHERE username NOT LIKE '未激活_%' AND username NOT LIKE '用户_%'")
        except Exception as e:
            print(f"Migration warning: {e}")

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

# Vercel环境下的数据库初始化标记
_db_initialized = False

@app.before_request
def initialize_database():
    global _db_initialized
    if os.environ.get('VERCEL') and not _db_initialized:
        try:
            init_db()
            _db_initialized = True
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
    if session.get("authorized"):
        return redirect(url_for("home"))
        
    if request.method == "POST":
        code = request.form.get("code")
        if code:
            # 统一转换为大写并去除首尾空格
            code = code.strip().upper()
            
            try:
                # 确保数据库表结构最新
                init_db()
                
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                
                # 检查是否存在绑定该授权码的用户
                cursor.execute("SELECT user_id, username, email FROM users WHERE auth_code = ?", (code,))
                user = cursor.fetchone()
                
                if user:
                    # 用户存在，直接登录
                    user_id, username, email = user
                    session["user_id"] = user_id
                    session["username"] = username
                    session["email"] = email
                    session["authorized"] = True
                    session.permanent = True # 设置永久会话
                    
                    conn.close()
                    return redirect(url_for("home"))
                else:
                    # 授权码不存在，提示错误（不再自动注册）
                    conn.close()
                    return render_template("login.html", error="无效的授权码，请联系管理员获取")
            except Exception as e:
                print(f"Login error: {str(e)}")
                return render_template("login.html", error="登录失败，系统错误")
        else:
            return render_template("login.html", error="请输入授权码")
            
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
                    return render_template("home.html", username=username, email=email, error="用户名和邮箱不能为空", step='save_info')
                
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
                
                # 检查用户是否已存在（排除自己）
                print(f"检查用户名是否可用: {username}")
                cursor.execute("SELECT user_id FROM users WHERE username = ? AND user_id != ?", (username, user_id))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    conn.close()
                    return render_template("home.html", username=username, email=email, error="该用户名已被使用，请换一个", step='save_info')
                
                # 更新当前用户信息
                print(f"更新用户信息: user_id={user_id}, username={username}, email={email}")
                # 每次修改信息都重置setup_completed状态，强制重新验证
                cursor.execute("UPDATE users SET username = ?, email = ?, setup_completed = 0 WHERE user_id = ?", (username, email, user_id))
                print(f"更新成功")
                
                print("提交事务")
                conn.commit()
                print("事务提交成功")
                conn.close()
                print("数据库连接关闭")
                
                # 更新会话
                session["user_id"] = user_id
                session["username"] = username
                session["email"] = email
                session["info_saved"] = True  # 标记用户信息已保存
                session["email_sent"] = False # 重新保存后需要重新发送邮件
                print(f"会话更新成功: user_id={user_id}")
                
                # 刷新数据
                print("刷新数据")
                consecutive_days = get_consecutive_days(user_id)
                print(f"连续天数: {consecutive_days}")
                longest_streak = get_longest_streak(user_id)
                print(f"最长连续: {longest_streak}")
                signed_in_today = is_signed_in_today(user_id)
                print(f"今日已签到: {signed_in_today}")
                
                # 计算步骤状态
                step = 'done'
                if not signed_in_today:
                    # 检查是否使用了默认用户名（以"用户_"开头），如果是则认为未保存信息
                    if not session.get("info_saved") or username.startswith("用户_"):
                        step = 'save_info'
                    elif not session.get("email_sent"):
                        step = 'send_email'
                
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success="用户信息已保存", step=step)
            except Exception as e:
                # 打印详细的错误信息到日志
                import traceback
                print(f"保存用户信息错误: {str(e)}")
                print("错误堆栈:")
                traceback.print_exc()
                # 返回友好的错误信息给用户
                return render_template("home.html", username=username, email=email, error="保存用户信息失败，请稍后重试", step='save_info')
        
        elif action == "sign_in":
            try:
                # 执行签到
                if not user_id:
                    return render_template("home.html", username=username, email=email, error="请先保存用户信息", step='save_info')
                
                # 检查是否已完成设置
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute("SELECT setup_completed FROM users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                conn.close()
                
                if not result or not result[0]:
                    return render_template("home.html", username=username, email=email, error="请先完成邮箱验证", step='send_email')
                
                if signed_in_today:
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error="您今日已签到", step='done')
                
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
                
                # 获取已使用的语录索引
                used_quotes = session.get("used_quotes", [])
                
                # 计算可用索引
                all_indices = set(range(len(quotes.QUOTES)))
                available_indices = list(all_indices - set(used_quotes))
                
                if not available_indices:
                    # 如果所有语录都用过了，重置
                    used_quotes = []
                    available_indices = list(all_indices)
                
                # 随机选择一个索引
                if available_indices:
                    quote_index = random.choice(available_indices)
                    quote = quotes.QUOTES[quote_index]
                    
                    # 更新已使用列表
                    used_quotes.append(quote_index)
                    session["used_quotes"] = used_quotes
                else:
                    #以防万一quotes为空
                    quote = "加油！"
                
                # 随机选择一个主题图标 (1-4)
                theme_id = random.randint(1, 4)
                
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success="签到成功", step='done', quote=quote, theme_id=theme_id)
            except Exception as e:
                # 打印错误信息到日志
                print(f"签到错误: {str(e)}")
                # 返回友好的错误信息给用户
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error="签到失败，请稍后重试", step='done') # 签到失败可能需要保持原状态，但这里简单处理，或者重新计算step
        
        elif action == "send_email":
            try:
                if not user_id:
                    return render_template("home.html", username=username, email=email, error="请先保存用户信息", show_form=True)
                
                if not email:
                    return render_template("home.html", username=username, email=email, error="请先设置紧急联系人邮箱", show_form=True)
                
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
                    session["email_sent"] = True  # 标记邮件已发送
                    
                    # 更新数据库状态
                    conn = sqlite3.connect(DATABASE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET setup_completed = 1 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    conn.close()
                    
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, success=f"紧急联系人已设置。通知发送结果: {full_msg}", step='done')
                else:
                    # 发送失败，显示发送邮件按钮
                    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error=f"发送通知失败: {full_msg}", step='send_email')
            except Exception as e:
                print(f"发送通知错误: {str(e)}")
                return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, error=f"系统错误: {str(e)}", step='send_email')
        
        elif action == "edit_info":
            session["info_saved"] = False
            session["email_sent"] = False
            return redirect(url_for("home"))
    
    # 计算步骤状态
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT setup_completed FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    is_setup_completed = result and result[0] == 1
    
    step = 'done'
    if not is_setup_completed:
        if not username or username.startswith("未激活_") or username.startswith("用户_") or not email:
            step = 'save_info'
        else:
            step = 'send_email'
    
    return render_template("home.html", username=username, email=email, consecutive_days=consecutive_days, longest_streak=longest_streak, signed_in_today=signed_in_today, step=step)

# 退出登录
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- 管理员路由 ---

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
        
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "密码错误"
            
    return render_template("admin.html", logged_in=False, error=error)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 获取所有用户数据
    cursor.execute("""
        SELECT u.user_id, u.auth_code, u.username, u.email, 
               (SELECT MAX(sign_date) FROM sign_records WHERE user_id = u.user_id) as last_sign
        FROM users u
    """)
    rows = cursor.fetchall()
    
    users_data = []
    active_today_count = 0
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    for row in rows:
        user_id, auth_code, username, email, last_sign = row
        streak = get_consecutive_days(user_id)
        
        if last_sign == today_str:
            active_today_count += 1
            
        users_data.append({
            "id": user_id,
            "auth_code": auth_code if auth_code else "(旧用户)",
            "username": username,
            "email": email,
            "streak": streak,
            "last_sign": last_sign
        })
    
    conn.close()
    
    return render_template("admin.html", logged_in=True, users=users_data, 
                          total_users=len(users_data), active_today=active_today_count)

@app.route("/admin/generate", methods=["POST"])
def admin_generate_code():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
        
    # 生成随机6位字母数字组合
    import string
    chars = string.ascii_uppercase + string.digits
    while True:
        new_code = ''.join(random.choice(chars) for _ in range(6))
        # 检查是否重复
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE auth_code = ?", (new_code,))
        if not cursor.fetchone():
            # 创建预留用户
            try:
                temp_username = f"未激活_{new_code}"
                cursor.execute("INSERT INTO users (username, auth_code) VALUES (?, ?)", (temp_username, new_code))
                conn.commit()
                conn.close()
                break
            except sqlite3.IntegrityError:
                conn.close()
                continue
        conn.close()
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete", methods=["POST"])
def admin_delete_user():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
        
    user_id = request.form.get("user_id")
    if user_id:
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            # 删除签到记录
            cursor.execute("DELETE FROM sign_records WHERE user_id = ?", (user_id,))
            # 删除用户
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Delete error: {e}")
            
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# 确保应用启动时初始化数据库
init_db()

if __name__ == "__main__":
    # 启动时检查所有用户并发送未签到提醒
    check_and_send_reminders()
    
    # 生产环境配置
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host=host, port=port, debug=debug)
