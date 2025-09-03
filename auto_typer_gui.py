import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyautogui
import pyperclip
import time
import threading
from typing import Optional

class AutoTyperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能自动打字助手")
        self.root.geometry("600x720")
        self.root.resizable(True, True)
        
        # 设置现代化主题
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色主题
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei UI', 10), foreground='#34495e')
        style.configure('Custom.TButton', font=('Microsoft YaHei UI', 10))
        
        # 状态变量
        self.is_typing = False
        self.typing_thread: Optional[threading.Thread] = None
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.is_topmost = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🖊️智能自动打字助手", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="轻松实现自动打字，提高工作效率", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 文本输入区域
        text_frame = ttk.LabelFrame(main_frame, text="📝 输入文本", padding="10")
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(1, weight=1)
        
        # 文本框
        self.text_area = scrolledtext.ScrolledText(text_frame, height=8, font=('Consolas', 10), wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(text_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(button_frame, text="📋 从剪贴板粘贴", command=self.paste_from_clipboard, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ 清空", command=self.clear_text, style='Custom.TButton').pack(side=tk.LEFT)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 打字设置", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        
        # 速度设置
        ttk.Label(settings_frame, text="打字速度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.speed_var = tk.StringVar(value="中速")
        speed_combo = ttk.Combobox(settings_frame, textvariable=self.speed_var, 
                                 values=["慢速 (0.1s/字符)", "中速 (0.05s/字符)", "快速 (0.02s/字符)", "极速 (0.01s/字符)"],
                                 state="readonly", width=20)
        speed_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        speed_combo.set("中速 (0.05s/字符)")
        
        # 延迟设置
        ttk.Label(settings_frame, text="开始延迟:").grid(row=0, column=2, sticky=tk.W, padx=(10, 10))
        
        self.delay_var = tk.StringVar(value="3")
        delay_spin = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.delay_var, width=5)
        delay_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(settings_frame, text="秒").grid(row=0, column=4, sticky=tk.W)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15))
        
        # 第一行按钮
        button_row1 = ttk.Frame(control_frame)
        button_row1.pack(pady=(0, 5))
        
        self.start_button = ttk.Button(button_row1, text="🚀 开始打字", command=self.start_typing, style='Custom.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_button = ttk.Button(button_row1, text="⏸️ 暂停", command=self.pause_typing, state=tk.DISABLED, style='Custom.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_row1, text="⏹️ 停止", command=self.stop_typing, state=tk.DISABLED, style='Custom.TButton')
        self.stop_button.pack(side=tk.LEFT)
        
        # 第二行按钮
        button_row2 = ttk.Frame(control_frame)
        button_row2.pack()
        
        self.topmost_button = ttk.Button(button_row2, text="📌 窗口置顶", command=self.toggle_topmost, style='Custom.TButton')
        self.topmost_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_row2, text="ℹ️ 关于", command=self.show_about, style='Custom.TButton').pack(side=tk.LEFT)
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="📊 状态: 就绪", foreground='#27ae60')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def paste_from_clipboard(self):
        """从剪贴板粘贴文本"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, clipboard_content)
                self.update_status("📋 已从剪贴板粘贴文本")
            else:
                messagebox.showwarning("警告", "剪贴板为空！")
        except Exception as e:
            messagebox.showerror("错误", f"粘贴失败: {e}")
    
    def clear_text(self):
        """清空文本"""
        self.text_area.delete(1.0, tk.END)
        self.update_status("🗑️ 文本已清空")
    
    def get_typing_delay(self):
        """获取打字延迟"""
        speed_map = {
            "慢速 (0.1s/字符)": 0.1,
            "中速 (0.05s/字符)": 0.05,
            "快速 (0.02s/字符)": 0.02,
            "极速 (0.01s/字符)": 0.01
        }
        return speed_map.get(self.speed_var.get(), 0.05)
    
    def update_status(self, message, color='#34495e'):
        """更新状态信息"""
        self.status_label.config(text=f"📊 状态: {message}", foreground=color)
        self.root.update_idletasks()
    
    def start_typing(self):
        """开始打字"""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请先输入要打字的文本！")
            return
        
        self.is_typing = True
        self.pause_event.set()
        self.stop_event.clear()
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        
        # 启动打字线程
        self.typing_thread = threading.Thread(target=self._typing_worker, args=(text,))
        self.typing_thread.daemon = True
        self.typing_thread.start()
    
    def pause_typing(self):
        """暂停/继续打字"""
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_button.config(text="▶️ 继续")
            self.update_status("⏸️ 打字已暂停", '#f39c12')
        else:
            self.pause_event.set()
            self.pause_button.config(text="⏸️ 暂停")
            self.update_status("▶️ 打字继续中...", '#3498db')
    
    def stop_typing(self):
        """停止打字"""
        self.stop_event.set()
        self.is_typing = False
        
        # 重置按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸️ 暂停")
        self.stop_button.config(state=tk.DISABLED)
        
        self.progress_var.set(0)
        self.update_status("⏹️ 打字已停止", '#e74c3c')
    
    def _typing_worker(self, text):
        """打字工作线程"""
        try:
            delay = self.get_typing_delay()
            start_delay = int(self.delay_var.get())
            
            # 倒计时
            for i in range(start_delay, 0, -1):
                if self.stop_event.is_set():
                    return
                self.update_status(f"⏰ {i} 秒后开始打字，请将光标放在目标位置...", '#f39c12')
                time.sleep(1)
            
            if self.stop_event.is_set():
                return
            
            self.update_status("🖊️ 正在打字中...", '#3498db')
            
            total_chars = len(text)
            for i, char in enumerate(text):
                if self.stop_event.is_set():
                    break
                
                # 等待暂停解除
                self.pause_event.wait()
                
                if self.stop_event.is_set():
                    break
                
                pyautogui.write(char)
                time.sleep(delay)
                
                # 更新进度
                progress = (i + 1) / total_chars * 100
                self.progress_var.set(progress)
                
                if (i + 1) % 50 == 0:
                    self.update_status(f"🖊️ 打字进度: {progress:.1f}%", '#3498db')
            
            if not self.stop_event.is_set():
                self.update_status("✅ 打字完成！", '#27ae60')
                self.progress_var.set(100)
            
        except Exception as e:
            self.update_status(f"❌ 错误: {e}", '#e74c3c')
        finally:
            # 重置状态
            self.root.after(0, self._reset_ui_state)
    
    def _reset_ui_state(self):
        """重置UI状态"""
        self.is_typing = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸️ 暂停")
        self.stop_button.config(state=tk.DISABLED)
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)
        
        if self.is_topmost:
            self.topmost_button.config(text="📌 取消置顶")
            self.update_status("📌 窗口已置顶", '#3498db')
        else:
            self.topmost_button.config(text="📌 窗口置顶")
            self.update_status("📌 窗口置顶已取消", '#34495e')
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """🖊️ 智能自动打字助手 v2.0

✨ 功能特性:
• 多种输入模式支持
• 灵活的速度控制
• 实时进度显示
• 暂停/继续/停止控制
• 窗口置顶功能

💡 使用提示:
• 使用前请将光标放在目标位置
• 按Ctrl+C可随时中断操作
• 建议先在记事本中测试

⚠️ 注意事项:
• 确保目标应用程序已获得焦点
• 避免在重要文档中直接使用
• 打字过程中不要移动鼠标

🎯 开发目标: 提高工作效率，简化重复输入"""
        
        messagebox.showinfo("关于 - 智能自动打字助手", about_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = AutoTyperGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()