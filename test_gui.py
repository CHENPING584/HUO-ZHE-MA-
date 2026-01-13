import tkinter as tk
from tkinter import ttk, messagebox, font

# 简化版GUI测试，不连接数据库
class SimpleSignInApp:
    def __init__(self, root):
        # 统一颜色主题 - 背景设为图片中的浅蓝色，主色改为Kelly Green
        self.colors = {
            'primary': '#4CBB17',      # 主色（Kelly Green）
            'primary_dark': '#3A9E0F',  # 主色深色（深Kelly Green）
            'primary_light': '#66CD00', # 主色浅色（浅Kelly Green）
            'secondary': '#f7f9fc',     # 次要色（浅灰，微质感）
            'text': '#333333',          # 主要文字色（深灰色）
            'text_light': '#666666',     # 次要文字色（中灰色）
            'border': '#E0E0E0',        # 边框色（浅灰色）
            'success': '#4CBB17',       # 成功色（Kelly Green）
            'warning': '#f6ad55',       # 警告色
            'error': '#fc8181',         # 错误色
            'background': '#E0F7FA',    # 背景色（图片中的浅蓝色）
            'card': '#E0F7FA',           # 卡片背景色（与背景一致）
            'input_bg': '#E0F7FA',       # 输入框背景色（与背景一致）
            'gradient_start': '#E0F7FA', # 渐变开始色（与背景一致）
            'gradient_end': '#B2EBF2'    # 渐变结束色（稍深的浅蓝色）
        }
        
        # 设置窗口标题和大小
        self.root = root
        self.root.title("健康打卡")
        self.root.geometry("400x650")  # 固定尺寸用于测试
        self.is_mobile = True  # 固定为移动端模式用于测试
        
        self.root.resizable(True, True)
        self.root.configure(bg=self.colors['background'])  # 图片中的浅蓝色背景
        
        # 设置全局字体
        self.default_font = ("微软雅黑", 14)
        
        # 创建主框架 - 移除卡片效果，使用纯净白色背景
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建容器 - 移除卡片效果，使用纯净白色背景
        self.card_frame = tk.Frame(self.main_frame, 
                                 bg=self.colors['card'],
                                 bd=0,
                                 relief="flat",
                                 padx=10,
                                 pady=10)
        self.card_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置主题样式
        self._setup_styles()
        
        # 创建界面组件
        self._create_user_info_section()
        self._create_sign_in_section()
    
    def _setup_styles(self):
        """
        设置自定义样式 - 统一使用微软雅黑字体，去除灰色底纹
        """
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('vista')
        
        # 重置标签样式，去除背景色设置
        style.configure("TLabel",
                      font=('黑体', 12, 'bold'),
                      foreground=self.colors['text'])
        
        # 重置自定义标签样式，去除背景色
        style.configure("Custom.TLabel",
                      font=('黑体', 12, 'bold'),
                      foreground=self.colors['text'])
        
        # 重置输入框样式为横线样式
        style.configure("TEntry",
                      borderwidth=0,
                      relief="flat",
                      padding=(0, 5),  # 上下内边距
                      font=('黑体', 12, 'bold'),
                      foreground=self.colors['text'],
                      fieldbackground=self.colors['card'],
                      bordercolor=self.colors['border'])
        
        # 重置自定义输入框样式为横线样式
        style.configure("Custom.TEntry",
                      borderwidth=0,
                      relief="flat",
                      padding=(0, 5),  # 上下内边距
                      font=('黑体', 12, 'bold'),
                      foreground=self.colors['text'],
                      fieldbackground=self.colors['card'],
                      bordercolor=self.colors['border'])
        
        # 简化输入框样式，移除自定义layout
        # 使用更简单的方法创建横线效果
        
        # 设置输入框焦点样式
        style.map("Custom.TEntry",
                 fieldbackground=[('focus', self.colors['card']), ('!focus', self.colors['card'])],
                 bordercolor=[('focus', self.colors['primary']), ('!focus', self.colors['border'])],
                 highlightcolor=[('focus', self.colors['primary'])],
                 highlightthickness=[('focus', 0), ('!focus', 0)])
    
    def _create_user_info_section(self):
        """
        创建用户信息显示区
        """
        # 用户信息框架 - 减少边距，整体上移
        user_frame = tk.Frame(self.card_frame, 
                            bg=self.colors['card'],
                            bd=0,
                            relief="flat",
                            padx=10,
                            pady=2)
        user_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 输入框容器，根据设备类型选择布局
        inputs_container = tk.Frame(user_frame, bg=self.colors['card'])
        inputs_container.pack(fill=tk.X, pady=(0, 0))
        
        if self.is_mobile:
            # 移动端：上下垂直布局
            # 姓名输入区域 - 减少间距
            name_container = tk.Frame(inputs_container, bg=self.colors['card'])
            name_container.pack(fill=tk.X, pady=(0, 5))
            
            # 姓名标签 - 字体大小设置为10磅
            name_label = tk.Label(name_container, text="你的名字", 
                                  font=('黑体', 10, 'bold'),
                                  foreground=self.colors['text'],
                                  bg=self.colors['card'])  # 明确设置背景色与容器一致
            name_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 2))
            
            # 姓名输入框 - 使用微软雅黑字体，下方添加横线
            self.username_var = tk.StringVar()
            self.username_entry = ttk.Entry(
                name_container, 
                textvariable=self.username_var, 
                font=('黑体', 12, 'bold'),
                width=25,
                justify=tk.LEFT,
                style="Custom.TEntry"  # 使用自定义样式
            )
            self.username_entry.pack(fill=tk.X, expand=True, ipady=0)
            
            # 添加底部横线
            username_underline = tk.Frame(name_container, height=1, bg=self.colors['border'])
            username_underline.pack(fill=tk.X, expand=True)
            
            # 紧急联系人邮箱输入区域
            email_container = tk.Frame(inputs_container, bg=self.colors['card'])
            email_container.pack(fill=tk.X)
            
            # 邮箱标签 - 字体大小设置为10磅
            email_label = tk.Label(email_container, text="紧急联系人邮箱", 
                                   font=('黑体', 10, 'bold'),
                                   foreground=self.colors['text'],
                                   bg=self.colors['card'])  # 明确设置背景色与容器一致
            email_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 2))
            
            # 邮箱输入框 - 使用微软雅黑字体，下方添加横线
            self.email_var = tk.StringVar()
            self.email_entry = ttk.Entry(
                email_container, 
                textvariable=self.email_var, 
                font=('黑体', 12, 'bold'),
                width=25,
                justify=tk.LEFT,
                style="Custom.TEntry"  # 使用自定义样式
            )
            self.email_entry.pack(fill=tk.X, expand=True, ipady=0)
            
            # 添加底部横线
            email_underline = tk.Frame(email_container, height=1, bg=self.colors['border'])
            email_underline.pack(fill=tk.X, expand=True)
        else:
            # 电脑端：左右并排布局
            # 创建水平布局容器
            horizontal_container = tk.Frame(inputs_container, bg=self.colors['card'])
            horizontal_container.pack(fill=tk.X, expand=True)
            
            # 姓名输入区域 - 左侧
            name_container = tk.Frame(horizontal_container, bg=self.colors['card'])
            name_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            # 姓名标签 - 字体大小设置为10磅
            name_label = tk.Label(name_container, text="你的名字", 
                                  font=('黑体', 10, 'bold'),
                                  foreground=self.colors['text'],
                                  bg=self.colors['card'])  # 明确设置背景色与容器一致
            name_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 2))
            
            # 姓名输入框 - 使用微软雅黑字体，下方添加横线
            self.username_var = tk.StringVar()
            self.username_entry = ttk.Entry(
                name_container, 
                textvariable=self.username_var, 
                font=('黑体', 12, 'bold'),
                justify=tk.LEFT,
                style="Custom.TEntry"  # 使用自定义样式
            )
            self.username_entry.pack(fill=tk.X, expand=True, ipady=0)
            
            # 添加底部横线
            username_underline = tk.Frame(name_container, height=1, bg=self.colors['border'])
            username_underline.pack(fill=tk.X, expand=True)
            
            # 紧急联系人邮箱输入区域 - 右侧
            email_container = tk.Frame(horizontal_container, bg=self.colors['card'])
            email_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            
            # 邮箱标签 - 字体大小设置为10磅
            email_label = tk.Label(email_container, text="紧急联系人邮箱", 
                                   font=('黑体', 10, 'bold'),
                                   foreground=self.colors['text'],
                                   bg=self.colors['card'])  # 明确设置背景色与容器一致
            email_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 2))
            
            # 邮箱输入框 - 使用微软雅黑字体，下方添加横线
            self.email_var = tk.StringVar()
            self.email_entry = ttk.Entry(
                email_container, 
                textvariable=self.email_var, 
                font=('黑体', 12, 'bold'),
                justify=tk.LEFT,
                style="Custom.TEntry"  # 使用自定义样式
            )
            self.email_entry.pack(fill=tk.X, expand=True, ipady=0)
            
            # 添加底部横线
            email_underline = tk.Frame(email_container, height=1, bg=self.colors['border'])
            email_underline.pack(fill=tk.X, expand=True)
        
        # 添加设置按钮，使用箭头形式表示"进入设置"
        settings_frame = tk.Frame(user_frame, bg=self.colors['card'])
        settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 创建弱化的设置按钮
        self.settings_button = tk.Canvas(
            settings_frame, 
            width=40, 
            height=40, 
            bg=self.colors['card'],
            highlightthickness=0
        )
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        # 绘制箭头按钮 - 使用微软雅黑字体
        self.settings_button.create_oval(0, 0, 40, 40, 
                                      fill=self.colors['secondary'], 
                                      outline="",
                                      width=0)
        self.settings_button.create_text(20, 20, 
                                      text=">",
                                      font=('黑体', 16, 'bold'),
                                      fill=self.colors['text_light'])
        
        # 绑定按钮点击事件
        self.settings_button.bind("<Button-1>", lambda e: self._save_user_info())
        
        # 添加状态提示标签 - 使用tk.Label而非ttk.Label，避免默认样式问题
        self.status_label = tk.Label(user_frame, 
                                     text="",
                                     font=('黑体', 14, 'bold'),
                                     foreground=self.colors['success'],
                                     bg=self.colors['card'])  # 明确设置背景色与容器一致
        self.status_label.pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
    
    def _create_sign_in_section(self):
        """
        创建签到功能区
        """
        # 签到框架 - 减少边距，整体上移
        sign_frame = tk.Frame(self.card_frame, 
                            bg=self.colors['card'],
                            padx=10,
                            pady=0)
        sign_frame.pack(fill=tk.BOTH, expand=True)
        
        # 签到按钮容器（居中显示，占据主要空间）
        button_container = tk.Frame(sign_frame, bg=self.colors['card'])
        button_container.pack(expand=True, pady=(0, 0))
        
        # 添加签到状态变量
        self.is_signed_in = False
        
        # 自定义圆形签到按钮（根据设备类型调整尺寸）
        if self.is_mobile:
            self.button_size = 180  # 移动端按钮尺寸
        else:
            self.button_size = 220  # 电脑端按钮尺寸
            
        self.sign_button = tk.Canvas(
            button_container, 
            width=self.button_size, 
            height=self.button_size,
            bg=self.colors['card'],
            highlightthickness=0
        )
        # 尝试开启抗锯齿 - 在Tkinter中，抗锯齿主要依赖于底层平台和Tk版本
        # 对于文字，Tkinter通常会自动处理抗锯齿
        # 对于图形，我们可以通过平滑绘制来模拟抗锯齿效果
        self.sign_button.pack(pady=(0, 5))  # 进一步减小顶部间距，将按钮上移
        
        # 绘制圆形按钮
        self._draw_circle_button()
        
        # 绑定按钮事件
        self.sign_button.bind("<Button-1>", lambda e: self._handle_sign_in())
        self.sign_button.bind("<Enter>", lambda e: self._circle_button_hover(True))
        self.sign_button.bind("<Leave>", lambda e: self._circle_button_hover(False))
        
        # 添加数据统计卡片区域
        cards_frame = tk.Frame(sign_frame, bg=self.colors['card'])
        cards_frame.pack(fill=tk.X, expand=True, pady=(10, 15))
        
        # 创建连续打卡卡片
        consecutive_card = tk.Frame(cards_frame, 
                                  bg=self.colors['card'],
                                  bd=1,
                                  relief="solid",
                                  padx=15,
                                  pady=10)  # 减小内部padding，降低卡片高度
        consecutive_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 连续打卡卡片标题
        consecutive_title = tk.Label(consecutive_card, 
                                    text="连续打卡",
                                    font=('黑体', 12, 'bold'),
                                    foreground=self.colors['text'],
                                    bg=self.colors['card'])
        consecutive_title.pack(side=tk.TOP, anchor=tk.CENTER, pady=(0, 5))
        
        # 连续打卡天数
        consecutive_days = tk.Label(consecutive_card, 
                                   text="5",
                                   font=('黑体', 24, 'bold'),
                                   foreground=self.colors['primary'],
                                   bg=self.colors['card'])
        consecutive_days.pack(side=tk.TOP, anchor=tk.CENTER)
        
        # 连续打卡单位
        consecutive_unit = tk.Label(consecutive_card, 
                                  text="天",
                                  font=('黑体', 12, 'bold'),
                                  foreground=self.colors['text_light'],
                                  bg=self.colors['card'])
        consecutive_unit.pack(side=tk.TOP, anchor=tk.CENTER)
        
        # 创建最长连续打卡卡片
        longest_card = tk.Frame(cards_frame, 
                               bg=self.colors['card'],
                               bd=1,
                               relief="solid",
                               padx=15,
                               pady=10)  # 减小内部padding，降低卡片高度
        longest_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 最长连续打卡卡片标题
        longest_title = tk.Label(longest_card, 
                               text="最长连续",
                               font=('黑体', 12, 'bold'),
                               foreground=self.colors['text'],
                               bg=self.colors['card'])
        longest_title.pack(side=tk.TOP, anchor=tk.CENTER, pady=(0, 5))
        
        # 最长连续打卡天数
        longest_days = tk.Label(longest_card, 
                              text="12",
                              font=('黑体', 24, 'bold'),
                              foreground=self.colors['primary'],
                              bg=self.colors['card'])
        longest_days.pack(side=tk.TOP, anchor=tk.CENTER)
        
        # 最长连续打卡单位
        longest_unit = tk.Label(longest_card, 
                             text="天",
                             font=('黑体', 12, 'bold'),
                             foreground=self.colors['text_light'],
                             bg=self.colors['card'])
        longest_unit.pack(side=tk.TOP, anchor=tk.CENTER)
        
        # 添加提示文案（位于卡片下方）- 使用tk.Label而非ttk.Label，避免默认样式问题
        self.warning_label = tk.Label(sign_frame, 
                                       text="若连续两日未签到，系统将自动向您填写的紧急联系人邮箱发送提醒邮件",
                                       font=('黑体', 12, 'bold'),
                                       foreground=self.colors['text_light'],
                                       bg=self.colors['card'],  # 明确设置背景色与容器一致
                                       wraplength=380,
                                       justify=tk.CENTER)
        self.warning_label.pack(pady=(0, 15))  # 减少底部间距
    
    def _draw_circle_button(self):
        """
        绘制圆形签到按钮
        """
        # 清空画布
        self.sign_button.delete("all")
        
        # 根据签到状态设置按钮颜色
        if self.is_signed_in:
            bg_color = '#9E9E9E'  # 灰色，已签到
            text_color = '#FFFFFF'  # 白色文字
            outline_color = '#BDBDBD'  # 浅灰色描边
        else:
            bg_color = self.colors['primary']  # Kelly Green，未签到
            text_color = '#FFFFFF'  # 白色文字
            outline_color = self.colors['primary_light']  # 浅Kelly Green描边
        
        # 1. 绘制圆形背景 - 使用平滑绘制，通过多次绘制模拟抗锯齿
        # 先绘制外层柔和的边框，模拟抗锯齿效果
        border_width = 1
        button_size = self.button_size  # 动态获取按钮尺寸
        center_x = button_size // 2
        center_y = button_size // 2
        
        if border_width > 0:
            for i in range(border_width):
                self.sign_button.create_oval(
                    i, i, button_size - i, button_size - i, 
                    fill=outline_color,  # 使用描边颜色绘制柔和边框
                    outline="",
                    width=0
                )
        
        # 绘制主圆形背景
        circle = self.sign_button.create_oval(
            border_width, border_width, button_size - border_width, button_size - border_width, 
            fill=bg_color,  # 根据状态设置颜色
            outline="",
            width=0
        )
        
        # 2. 直接在绿色底色上绘制笑脸，符合用户提供的图片样式
        face_x = center_x  # 按钮中心位置
        face_y = button_size * 0.39  # 按钮中心偏上位置，动态计算
        
        # 眼睛 - 圆形眼睛，位置较高
        eye_color = '#FFFFFF' if not self.is_signed_in else '#E0E0E0'  # 已签到时眼睛变浅
        eye_radius = int(button_size * 0.022)  # 眼睛半径，根据按钮尺寸动态计算
        
        # 左眼
        self.sign_button.create_oval(
            face_x - button_size * 0.083 - eye_radius, face_y - button_size * 0.067 - eye_radius, 
            face_x - button_size * 0.083 + eye_radius, face_y - button_size * 0.067 + eye_radius, 
            fill=eye_color,
            outline="",
            width=0
        )
        # 右眼
        self.sign_button.create_oval(
            face_x + button_size * 0.083 - eye_radius, face_y - button_size * 0.067 - eye_radius, 
            face_x + button_size * 0.083 + eye_radius, face_y - button_size * 0.067 + eye_radius, 
            fill=eye_color,
            outline="",
            width=0
        )
        
        # 微笑的嘴巴 - 向上弯曲的弧线，两端有上扬
        mouth_color = '#FFFFFF' if not self.is_signed_in else '#E0E0E0'  # 已签到时嘴巴变浅
        mouth_width = int(button_size * 0.139)  # 嘴巴宽度，动态计算
        
        # 使用曲线绘制微笑，两端有上扬
        # 左边上扬的小弧线
        self.sign_button.create_arc(
            face_x - mouth_width * 1.25, face_y - button_size * 0.028, 
            face_x - mouth_width * 0.25, face_y + button_size * 0.083, 
            start=30, extent=40,  # 左半部分上扬
            fill="",
            outline=mouth_color,
            width=2
        )
        # 中间的弧形
        self.sign_button.create_arc(
            face_x - mouth_width, face_y, 
            face_x + mouth_width, face_y + button_size * 0.111, 
            start=0, extent=-180,  # 中间的微笑弧线
            fill="",
            outline=mouth_color,
            width=2
        )
        # 右边上扬的小弧线
        self.sign_button.create_arc(
            face_x + mouth_width * 0.25, face_y - button_size * 0.028, 
            face_x + mouth_width * 1.25, face_y + button_size * 0.083, 
            start=110, extent=40,  # 右半部分上扬
            fill="",
            outline=mouth_color,
            width=2
        )
        
        # 3. 绘制文字（根据状态显示不同文字）- 使用微软雅黑字体
        button_text = "已签到" if self.is_signed_in else "今日签到"
        # 根据按钮尺寸动态调整字体大小
        if self.is_mobile:
            font_size = 20
        else:
            font_size = 24
            
        text = self.sign_button.create_text(center_x, button_size * 0.72, 
                                            text=button_text,
                                            font=('黑体', font_size, 'bold'),  # 调整字号
                                            fill=text_color,
                                            justify=tk.CENTER)
    
    def _circle_button_hover(self, is_hover):
        """
        圆形按钮悬停效果
        """
        # 只有未签到状态下才显示悬停效果
        if not self.is_signed_in:
            # 清空画布
            self.sign_button.delete("all")
            
            # 1. 绘制圆形背景（悬停时颜色变化）
            if is_hover:
                bg_color = self.colors['primary_dark']  # 深Kelly Green
            else:
                bg_color = self.colors['primary']  # 主色Kelly Green
            
            # 使用平滑绘制模拟抗锯齿效果
            # 先绘制柔和的边框
            outline_color = self.colors['primary_light']  # 浅Kelly Green
            border_width = 1
            button_size = self.button_size  # 动态获取按钮尺寸
            center_x = button_size // 2
            center_y = button_size // 2
            
            for i in range(border_width):
                self.sign_button.create_oval(
                    i, i, button_size - i, button_size - i, 
                    fill=outline_color, 
                    outline="",
                    width=0
                )
            
            # 绘制主圆形背景
            self.sign_button.create_oval(
                border_width, border_width, button_size - border_width, button_size - border_width, 
                fill=bg_color, 
                outline="",
                width=0
            )
            
            # 2. 直接在绿色底色上绘制笑脸，符合用户提供的图片样式
            face_x = center_x  # 按钮中心位置
            face_y = button_size * 0.39  # 按钮中心偏上位置，动态计算
            
            # 眼睛 - 圆形眼睛，位置较高
            eye_color = '#FFFFFF'
            eye_radius = int(button_size * 0.022)  # 眼睛半径，根据按钮尺寸动态计算
            
            # 左眼
            self.sign_button.create_oval(
                face_x - button_size * 0.083 - eye_radius, face_y - button_size * 0.067 - eye_radius, 
                face_x - button_size * 0.083 + eye_radius, face_y - button_size * 0.067 + eye_radius, 
                fill=eye_color,
                outline="",
                width=0
            )
            # 右眼
            self.sign_button.create_oval(
                face_x + button_size * 0.083 - eye_radius, face_y - button_size * 0.067 - eye_radius, 
                face_x + button_size * 0.083 + eye_radius, face_y - button_size * 0.067 + eye_radius, 
                fill=eye_color,
                outline="",
                width=0
            )
            
            # 微笑的嘴巴 - 向上弯曲的弧线，两端有上扬
            mouth_color = '#FFFFFF'
            mouth_width = int(button_size * 0.139)  # 嘴巴宽度，动态计算
            
            # 使用曲线绘制微笑，两端有上扬
            # 左边上扬的小弧线
            self.sign_button.create_arc(
                face_x - mouth_width * 1.25, face_y - button_size * 0.028, 
                face_x - mouth_width * 0.25, face_y + button_size * 0.083, 
                start=30, extent=40,  # 左半部分上扬
                fill="",
                outline=mouth_color,
                width=2
            )
            # 中间的弧形
            self.sign_button.create_arc(
                face_x - mouth_width, face_y, 
                face_x + mouth_width, face_y + button_size * 0.111, 
                start=0, extent=-180,  # 中间的微笑弧线
                fill="",
                outline=mouth_color,
                width=2
            )
            # 右边上扬的小弧线
            self.sign_button.create_arc(
                face_x + mouth_width * 0.25, face_y - button_size * 0.028, 
                face_x + mouth_width * 1.25, face_y + button_size * 0.083, 
                start=110, extent=40,  # 右半部分上扬
                fill="",
                outline=mouth_color,
                width=2
            )
            
            # 3. 绘制文字"今日签到"（居中显示，调整字号）- 使用微软雅黑字体
            if self.is_mobile:
                font_size = 20
            else:
                font_size = 24
                
            self.sign_button.create_text(center_x, button_size * 0.72, 
                                        text="今日签到",
                                        font=('黑体', font_size, 'bold'),
                                        fill="white",
                                        justify=tk.CENTER)
        else:
            # 已签到状态下不显示悬停效果，直接绘制灰色按钮
            self._draw_circle_button()
    
    def _save_user_info(self):
        """
        保存用户信息（模拟）
        """
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        
        if not username or not email:
            messagebox.showwarning("警告", "用户名和邮箱不能为空！")
            return False
        
        # 验证邮箱格式（简单验证）
        if "@" not in email or "." not in email:
            messagebox.showwarning("警告", "请输入有效的邮箱地址！")
            return False
        
        # 显示状态提示
        self.status_label.config(text="已记住你的信息")
        # 3秒后自动隐藏状态提示
        self.root.after(3000, lambda: self.status_label.config(text=""))
        return True
    
    def _handle_sign_in(self):
        """
        处理签到操作（模拟）
        """
        if not self.is_signed_in:
            # 执行签到操作
            messagebox.showinfo("成功", "签到成功！")
            # 更新签到状态
            self.is_signed_in = True
            # 重新绘制按钮，变为灰色
            self._draw_circle_button()
            # 移除悬停事件绑定，已签到状态下不需要悬停效果
            self.sign_button.unbind("<Enter>")
            self.sign_button.unbind("<Leave>")
        else:
            # 已签到状态下点击，显示提示
            messagebox.showinfo("提示", "您今日已签到！")

# 测试代码
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleSignInApp(root)
    root.mainloop()
