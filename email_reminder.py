import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

class EmailReminder:
    def __init__(self, sender_email, sender_password, smtp_server=None, smtp_port=None):
        """
        初始化邮件发送器
        :param sender_email: 发件人邮箱
        :param sender_password: 发件人邮箱授权码（注意：不是登录密码，需要在邮箱设置中开启SMTP服务并获取授权码）
        :param smtp_server: SMTP服务器地址，默认根据邮箱域名自动选择
        :param smtp_port: SMTP服务器端口，默认根据邮箱域名自动选择
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # 根据邮箱域名自动选择SMTP服务器和端口
        if not smtp_server or not smtp_port:
            smtp_info = self._get_smtp_info(sender_email)
            self.smtp_server = smtp_info['server']
            self.smtp_port = smtp_info['port']
        else:
            self.smtp_server = smtp_server
            self.smtp_port = smtp_port
    
    def _get_smtp_info(self, email):
        """
        根据邮箱域名获取对应的SMTP服务器信息
        :param email: 邮箱地址
        :return: 包含SMTP服务器地址和端口的字典
        """
        domain = email.split('@')[-1].lower()
        smtp_config = {
            'qq.com': {'server': 'smtp.qq.com', 'port': 465},
            '163.com': {'server': 'smtp.163.com', 'port': 465},
            '126.com': {'server': 'smtp.126.com', 'port': 465},
            'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
            'outlook.com': {'server': 'smtp.office365.com', 'port': 587}
        }
        
        if domain in smtp_config:
            return smtp_config[domain]
        else:
            # 默认配置，使用QQ邮箱的SMTP服务器
            return {'server': 'smtp.qq.com', 'port': 465}
    
    def send_email(self, recipient_email, subject, content):
        """
        发送邮件
        :param recipient_email: 收件人邮箱
        :param subject: 邮件标题
        :param content: 邮件内容
        :return: 发送结果字典，包含success（布尔值）和message（字符串）
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = Header(self.sender_email, 'utf-8')
            msg['To'] = Header(recipient_email, 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送邮件
            server = None
            try:
                # 根据端口选择加密方式
                if self.smtp_port == 465:
                    # 使用SSL加密
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
                else:
                    # 使用TLS加密
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                    server.starttls()
                
                # 登录邮箱
                server.login(self.sender_email, self.sender_password)
                
                # 发送邮件
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
                
                return {
                    'success': True,
                    'message': f"邮件发送成功！收件人：{recipient_email}"
                }
            finally:
                if server:
                    server.quit()
        
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': "邮件发送失败：授权码错误，请检查发件人邮箱授权码是否正确"
            }
        except smtplib.SMTPConnectError:
            return {
                'success': False,
                'message': "邮件发送失败：无法连接到SMTP服务器，请检查网络连接或SMTP服务器配置"
            }
        except smtplib.SMTPTimeoutError:
            return {
                'success': False,
                'message': "邮件发送失败：连接超时，请检查网络连接"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"邮件发送失败：{str(e)}"
            }

# 邮件配置教程
"""
邮件配置教程：

1. 开启SMTP服务并获取授权码：
   - QQ邮箱：
     1. 登录QQ邮箱网页版
     2. 点击右上角"设置" -> "账户"
     3. 下滑找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
     4. 开启"SMTP服务"
     5. 点击"生成授权码"，按照提示操作获取16位授权码
   
   - 163邮箱：
     1. 登录163邮箱网页版
     2. 点击右上角"设置" -> "POP3/SMTP/IMAP"
     3. 开启"SMTP服务"
     4. 设置客户端授权密码，保存后记住该密码

2. 配置邮件发送参数：
   在主程序中，需要实例化EmailReminder类，并传入以下参数：
   - sender_email: 发件人邮箱地址（如：your_email@qq.com）
   - sender_password: 刚才获取的授权码（如：xxxxxxxxxxxxxxxx）

3. 示例代码：
   from email_reminder import EmailReminder
   
   # 初始化邮件发送器
   email_sender = EmailReminder(
       sender_email="your_email@qq.com",
       sender_password="your_authorization_code"
   )
   
   # 发送邮件
   result = email_sender.send_email(
       recipient_email="recipient@example.com",
       subject="签到提醒",
       content="您已连续2天未签到，请及时签到！"
   )
   
   print(result)
"""

# 测试代码
if __name__ == "__main__":
    # 测试邮件发送功能
    # 使用config.ini中的配置
    import configparser
    
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    sender_email = config.get('Email', 'sender_email')
    sender_password = config.get('Email', 'sender_password')
    
    test_sender = EmailReminder(
        sender_email=sender_email,
        sender_password=sender_password
    )
    
    test_result = test_sender.send_email(
        recipient_email=sender_email,  # 发送给自己测试
        subject="签到提醒测试",
        content="这是一封签到提醒测试邮件，无需回复。\n发送时间：" + time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    print(f"邮件发送测试结果：{test_result}")