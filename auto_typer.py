import pyautogui
import pyperclip
import time
import sys
import threading
from typing import Optional
import signal

class AutoTyper:
    """自动打字类"""
    
    def __init__(self):
        self.is_typing = False
        self.stop_flag = threading.Event()
        
    def auto_type_from_clipboard(self, delay=0.05, countdown=3):
        """
        从剪贴板获取文本并自动打字
        
        Args:
            delay (float): 每个字符之间的延迟时间（秒）
            countdown (int): 开始前的倒计时秒数
        """
        try:
            # 获取剪贴板内容
            clipboard_content = pyperclip.paste()
            
            if not clipboard_content:
                print("❌ 剪贴板为空！")
                return False
            
            # 分割文本，获取第一段（以双换行符分割）
            paragraphs = clipboard_content.split('\n\n')
            text_to_type = paragraphs[0].strip()
            
            if not text_to_type:
                print("❌ 第一段为空！")
                return False
            
            return self._type_text(text_to_type, delay, countdown)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断操作！")
            return False
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            return False
    
    def auto_type_text(self, text, delay=0.05, countdown=3):
        """
        直接输入指定文本
        
        Args:
            text (str): 要输入的文本
            delay (float): 每个字符之间的延迟时间（秒）
            countdown (int): 开始前的倒计时秒数
        """
        if not text.strip():
            print("❌ 文本为空！")
            return False
            
        return self._type_text(text.strip(), delay, countdown)
    
    def _type_text(self, text, delay, countdown):
        """
        内部打字方法
        """
        try:
            print(f"📝 准备输入文本 ({len(text)} 字符): {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"⏰ {countdown}秒后开始自动打字，请将光标放在目标位置...")
            print("💡 按 Ctrl+C 可随时中断")
            
            # 重置停止标志
            self.stop_flag.clear()
            self.is_typing = True
            
            # 倒计时
            for i in range(countdown, 0, -1):
                if self.stop_flag.is_set():
                    return False
                print(f"⏳ {i}...")
                time.sleep(1)
            
            if self.stop_flag.is_set():
                return False
                
            print("🚀 开始打字！")
            
            # 逐字符输入
            for i, char in enumerate(text):
                if self.stop_flag.is_set():
                    print("\n⏹️ 打字被中断！")
                    return False
                    
                pyautogui.write(char)
                time.sleep(delay)
                
                # 每50个字符显示进度
                if (i + 1) % 50 == 0:
                    progress = (i + 1) / len(text) * 100
                    print(f"\r📊 进度: {progress:.1f}% ({i + 1}/{len(text)})", end='', flush=True)
            
            print("\n\n✅ 打字完成！")
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断打字！")
            return False
        except Exception as e:
            print(f"\n❌ 打字过程中发生错误: {e}")
            return False
        finally:
            self.is_typing = False
    
    def stop_typing(self):
        """停止打字"""
        self.stop_flag.set()
        self.is_typing = False

# 保持向后兼容的函数
def auto_type_from_clipboard(delay=0.05):
    """向后兼容的函数"""
    typer = AutoTyper()
    return typer.auto_type_from_clipboard(delay)

def auto_type_with_speed_control():
    """
    带速度控制的自动打字（改进版）
    """
    try:
        clipboard_content = pyperclip.paste()
        
        if not clipboard_content:
            print("❌ 剪贴板为空！")
            return False
        
        # 获取第一段
        paragraphs = clipboard_content.split('\n\n')
        text_to_type = paragraphs[0].strip()
        
        if not text_to_type:
            print("❌ 第一段为空！")
            return False
        
        print(f"📝 文本长度: {len(text_to_type)} 字符")
        print(f"📄 预览: {text_to_type[:100]}{'...' if len(text_to_type) > 100 else ''}")
        print("\n⚡ 选择打字速度:")
        print("1. 🐌 慢速 (0.1秒/字符) - 适合演示")
        print("2. 🚶 中速 (0.05秒/字符) - 推荐")
        print("3. 🏃 快速 (0.02秒/字符) - 高效")
        print("4. 🚀 极速 (0.01秒/字符) - 最快")
        print("5. 🎯 自定义速度")
        
        while True:
            choice = input("\n请选择 (1-5): ").strip()
            
            speed_map = {
                '1': (0.1, "慢速"),
                '2': (0.05, "中速"),
                '3': (0.02, "快速"),
                '4': (0.01, "极速")
            }
            
            if choice in speed_map:
                delay, speed_name = speed_map[choice]
                break
            elif choice == '5':
                try:
                    delay = float(input("请输入延迟时间（秒，如0.03）: "))
                    if delay < 0:
                        print("❌ 延迟时间不能为负数！")
                        continue
                    speed_name = "自定义"
                    break
                except ValueError:
                    print("❌ 请输入有效的数字！")
                    continue
            else:
                print("❌ 无效选择，请重新输入！")
        
        # 询问倒计时时间
        while True:
            try:
                countdown = int(input(f"\n⏰ 设置倒计时时间（秒，默认5）: ") or "5")
                if countdown < 0:
                    print("❌ 倒计时不能为负数！")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字！")
        
        # 创建AutoTyper实例并开始打字
        typer = AutoTyper()
        
        print(f"\n🎯 设置完成:")
        print(f"   速度: {speed_name} ({delay}秒/字符)")
        print(f"   倒计时: {countdown}秒")
        print(f"   文本长度: {len(text_to_type)}字符")
        
        estimated_time = len(text_to_type) * delay
        print(f"   预计用时: {estimated_time:.1f}秒")
        
        return typer.auto_type_text(text_to_type, delay, countdown)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户取消操作！")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def interactive_text_input():
    """
    交互式文本输入模式
    """
    print("\n📝 请输入要自动打字的文本:")
    print("💡 提示: 输入完成后按两次回车结束输入")
    print("-" * 50)
    
    lines = []
    empty_line_count = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
            lines.append(line)
        except KeyboardInterrupt:
            print("\n⏹️ 输入被取消！")
            return None
    
    text = "\n".join(lines).strip()
    if not text:
        print("❌ 未输入任何文本！")
        return None
    
    return text

def main():
    """
    主函数
    """
    print("🖊️" + "=" * 48)
    print("🎯           智能自动打字助手 v2.0")
    print("🖊️" + "=" * 48)
    print("💡 功能: 自动模拟键盘输入，提高工作效率")
    print("⚠️  注意: 请确保目标应用程序已获得焦点")
    print()
    
    # 设置Ctrl+C处理
    def signal_handler(sig, frame):
        print("\n\n👋 程序已退出，再见！")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        print("\n📋 选择输入模式:")
        print("1. 📋 剪贴板模式 (从剪贴板获取文本)")
        print("2. ⚡ 高级剪贴板模式 (可选择速度)")
        print("3. ✏️  手动输入模式 (直接输入文本)")
        print("4. 🖥️  启动GUI界面")
        print("5. ❓ 帮助信息")
        print("6. 🚪 退出程序")
        
        try:
            choice = input("\n请选择模式 (1-6): ").strip()
            
            if choice == '1':
                print("\n🚀 启动简单剪贴板模式...")
                result = auto_type_from_clipboard()
                if result:
                    print("\n✅ 任务完成！")
                else:
                    print("\n❌ 任务失败或被取消")
                    
            elif choice == '2':
                print("\n🚀 启动高级剪贴板模式...")
                result = auto_type_with_speed_control()
                if result:
                    print("\n✅ 任务完成！")
                else:
                    print("\n❌ 任务失败或被取消")
                    
            elif choice == '3':
                print("\n🚀 启动手动输入模式...")
                text = interactive_text_input()
                if text:
                    typer = AutoTyper()
                    result = typer.auto_type_text(text)
                    if result:
                        print("\n✅ 任务完成！")
                    else:
                        print("\n❌ 任务失败或被取消")
                        
            elif choice == '4':
                print("\n🖥️ 启动GUI界面...")
                try:
                    import subprocess
                    subprocess.run([sys.executable, "auto_typer_gui.py"], check=True)
                except FileNotFoundError:
                    print("❌ GUI文件 'auto_typer_gui.py' 未找到！")
                except Exception as e:
                    print(f"❌ 启动GUI失败: {e}")
                    
            elif choice == '5':
                print("\n📖 帮助信息:")
                print("=" * 50)
                print("🎯 程序功能:")
                print("   • 自动模拟键盘输入")
                print("   • 支持多种速度设置")
                print("   • 可暂停/继续/停止")
                print("   • 实时进度显示")
                print()
                print("💡 使用技巧:")
                print("   • 使用前请将光标放在目标位置")
                print("   • 按Ctrl+C可随时中断操作")
                print("   • 建议先在记事本中测试")
                print()
                print("⚠️  注意事项:")
                print("   • 确保目标应用程序已获得焦点")
                print("   • 避免在重要文档中直接使用")
                print("   • 打字过程中不要移动鼠标")
                
            elif choice == '6':
                print("\n👋 感谢使用智能自动打字助手！")
                print("🎯 如有问题或建议，欢迎反馈")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入1-6之间的数字！")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出，再见！")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")
            print("🔄 请重试或选择其他模式")
        
        # 询问是否继续
        try:
            continue_choice = input("\n🔄 是否继续使用？(y/n，默认y): ").strip().lower()
            if continue_choice in ['n', 'no', '否']:
                print("\n👋 再见！")
                break
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出，再见！")
            break

if __name__ == "__main__":
    main()