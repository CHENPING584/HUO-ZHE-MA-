import sqlite3
import datetime
import os

class SignInDatabase:
    def __init__(self, db_path='sign_in.db'):
        """
        初始化数据库连接
        :param db_path: 数据库文件路径，默认当前目录下的sign_in.db
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """
        连接到SQLite数据库
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"数据库连接成功: {self.db_path}")
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")
            raise
    
    def _create_tables(self):
        """
        创建用户表和签到记录表
        """
        try:
            # 用户表：存储用户名、邮箱、注册时间
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE,
                    register_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 签到记录表：存储用户ID、签到日期、未签到累计天数
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sign_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    sign_date DATE NOT NULL,
                    consecutive_missed INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE (user_id, sign_date)
                )
            ''')
            
            self.conn.commit()
            print("数据库表创建成功")
        except sqlite3.Error as e:
            print(f"创建表失败: {e}")
            self.conn.rollback()
            raise
    
    def add_user(self, username, email=None):
        """
        添加新用户
        :param username: 用户名
        :param email: 邮箱（可选）
        :return: 用户ID，如果用户已存在返回None
        """
        if not username:
            raise ValueError("用户名不能为空")
        
        if not email:
            raise ValueError("邮箱不能为空")
        
        try:
            self.cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # 用户名或邮箱已存在
            return None
        except sqlite3.Error as e:
            print(f"添加用户失败: {e}")
            self.conn.rollback()
            raise
    
    def get_user_by_id(self, user_id):
        """
        根据用户ID获取用户信息
        :param user_id: 用户ID
        :return: 用户信息字典，如果不存在返回None
        """
        try:
            self.cursor.execute("SELECT user_id, username, email, register_time FROM users WHERE user_id = ?", (user_id,))
            user = self.cursor.fetchone()
            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'register_time': user[3]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取用户信息失败: {e}")
            raise
    
    def get_user_by_username(self, username):
        """
        根据用户名获取用户信息
        :param username: 用户名
        :return: 用户信息字典，如果不存在返回None
        """
        try:
            self.cursor.execute("SELECT user_id, username, email, register_time FROM users WHERE username = ?", (username,))
            user = self.cursor.fetchone()
            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'register_time': user[3]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取用户信息失败: {e}")
            raise
    
    def update_user(self, user_id, username=None, email=None):
        """
        更新用户信息
        :param user_id: 用户ID
        :param username: 新用户名（可选）
        :param email: 新邮箱（可选）
        :return: 是否更新成功
        """
        if not username and not email:
            return False
        
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            if username:
                update_fields.append("username = ?")
                update_values.append(username)
            if email:
                update_fields.append("email = ?")
                update_values.append(email)
            
            update_values.append(user_id)
            
            self.cursor.execute(
                f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?",
                tuple(update_values)
            )
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新用户信息失败: {e}")
            self.conn.rollback()
            raise
    
    def delete_user(self, user_id):
        """
        删除用户
        :param user_id: 用户ID
        :return: 是否删除成功
        """
        try:
            # 先删除该用户的签到记录
            self.cursor.execute("DELETE FROM sign_records WHERE user_id = ?", (user_id,))
            # 再删除用户
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除用户失败: {e}")
            self.conn.rollback()
            raise
    
    def get_all_users(self):
        """
        获取所有用户信息
        :return: 用户信息列表
        """
        try:
            self.cursor.execute("SELECT user_id, username, email, register_time FROM users")
            users = self.cursor.fetchall()
            return [{
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'register_time': user[3]
            } for user in users]
        except sqlite3.Error as e:
            print(f"获取所有用户失败: {e}")
            raise
    
    def add_sign_record(self, user_id):
        """
        添加签到记录
        :param user_id: 用户ID
        :return: 签到记录ID
        """
        today = datetime.date.today()
        try:
            # 检查今日是否已签到
            self.cursor.execute(
                "SELECT * FROM sign_records WHERE user_id = ? AND sign_date = ?",
                (user_id, today)
            )
            if self.cursor.fetchone():
                return None  # 今日已签到
            
            # 计算连续未签到天数
            yesterday = today - datetime.timedelta(days=1)
            self.cursor.execute(
                "SELECT consecutive_missed FROM sign_records WHERE user_id = ? AND sign_date = ?",
                (user_id, yesterday)
            )
            yesterday_record = self.cursor.fetchone()
            
            if yesterday_record:
                # 如果昨天有记录，重置连续未签到天数
                consecutive_missed = 0
            else:
                # 检查最近的签到记录
                self.cursor.execute(
                    "SELECT consecutive_missed, sign_date FROM sign_records WHERE user_id = ? ORDER BY sign_date DESC LIMIT 1",
                    (user_id,)
                )
                last_record = self.cursor.fetchone()
                
                if last_record:
                    last_date = last_record[1]
                    days_diff = (today - datetime.datetime.strptime(last_date, '%Y-%m-%d').date()).days
                    if days_diff > 1:
                        consecutive_missed = days_diff - 1
                    else:
                        consecutive_missed = 0
                else:
                    consecutive_missed = 0
            
            # 添加今日签到记录
            self.cursor.execute(
                "INSERT INTO sign_records (user_id, sign_date, consecutive_missed) VALUES (?, ?, ?)",
                (user_id, today, consecutive_missed)
            )
            
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加签到记录失败: {e}")
            self.conn.rollback()
            raise
    
    def get_sign_status(self, user_id):
        """
        获取用户今日签到状态
        :param user_id: 用户ID
        :return: True表示今日已签到，False表示未签到
        """
        today = datetime.date.today()
        try:
            self.cursor.execute(
                "SELECT * FROM sign_records WHERE user_id = ? AND sign_date = ?",
                (user_id, today)
            )
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"获取签到状态失败: {e}")
            raise
    
    def get_sign_history(self, user_id, limit=30):
        """
        获取用户签到历史记录
        :param user_id: 用户ID
        :param limit: 返回记录数量限制，默认30条
        :return: 签到历史记录列表
        """
        try:
            self.cursor.execute(
                "SELECT sign_date, consecutive_missed FROM sign_records WHERE user_id = ? ORDER BY sign_date DESC LIMIT ?",
                (user_id, limit)
            )
            records = self.cursor.fetchall()
            return [{
                'sign_date': record[0],
                'consecutive_missed': record[1]
            } for record in records]
        except sqlite3.Error as e:
            print(f"获取签到历史失败: {e}")
            raise
    
    def get_all_sign_records(self):
        """
        获取所有用户的签到记录（用于定时检测）
        :return: 签到记录列表，包含用户ID、签到日期、连续未签到天数
        """
        try:
            self.cursor.execute("""
                SELECT u.user_id, u.username, u.email, s.sign_date, s.consecutive_missed
                FROM users u
                LEFT JOIN sign_records s ON u.user_id = s.user_id
                WHERE s.sign_date = (SELECT MAX(sign_date) FROM sign_records WHERE user_id = u.user_id)
                OR s.sign_date IS NULL
            """)
            records = self.cursor.fetchall()
            return [{
                'user_id': record[0],
                'username': record[1],
                'email': record[2],
                'last_sign_date': record[3],
                'consecutive_missed': record[4] if record[4] is not None else 0
            } for record in records]
        except sqlite3.Error as e:
            print(f"获取所有签到记录失败: {e}")
            raise
    
    def get_consecutive_sign_days(self, user_id):
        """
        获取用户当前连续签到天数
        :param user_id: 用户ID
        :return: 连续签到天数
        """
        today = datetime.date.today()
        try:
            consecutive_days = 0
            current_date = today
            
            while True:
                self.cursor.execute(
                    "SELECT * FROM sign_records WHERE user_id = ? AND sign_date = ?",
                    (user_id, current_date)
                )
                if self.cursor.fetchone():
                    consecutive_days += 1
                    current_date -= datetime.timedelta(days=1)
                else:
                    break
            
            return consecutive_days
        except sqlite3.Error as e:
            print(f"获取连续签到天数失败: {e}")
            raise
    
    def get_longest_streak(self, user_id):
        """
        获取用户最长连续签到天数
        :param user_id: 用户ID
        :return: 最长连续签到天数
        """
        try:
            # 获取所有签到记录，按日期排序
            self.cursor.execute(
                "SELECT sign_date FROM sign_records WHERE user_id = ? ORDER BY sign_date ASC",
                (user_id,)
            )
            records = self.cursor.fetchall()
            
            if not records:
                return 0
            
            longest_streak = 1
            current_streak = 1
            previous_date = None
            
            for record in records:
                sign_date = datetime.datetime.strptime(record[0], '%Y-%m-%d').date()
                if previous_date:
                    # 检查是否连续
                    if (sign_date - previous_date).days == 1:
                        current_streak += 1
                        if current_streak > longest_streak:
                            longest_streak = current_streak
                    else:
                        current_streak = 1
                previous_date = sign_date
            
            return longest_streak
        except sqlite3.Error as e:
            print(f"获取最长连续签到天数失败: {e}")
            raise
    
    def close(self):
        """
        关闭数据库连接
        """
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

# 测试代码
if __name__ == "__main__":
    db = SignInDatabase()
    
    # 测试添加用户
    user_id = db.add_user("test_user", "test@example.com")
    print(f"添加用户ID: {user_id}")
    
    # 测试签到
    sign_id = db.add_sign_record(user_id)
    print(f"签到记录ID: {sign_id}")
    
    # 测试获取签到状态
    status = db.get_sign_status(user_id)
    print(f"今日签到状态: {status}")
    
    # 测试获取签到历史
    history = db.get_sign_history(user_id)
    print(f"签到历史: {history}")
    
    # 关闭数据库连接
    db.close()