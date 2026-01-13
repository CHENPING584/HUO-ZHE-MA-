import tkinter as tk
from tkinter import ttk, messagebox, font
from database import SignInDatabase
import datetime
import threading
import time
import sys
import os
import random

class SignInApp:
    def __init__(self, root):
        """
        初始化签到应用界面
        :param root: Tkinter根窗口
        """
        self.root = root
        self.db = SignInDatabase()
        self.current_user = None
        
        # 统一颜色主题（根据用户提供的设计要求）
        self.colors = {
            'primary': '#2E7D32',      # 主色（绿色）
            'primary_dark': '#1B5E20',  # 主色深色
            'primary_light': '#388E3C', # 主色浅色
            'secondary': '#f7f9fc',     # 次要色（浅灰，微质感）
            'text': '#333333',          # 主要文字色（深灰色）
            'text_light': '#666666',     # 次要文字色（中灰色）
            'border': '#E0E0E0',        # 边框色（浅灰色）
            'success': '#2E7D32',       # 成功色
            'warning': '#f6ad55',       # 警告色
            'error': '#fc8181',         # 错误色
            'background': '#f0f4f8',    # 背景色（柔和的浅蓝色）
            'card': '#ffffff',           # 卡片背景色
            'input_bg': '#FAFAFA',      # 输入框背景色
            'gradient_start': '#e8f5e8', # 渐变开始色（淡绿）
            'gradient_end': '#c8e6c9'    # 渐变结束色（浅绿）
        }
        
        # 设置窗口标题和大小（适配移动端和电脑端）
        self.root.title("死了吗")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 根据屏幕尺寸设置默认窗口大小
        if screen_width < 768:  # 移动端
            self.root.geometry("400x650")
            self.is_mobile = True
        else:  # 电脑端
            self.root.geometry("600x700")
            self.is_mobile = False
        
        self.root.resizable(True, True)
        
        # 设置窗口背景色
        self.root.configure(bg=self.colors['background'])
        
        # 根据屏幕尺寸调整全局字体大小
        if self.is_mobile:
            self.default_font = ("Segoe UI", 14)  # 移动端字体稍大，便于阅读
        else:
            self.default_font = ("Segoe UI", 12)  # 电脑端字体适中
        
        # 创建主框架，添加卡片效果
        self.main_frame = ttk.Frame(root, padding="0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带卡片效果的容器，根据屏幕尺寸调整
        self.card_frame = tk.Frame(self.main_frame, 
                                 bg=self.colors['card'],
                                 bd=0,
                                 relief="flat")
        
        # 根据屏幕尺寸调整卡片内边距
        if self.is_mobile:
            self.card_frame.configure(padx=20, pady=30)
        else:
            self.card_frame.configure(padx=40, pady=40)
        
        self.card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 添加阴影效果（通过叠加Frame实现）
        self.shadow_frame = tk.Frame(self.main_frame, 
                                   bg="#000000",
                                   bd=0,
                                   relief="flat")
        self.shadow_frame.place(x=15, y=15, relwidth=1, relheight=1, anchor=tk.NW)
        self.shadow_frame.lower()  # 置于底层
        self.card_frame.lift()  # 置于顶层
        
        # 设置主题样式
        self._setup_styles()
        
        # 创建界面组件
        self._create_user_info_section()
        self._create_sign_in_section()  # 取消注释，测试签到功能区
        # 注释掉统计功能区，简化界面
        # self._create_stats_section()  # 取消注释，测试统计功能区
        # 注释掉可能有问题的组件创建方法，先测试基本功能
        # self._create_history_section()
        
        # 刷新界面数据
        # self._refresh_sign_status()
        # self._refresh_history()
        # self._refresh_stats_cards()
    
    def _setup_styles(self):
        """
        设置自定义样式（根据用户提供的设计要求）
        """
        style = ttk.Style()
        
        # 设置主题（根据系统自动选择）
        if sys.platform.startswith('win'):
            style.theme_use('vista')  # Windows
        else:
            style.theme_use('clam')  # macOS/Linux
        
        # 自定义标签样式
        style.configure("Custom.TLabel",
                      font=('黑体', 14, 'bold'),
                      foreground=self.colors['text'])
        
        # 优化输入框样式（根据设计要求）
        style.configure("Custom.TEntry",
                      borderwidth=1,
                      relief="solid",
                      padding=(10, 0),
                      font=('黑体', 14, 'bold'),
                      foreground=self.colors['text'],
                      fieldbackground=self.colors['input_bg'],
                      bordercolor=self.colors['border'])
        
        # 设置输入框焦点样式
        style.map("Custom.TEntry",
                 bordercolor=[('focus', self.colors['primary']), ('!focus', self.colors['border'])],
                 highlightcolor=[('focus', self.colors['primary'])],
                 highlightthickness=[('focus', 1), ('!focus', 0)])
    
    def _create_user_info_section(self):
        """
        创建用户信息显示区（根据用户提供的设计要求，左右并排布局）
        """
        # 用户信息框架（简洁设计）
        user_frame = tk.Frame(self.card_frame, 
                            bg=self.colors['card'],
                            bd=0,
                            relief="flat",
                            padx=10,
                            pady=20)
        user_frame.pack(fill=tk.X, pady=(10, 20))
        
        # 标题
        if self.is_mobile:
            title_font = ('黑体', 24, 'bold')
        else:
            title_font = ('黑体', 28, 'bold')
        
        title_label = ttk.Label(user_frame, text="健康打卡", 
                               font=title_font,
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=(0, 30))
        
        # 输入框容器，根据设备类型选择布局
        inputs_container = tk.Frame(user_frame, bg=self.colors['card'])
        inputs_container.pack(fill=tk.X, pady=(0, 20))
        
        if self.is_mobile:
            # 移动端：上下垂直布局
            # 姓名输入区域
            name_container = tk.Frame(inputs_container, bg=self.colors['card'])
            name_container.pack(fill=tk.X, pady=(0, 15))
            
            # 姓名标签 - 字体大小设置为10磅
            name_label = ttk.Label(name_container, text="你的名字", 
                                  font=('黑体', 10, 'bold'),
                                  foreground=self.colors['text'])
            name_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))
            
            # 姓名输入框
            self.username_var = tk.StringVar()
            self.username_entry = ttk.Entry(
                name_container, 
                textvariable=self.username_var, 
                style="Custom.TEntry",
                width=30,
                justify=tk.LEFT
            )
            self.username_entry.pack(fill=tk.X, expand=True, ipady=8)  # 调整高度
            
            # 紧急联系人邮箱输入区域
            email_container = tk.Frame(inputs_container, bg=self.colors['card'])
            email_container.pack(fill=tk.X, pady=(0, 15))
            
            # 邮箱标签 - 字体大小设置为10磅
            email_label = ttk.Label(email_container, text="紧急联系人邮箱", 
                                   font=('黑体', 10, 'bold'),
                                   foreground=self.colors['text'])
            email_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))
            
            # 邮箱输入框
            self.email_var = tk.StringVar()
            self.email_entry = ttk.Entry(
                email_container, 
                textvariable=self.email_var, 
                style="Custom.TEntry",
                width=30,
                justify=tk.LEFT
            )
            self.email_entry.pack(fill=tk.X, expand=True, ipady=8)  # 调整高度
        else:
            # 电脑端：左右并排布局
            input_row = tk.Frame(inputs_container, bg=self.colors['card'])
            input_row.pack(fill=tk.X, pady=(0, 15))
            
            # 姓名输入区域
            name_container = tk.Frame(input_row, bg=self.colors['card'])
            name_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            # 姓名标签 - 字体大小设置为10磅
            name_label = ttk.Label(name_container, text="你的名字", 
                                  font=('黑体', 10, 'bold'),
                                  foreground=self.colors['text'])
            name_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))
            
            # 姓名输入框
            self.username_var = tk.StringVar()
            self.username_entry = ttk.Entry(
                name_container, 
                textvariable=self.username_var, 
                style="Custom.TEntry",
                justify=tk.LEFT
            )
            self.username_entry.pack(fill=tk.X, expand=True, ipady=8)  # 调整高度
            
            # 紧急联系人邮箱输入区域
            email_container = tk.Frame(input_row, bg=self.colors['card'])
            email_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            
            # 邮箱标签 - 字体大小设置为10磅
            email_label = ttk.Label(email_container, text="紧急联系人邮箱", 
                                   font=('黑体', 10, 'bold'),
                                   foreground=self.colors['text'])
            email_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))
            
            # 邮箱输入框
            self.email_var = tk.StringVar()
            self.email_entry = ttk.Entry(
                email_container, 
                textvariable=self.email_var, 
                style="Custom.TEntry",
                justify=tk.LEFT
            )
            self.email_entry.pack(fill=tk.X, expand=True, ipady=8)  # 调整高度
        
        # 添加提示文案（位于输入框下方、签到按钮上方）
        self.warning_label = ttk.Label(user_frame, 
                                       text="若连续两日未签到，系统将自动向您填写的紧急联系人邮箱发送提醒",
                                       font=('黑体', 12, 'bold'),
                                       foreground=self.colors['text_light'],
                                       wraplength=380,
                                       justify=tk.CENTER)
        self.warning_label.pack(pady=(20, 20))
        
        # 添加设置按钮，使用箭头形式表示"进入设置"
        settings_frame = tk.Frame(user_frame, bg=self.colors['card'])
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 创建弱化的设置按钮
        self.settings_button = tk.Canvas(
            settings_frame, 
            width=60, 
            height=60, 
            bg=self.colors['card'],
            highlightthickness=0
        )
        self.settings_button.pack(side=tk.RIGHT, padx=10)
        
        # 绘制箭头按钮
        self.settings_button.create_oval(0, 0, 60, 60, 
                                      fill=self.colors['secondary'], 
                                      outline="",
                                      width=0)
        self.settings_button.create_text(30, 30, 
                                      text=">",
                                      font=('黑体', 24, 'bold'),
                                      fill=self.colors['text_light'])
        
        # 绑定按钮点击事件
        self.settings_button.bind("<Button-1>", lambda e: self._save_user_info())
        
        # 添加状态提示标签
        self.status_label = ttk.Label(user_frame, 
                                     text="",
                                     font=('黑体', 14, 'bold'),
                                     foreground=self.colors['success'])
        self.status_label.pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
    
    def _toggle_save_switch(self, event):
        """
        切换保存开关状态
        """
        if not self.save_switch_state:
            # 先执行保存操作，只有成功后才切换开关状态
            if self._save_user_info():
                # 保存成功，切换到开启状态
                self.save_switch.coords(self.switch_slider, 37, 7, 53, 23)
                self.save_switch.itemconfig(self.switch_slider, fill=self.colors['primary'])
                self.save_switch_state = True
        else:
            # 切换到关闭状态
            self.save_switch.coords(self.switch_slider, 7, 7, 23, 23)
            self.save_switch.itemconfig(self.switch_slider, fill=self.colors['secondary'])
            self.save_switch_state = False
    
    def _create_sign_in_section(self):
        """
        创建签到功能区（根据用户提供的设计要求）
        """
        # 签到框架（无边框，简洁设计）
        sign_frame = tk.Frame(self.card_frame, 
                            bg=self.colors['card'],
                            padx=20,
                            pady=10)
        sign_frame.pack(fill=tk.BOTH, expand=True)
        
        # 签到按钮容器（居中显示，占据主要空间）
        button_container = tk.Frame(sign_frame, bg=self.colors['card'])
        button_container.pack(expand=True, pady=(0, 50))
        
        # 自定义圆形签到按钮（根据设备类型调整尺寸）
        if self.is_mobile:
            button_size = 180
        else:
            button_size = 220
            
        self.sign_button = tk.Canvas(
            button_container, 
            width=button_size, 
            height=button_size,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.sign_button.pack(pady=20)
        
        # 绘制圆形按钮
        self._draw_circle_button()
        
        # 绑定按钮事件
        self.sign_button.bind("<Button-1>", lambda e: self._handle_sign_in())
        self.sign_button.bind("<Enter>", lambda e: self._circle_button_hover(True))
        self.sign_button.bind("<Leave>", lambda e: self._circle_button_hover(False))
        
        # 删除隐私政策和用户协议链接
        # 删除底部黑色色块（通过简化设计实现）
    
    def _draw_circle_button(self):
        """
        绘制圆形签到按钮（根据用户提供的设计要求）
        """
        # 清空画布
        self.sign_button.delete("all")
        
        # 获取画布尺寸
        button_size = self.sign_button.winfo_width()
        center_x = button_size // 2
        center_y = button_size // 2
        
        # 1. 绘制圆形背景（纯绿色填充）
        self.sign_button.create_oval(0, 0, button_size, button_size, 
                                    fill=self.colors['primary'], 
                                    outline="",
                                    width=0)
        
        # 2. 绘制文字"今日签到"（居中显示，根据按钮大小调整字号）
        if button_size <= 180:
            text_font = ('黑体', 20, 'bold')
        else:
            text_font = ('黑体', 24, 'bold')
            
        self.sign_button.create_text(center_x, center_y, 
                                    text="今日签到",
                                    font=text_font,
                                    fill="white",
                                    justify=tk.CENTER)
    
    def _circle_button_hover(self, is_hover):
        """
        圆形按钮悬停效果（根据用户提供的设计要求）
        """
        # 清空画布
        self.sign_button.delete("all")
        
        # 获取画布尺寸
        button_size = self.sign_button.winfo_width()
        center_x = button_size // 2
        center_y = button_size // 2
        
        # 1. 绘制圆形背景（悬停时颜色变化）
        if is_hover:
            bg_color = self.colors['primary_dark']  # 深绿色
        else:
            bg_color = self.colors['primary']  # 主色绿色
        
        self.sign_button.create_oval(0, 0, button_size, button_size, 
                                    fill=bg_color, 
                                    outline="",
                                    width=0)
        
        # 2. 绘制文字"今日签到"（居中显示，根据按钮大小调整字号）
        if button_size <= 180:
            text_font = ('黑体', 20, 'bold')
        else:
            text_font = ('黑体', 24, 'bold')
            
        self.sign_button.create_text(center_x, center_y, 
                                    text="今日签到",
                                    font=text_font,
                                    fill="white",
                                    justify=tk.CENTER)
    
    def _draw_save_button(self):
        """
        绘制保存按钮（根据用户提供的设计要求）
        """
        # 清空画布
        self.save_button.delete("all")
        
        # 获取画布尺寸
        width = self.save_button.winfo_width()
        height = self.save_button.winfo_height()
        
        # 绘制圆角矩形背景（圆角6px，主题绿色填充，无描边）
        radius = 6
        # 绘制圆角矩形的四个角
        self.save_button.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, fill=self.colors['primary'], outline="", width=0)
        self.save_button.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, fill=self.colors['primary'], outline="", width=0)
        self.save_button.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, fill=self.colors['primary'], outline="", width=0)
        self.save_button.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, fill=self.colors['primary'], outline="", width=0)
        # 绘制圆角矩形的四条边
        self.save_button.create_rectangle(radius, 0, width-radius, height, fill=self.colors['primary'], outline="", width=0)
        self.save_button.create_rectangle(0, radius, width, height-radius, fill=self.colors['primary'], outline="", width=0)
        
        # 绘制文字"保存"（居中，16px微软雅黑，加粗）
        self.save_button.create_text(width/2, height/2, 
                                    text="保存",
                                    font=('微软雅黑', 16, 'bold'),
                                    fill="white")
    
    def _show_privacy_policy(self):
        """
        显示隐私政策和用户协议
        """
        messagebox.showinfo("隐私政策和用户协议", "感谢您使用每日签到提醒系统！\n\n隐私政策：\n1. 我们承诺保护您的个人信息安全\n2. 您的信息仅用于签到提醒服务\n3. 我们不会向第三方泄露您的信息\n\n用户协议：\n1. 请确保提供准确的紧急联系人邮箱\n2. 连续2日未签到将触发邮件通知\n3. 您可以随时修改或删除您的信息")
    
    def _create_stats_section(self):
        """
        创建数据统计卡片区域
        """
        # 数据统计卡片区域
        stats_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        stats_frame.pack(fill=tk.X, pady=(10, 10))
        
        # 创建两个数据统计卡片
        self._create_stats_cards(stats_frame)
    
    def _create_stats_cards(self, parent):
        """
        创建数据统计卡片
        :param parent: 父容器
        """
        # 创建卡片容器，使用Frame实现横向布局
        cards_container = tk.Frame(parent, bg=self.colors['background'])
        cards_container.pack(fill=tk.X, expand=True, padx=20)
        
        # 卡片宽度配置
        card_width = 160
        card_height = 100
        
        # 创建左侧卡片：连续签到天数
        self.consecutive_card = tk.Canvas(
            cards_container, 
            width=card_width, 
            height=card_height,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.consecutive_card.pack(side=tk.LEFT, padx=(0, 15), pady=10, expand=True)
        
        # 创建右侧卡片：最长连续签到天数
        self.longest_card = tk.Canvas(
            cards_container, 
            width=card_width, 
            height=card_height,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.longest_card.pack(side=tk.LEFT, padx=(15, 0), pady=10, expand=True)
        
        # 初始化卡片显示
        self._refresh_stats_cards()
    
    def _refresh_stats_cards(self):
        """
        刷新数据统计卡片内容
        """
        # 初始化数据
        consecutive_days = 0
        longest_streak = 0
        
        # 如果有当前用户，获取真实数据
        if self.current_user:
            try:
                consecutive_days = self.db.get_consecutive_sign_days(self.current_user["user_id"])
                longest_streak = self.db.get_longest_streak(self.current_user["user_id"])
            except Exception as e:
                print(f"刷新统计数据失败: {e}")
        
        # 绘制左侧卡片：连续签到天数
        self._draw_stats_card(
            canvas=self.consecutive_card,
            title="连续签到",
            value=str(consecutive_days),
            unit="天",
            icon_type="flame",
            value_color="#ef4444",  # 红色
            bg_color="#e0f2fe"      # 浅深蓝色
        )
        
        # 绘制右侧卡片：最长连续签到天数
        self._draw_stats_card(
            canvas=self.longest_card,
            title="最长连续签到",
            value=str(longest_streak),
            unit="天",
            icon_type="trophy",
            value_color="#f59e0b",  # 金色
            bg_color="#e0f2fe"      # 浅深蓝色
        )
    
    def _draw_stats_card(self, canvas, title, value, unit, icon_type, value_color, bg_color):
        """
        绘制单个统计卡片
        :param canvas: Canvas对象
        :param title: 卡片标题
        :param value: 卡片数值
        :param unit: 数值单位
        :param icon_type: 图标类型 (flame/trophy)
        :param value_color: 数值颜色
        :param bg_color: 卡片背景色
        """
        # 清空画布
        canvas.delete("all")
        
        # 获取画布尺寸
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # 绘制带圆角的卡片背景
        radius = 10
        
        # 创建背景圆角矩形（使用Canvas的create_oval和create_rectangle组合实现）
        canvas.create_rectangle(radius, 0, width-radius, height, fill=bg_color, outline="")
        canvas.create_rectangle(0, radius, width, height-radius, fill=bg_color, outline="")
        canvas.create_oval(0, 0, radius*2, radius*2, fill=bg_color, outline="")
        canvas.create_oval(width-radius*2, 0, width, radius*2, fill=bg_color, outline="")
        canvas.create_oval(0, height-radius*2, radius*2, height, fill=bg_color, outline="")
        canvas.create_oval(width-radius*2, height-radius*2, width, height, fill=bg_color, outline="")
        
        # 绘制阴影效果（右下角偏移）
        shadow_offset = 2
        canvas.create_rectangle(radius+shadow_offset, shadow_offset, width-radius, height+shadow_offset, 
                               fill="#000000", outline="", stipple="gray50")
        canvas.create_rectangle(shadow_offset, radius+shadow_offset, width+shadow_offset, height-radius, 
                               fill="#000000", outline="", stipple="gray50")
        canvas.create_oval(shadow_offset, shadow_offset, radius*2+shadow_offset, radius*2+shadow_offset, 
                          fill="#000000", outline="", stipple="gray50")
        canvas.create_oval(width-radius*2+shadow_offset, shadow_offset, width+shadow_offset, radius*2+shadow_offset, 
                          fill="#000000", outline="", stipple="gray50")
        canvas.create_oval(shadow_offset, height-radius*2+shadow_offset, radius*2+shadow_offset, height+shadow_offset, 
                          fill="#000000", outline="", stipple="gray50")
        canvas.create_oval(width-radius*2+shadow_offset, height-radius*2+shadow_offset, width+shadow_offset, height+shadow_offset, 
                          fill="#000000", outline="", stipple="gray50")
        
        # 绘制标题（优化文字显示）
        if "连续" in title:
            # 连续签到卡片标题
            title_text = "连续签到"
        else:
            # 普通签到卡片标题
            title_text = "签到"
        
        # 绘制主标题
        title_font = ("Segoe UI", 14, "bold")
        title_y = 25
        canvas.create_text(width/2, title_y, text=title_text, font=title_font, fill="#374151")
        
        # 绘制图标
        icon_y = 50
        if icon_type == "flame":
            # 绘制火焰图标（简化版）
            flame_points = [
                (width/2, icon_y),
                (width/2 - 12, icon_y + 20),
                (width/2 - 6, icon_y + 15),
                (width/2, icon_y + 24),
                (width/2 + 6, icon_y + 15),
                (width/2 + 12, icon_y + 20)
            ]
            canvas.create_polygon(flame_points, fill="#ef4444", outline="")
            
            # 绘制红色箭头
            canvas.create_polygon(width/2 - 10, 75, width/2, 85, width/2 + 10, 75, 
                               fill="#ef4444", outline="")
            
            # 绘制红色天字
            day_font = ("Segoe UI", 16, "bold")
            canvas.create_text(width/2, 95, text="天", font=day_font, fill="#ef4444")
        elif icon_type == "trophy":
            # 绘制奖杯图标（简化版）
            trophy_points = [
                (width/2, icon_y),
                (width/2 - 12, icon_y + 15),
                (width/2 - 8, icon_y + 15),
                (width/2 - 8, icon_y + 20),
                (width/2 + 8, icon_y + 20),
                (width/2 + 8, icon_y + 15),
                (width/2 + 12, icon_y + 15)
            ]
            canvas.create_polygon(trophy_points, fill="#f59e0b", outline="")
            canvas.create_rectangle(width/2 - 6, icon_y + 20, width/2 + 6, icon_y + 24, fill="#f59e0b", outline="")
            
            # 绘制黄色箭头
            canvas.create_polygon(width/2 - 10, 75, width/2, 85, width/2 + 10, 75, 
                               fill="#f59e0b", outline="")
            
            # 绘制黄色天字
            day_font = ("Segoe UI", 16, "bold")
            canvas.create_text(width/2, 95, text="天", font=day_font, fill="#f59e0b")
        
        # 绘制数值（增大字号，加粗）
        value_font = ("Segoe UI", 32, "bold")
        value_y = 70
        canvas.create_text(width/2, value_y, text=value, font=value_font, fill=value_color)
        
        # 不再单独绘制单位，因为天字已经通过图标下方的文字显示
    
    def _create_history_section(self):
        """
        创建签到历史记录区
        """
        # 历史记录框架
        history_frame = ttk.LabelFrame(self.main_frame, text="签到历史", padding="15")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建表格
        columns = ("date", "status")
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=columns, 
            show="headings",
            height=8,
            selectmode="browse"
        )
        
        # 设置列标题
        self.history_tree.heading("date", text="日期", anchor=tk.CENTER)
        self.history_tree.heading("status", text="状态", anchor=tk.CENTER)
        
        # 设置列宽
        self.history_tree.column("date", width=180, anchor=tk.CENTER, minwidth=150)
        self.history_tree.column("status", width=180, anchor=tk.CENTER, minwidth=120)
        
        # 设置表格样式
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(self.default_font[0], 14, "bold"))
        style.configure("Treeview", 
                       font=(self.default_font[0], 14),
                       rowheight=35)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        # 布局表格和滚动条
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, ipady=10)
    
    def _handle_sign_in(self):
        """
        处理签到操作，添加粒子爆炸动画
        """
        # 检查用户信息是否已保存，如果没有保存，自动保存
        if not self.current_user:
            if self._save_user_info():
                # 保存成功，继续执行签到
                pass
            else:
                # 保存失败，提示用户
                messagebox.showwarning("警告", "请先填写有效的用户信息！")
                return
        
        try:
            # 执行签到
            sign_result = self.db.add_sign_record(self.current_user["user_id"])
            if sign_result:
                # 显示成功信息
                self._show_sign_success()
                # 播放粒子爆炸动画
                self._play_particle_animation()
                self._refresh_sign_status()
                self._refresh_history()
                self._refresh_stats_cards()
            else:
                messagebox.showinfo("提示", "您今日已签到！")
        except Exception as e:
            messagebox.showerror("错误", f"签到失败：{str(e)}")
    
    def _show_sign_success(self):
        """
        显示签到成功提示
        """
        # 创建临时成功提示窗口
        success_window = tk.Toplevel(self.root)
        success_window.title("")
        success_window.geometry("200x100")
        success_window.configure(bg=self.colors['background'])
        success_window.overrideredirect(True)  # 隐藏标题栏
        
        # 居中显示
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 100
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
        success_window.geometry(f"200x100+{x}+{y}")
        
        # 绘制成功提示
        success_canvas = tk.Canvas(success_window, width=200, height=100, bg=self.colors['background'], highlightthickness=0)
        success_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绘制成功图标
        success_canvas.create_oval(75, 20, 125, 70, fill=self.colors['success'], outline="")
        success_canvas.create_text(100, 48, text="✓", font=("Arial", 30, "bold"), fill="white")
        
        # 自动关闭窗口
        success_window.after(1500, success_window.destroy)
    
    def _play_particle_animation(self):
        """
        播放粒子爆炸动画
        """
        # 创建粒子画布
        particle_canvas = tk.Canvas(self.main_frame, 
                                   width=400,
                                   height=650,
                                   bg=self.colors['background'],
                                   highlightthickness=0)
        particle_canvas.place(x=0, y=0)
        
        # 生成粒子
        particles = []
        for i in range(30):
            # 随机粒子属性
            x = 200
            y = 325
            vx = (2 * (i % 2) - 1) * (10 + i % 5)
            vy = -10 - i % 10
            color = f"#{random.randint(112, 144):02x}{random.randint(193, 225):02x}{random.randint(179, 211):02x}"
            size = 2 + i % 3
            particles.append((x, y, vx, vy, color, size))
        
        # 绘制和更新粒子
        def update_particles():
            nonlocal particles
            particle_canvas.delete("all")
            
            new_particles = []
            for (x, y, vx, vy, color, size) in particles:
                # 更新粒子位置
                new_x = x + vx * 0.1
                new_y = y + vy * 0.1
                new_vy = vy + 1.5  # 重力
                
                # 如果粒子还在画布内，继续显示
                if 0 < new_x < 400 and 0 < new_y < 650:
                    # 绘制粒子
                    particle_canvas.create_oval(new_x - size, new_y - size, 
                                              new_x + size, new_y + size, 
                                              fill=color, outline="")
                    new_particles.append((new_x, new_y, vx, new_vy, color, size))
            
            particles = new_particles
            if particles:
                particle_canvas.after(30, update_particles)
            else:
                particle_canvas.destroy()
        
        # 启动粒子动画
        update_particles()
    
    def _blend_colors(self, color1, color2, alpha):
        """
        混合两种颜色
        """
        # 移除#号并转换为RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # 混合颜色
        r = int(r1 * (1 - alpha) + r2 * alpha)
        g = int(g1 * (1 - alpha) + g2 * alpha)
        b = int(b1 * (1 - alpha) + b2 * alpha)
        
        # 转换回十六进制
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _save_user_info(self):
        """
        保存用户信息
        :return: 保存成功返回True，失败返回False
        """
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        
        if not username:
            messagebox.showwarning("警告", "用户名不能为空！")
            return False
        
        if not email:
            messagebox.showwarning("警告", "邮箱不能为空！")
            return False
        
        # 验证邮箱格式（如果提供了邮箱）
        if email and ("@" not in email or "." not in email):
            messagebox.showwarning("警告", "请输入有效的邮箱地址！")
            return False
        
        try:
            # 检查用户是否已存在
            existing_user = self.db.get_user_by_username(username)
            if existing_user:
                # 更新用户信息
                success = self.db.update_user(existing_user["user_id"], email=email)
                if success:
                    self.current_user = existing_user
                    # 显示状态提示
                    self.status_label.config(text="已记住你的信息")
                    # 3秒后自动隐藏状态提示
                    self.root.after(3000, lambda: self.status_label.config(text=""))
                    self._refresh_sign_status()
                    self._refresh_history()
                    self._refresh_stats_cards()
                    return True
                else:
                    messagebox.showerror("错误", "用户信息更新失败！")
                    return False
            else:
                # 添加新用户
                user_id = self.db.add_user(username, email)
                if user_id:
                    self.current_user = self.db.get_user_by_id(user_id)
                    # 显示状态提示
                    self.status_label.config(text="已记住你的信息")
                    # 3秒后自动隐藏状态提示
                    self.root.after(3000, lambda: self.status_label.config(text=""))
                    self._refresh_sign_status()
                    self._refresh_history()
                    self._refresh_stats_cards()
                    return True
                else:
                    messagebox.showerror("错误", "用户名或邮箱已存在！")
                    return False
        except Exception as e:
            messagebox.showerror("错误", f"保存用户信息失败：{str(e)}")
            return False
    
    def _refresh_sign_status(self):
        """
        刷新签到状态显示
        """
        if not self.current_user:
            return
        
        try:
            # 获取今日签到状态
            is_signed = self.db.get_sign_status(self.current_user["user_id"])
            # 签到按钮状态已经在按钮交互中处理，此处不需要额外处理
        except Exception as e:
            messagebox.showerror("错误", f"刷新签到状态失败：{str(e)}")
    
    def _refresh_history(self):
        """
        刷新签到历史记录
        """
        # 清空现有记录
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if not self.current_user:
            return
        
        try:
            # 获取签到历史
            history = self.db.get_sign_history(self.current_user["user_id"], limit=30)
            
            # 添加到表格
            for record in history:
                date = record["sign_date"]
                if record["consecutive_missed"] == 0:
                    status = "已签到"
                    status_color = "green"
                else:
                    status = f"未签到({record['consecutive_missed']}天)"
                    status_color = "red"
                
                # 插入记录
                item_id = self.history_tree.insert("", tk.END, values=(date, status))
                # 设置行颜色
                self.history_tree.tag_configure(f"status_{item_id}", foreground=status_color)
                self.history_tree.item(item_id, tags=(f"status_{item_id}",))
        except Exception as e:
            messagebox.showerror("错误", f"刷新签到历史失败：{str(e)}")
    
    def __del__(self):
        """
        析构函数，关闭数据库连接
        """
        if hasattr(self, 'db'):
            self.db.close()

# 添加简单的主函数，用于直接测试GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SignInApp(root)
    root.mainloop()