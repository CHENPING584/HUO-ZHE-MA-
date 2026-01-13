import schedule
import time
import threading
from database import SignInDatabase
from email_reminder import EmailReminder
import datetime
import logging

# 配置日志
logging.basicConfig(
    filename='sign_in_reminder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class SignInScheduler:
    def __init__(self, email_sender=None, email_password=None, smtp_server=None, smtp_port=None):
        """
        初始化定时任务调度器
        :param email_sender: 发件人邮箱，用于发送提醒邮件
        :param email_password: 发件人邮箱授权码
        :param smtp_server: SMTP服务器地址
        :param smtp_port: SMTP服务器端口
        """
        self.db = SignInDatabase()
        self.email_sender = None
        
        # 初始化邮件发送器（如果提供了邮箱配置）
        if email_sender and email_password:
            try:
                # 处理端口转换
                port = int(smtp_port) if smtp_port else None
                self.email_sender = EmailReminder(email_sender, email_password, smtp_server, port)
                logging.info("邮件发送器初始化成功")
            except Exception as e:
                logging.error(f"邮件发送器初始化失败: {e}")
                self.email_sender = None
        
        self.is_running = False
        self.scheduler_thread = None
    
    def _check_sign_status(self):
        """
        检查所有用户的签到状态，发送提醒邮件
        """
        logging.info("开始执行签到状态检查任务")
        
        try:
            # 获取所有用户的最新签到记录
            all_users = self.db.get_all_sign_records()
            today = datetime.date.today()
            
            for user in all_users:
                try:
                    user_id = user['user_id']
                    username = user['username']
                    email = user['email']
                    last_sign_date = user['last_sign_date']
                    consecutive_missed = user['consecutive_missed']
                    
                    # 计算连续未签到天数
                    if last_sign_date:
                        # 转换为日期对象
                        last_sign = datetime.datetime.strptime(last_sign_date, '%Y-%m-%d').date()
                        days_diff = (today - last_sign).days
                        
                        # 如果最后签到日期不是今天，且不是昨天，更新连续未签到天数
                        if days_diff > 1:
                            consecutive_missed = days_diff - 1
                    else:
                        # 从未签到过
                        consecutive_missed = 0
                    
                    logging.info(f"检查用户: {username} (ID: {user_id})，最后签到日期: {last_sign_date}，连续未签到天数: {consecutive_missed}")
                    
                    # 如果连续2天未签到，发送提醒
                    if consecutive_missed >= 2:
                        # 检查用户是否有邮箱
                        if email:
                            # 检查邮件发送器是否已初始化
                            if self.email_sender:
                                self._send_reminder_email(email, username, consecutive_missed)
                                logging.info(f"已发送提醒邮件给用户: {username} (ID: {user_id})")
                            else:
                                logging.info(f"邮件发送器未初始化，跳过给用户 {username} (ID: {user_id}) 的邮件提醒")
                        else:
                            logging.info(f"用户 {username} (ID: {user_id}) 没有配置邮箱，无法发送提醒")
                        
                except Exception as e:
                    logging.error(f"处理用户 {user['username']} 时出错: {e}")
                    continue
            
            logging.info("签到状态检查任务执行完成")
            
        except Exception as e:
            logging.error(f"执行签到状态检查任务时出错: {e}")
    
    def _send_reminder_email(self, recipient_email: str, username: str, consecutive_days: int) -> None:
        """
        发送提醒邮件
        :param recipient_email: 收件人邮箱
        :param username: 用户名
        :param consecutive_days: 连续未签到天数
        """
        if not self.email_sender:
            logging.error("邮件发送器未初始化，无法发送提醒邮件")
            return
        
        subject = "【签到提醒】您已连续多日未签到"
        content = f"""亲爱的 {username}：

您已连续 {consecutive_days} 天未签到，请及时登录签到系统完成签到。

签到系统地址：桌面应用

祝您生活愉快！

--
每日签到提醒系统
"""
        
        try:
            result = self.email_sender.send_email(recipient_email, subject, content)
            if result['success']:
                logging.info(f"邮件发送成功: {recipient_email}")
            else:
                logging.error(f"邮件发送失败: {recipient_email}，原因: {result['message']}")
        except Exception as e:
            logging.error(f"发送邮件时出错: {e}")
    
    def start_scheduler(self):
        """
        启动定时任务
        """
        if self.is_running:
            logging.info("定时任务已在运行中")
            return
        
        try:
            # 设置每天凌晨1点执行任务
            schedule.every().day.at("01:00").do(self._check_sign_status)
            logging.info("定时任务已设置为每天凌晨1点执行")
            
            # 立即执行一次检查（用于测试）
            # self._check_sign_status()
            
            self.is_running = True
            
            # 创建并启动调度线程
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logging.info("定时任务调度线程已启动")
            
        except Exception as e:
            logging.error(f"启动定时任务失败: {e}")
            self.is_running = False
    
    def _run_scheduler(self):
        """
        运行调度器的线程函数
        """
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次是否有任务需要执行
            except Exception as e:
                logging.error(f"调度器运行出错: {e}")
                time.sleep(60)  # 出错后暂停一分钟再继续
    
    def stop_scheduler(self):
        """
        停止定时任务
        """
        if not self.is_running:
            logging.info("定时任务未在运行")
            return
        
        self.is_running = False
        
        # 等待调度线程结束
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logging.info("定时任务已停止")
    
    def manual_check(self):
        """
        手动触发一次签到状态检查
        """
        logging.info("手动触发签到状态检查")
        self._check_sign_status()

# 测试代码
if __name__ == "__main__":
    # 测试定时任务功能
    # 注意：请替换为您自己的邮箱和授权码
    test_scheduler = SignInScheduler(
        email_sender="your_email@qq.com",  # 请替换为您的发件人邮箱
        email_password="your_authorization_code"  # 请替换为您的授权码
    )
    
    print("启动定时任务测试...")
    test_scheduler.start_scheduler()
    
    # 手动触发一次检查
    test_scheduler.manual_check()
    
    print("定时任务已启动，将在每天凌晨1点执行检查")
    print("按Enter键停止测试...")
    input()
    
    test_scheduler.stop_scheduler()
    print("定时任务测试结束")