import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
import os
import sys
import time
from pathlib import Path
from ..core.compiler import PyCompiler
from ..core.interpreter import PyInterpreter
from ..core.security import CodeSecurityChecker
sys.path.append(str(Path(__file__).resolve().parent.parent))

class PyVMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python虚拟机")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置中文字体支持
        self.font = ('SimHei', 10)
        
        # 创建核心组件
        self.compiler = PyCompiler()
        self.interpreter = PyInterpreter()
        self.security_checker = CodeSecurityChecker()
        
        # 当前文件路径
        self.current_file = None
        self.current_pyc = None
        
        # 创建UI
        self._create_menu()
        self._create_main_frame()
        
    def _create_main_frame(self):
        """创建主框架（修改后）"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="就绪", font=self.font)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 创建安全状态指示器
        self.security_status = ttk.Label(status_frame, text="安全检查: 未检查", font=self.font, foreground="orange")
        self.security_status.pack(side=tk.RIGHT, padx=5)
        
        # 创建标签页控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 源代码编辑标签页
        source_frame = ttk.Frame(notebook)
        notebook.add(source_frame, text="源代码")
        
        # 创建滚动文本框用于编辑Python代码
        self.code_editor = scrolledtext.ScrolledText(source_frame, wrap=tk.WORD, font=self.font)
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # 输出标签页
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="输出")
        
        # 创建滚动文本框用于显示程序输出
        self.output_display = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=self.font)
        self.output_display.pack(fill=tk.BOTH, expand=True)
        self.output_display.config(state=tk.DISABLED)
        
        # 安全检查标签页
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text="安全检查")
        
        # 创建安全检查结果显示
        self.security_results = scrolledtext.ScrolledText(security_frame, wrap=tk.WORD, font=self.font)
        self.security_results.pack(fill=tk.BOTH, expand=True)
        self.security_results.config(state=tk.DISABLED)
        
        # 文件列表标签页
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="文件列表")
        
        # 创建文件列表
        self.file_list = ttk.Treeview(file_frame)
        self.file_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.file_list.configure(yscroll=scrollbar.set)
        
        # 设置文件列表列
        self.file_list["columns"] = ("size", "modified")
        self.file_list.column("#0", width=300, minwidth=250)
        self.file_list.column("size", width=100, minwidth=50)
        self.file_list.column("modified", width=150, minwidth=100)
        
        self.file_list.heading("#0", text="文件名")
        self.file_list.heading("size", text="大小")
        self.file_list.heading("modified", text="修改时间")
        
        # 绑定双击事件
        self.file_list.bind("<Double-1>", self._on_file_double_click)
        
        # 刷新文件列表
        self._refresh_file_list()
    
    def _compile_current_file(self):
        """编译当前文件（修改后）"""
        if not self.current_file:
            if not self._save_file():
                return
        
        # 先进行安全检查
        is_safe, issues = self._check_code_security()
        if not is_safe:
            self._update_security_status(False, issues)
            response = messagebox.askyesno("安全警告", 
                f"检测到{len(issues)}个潜在安全问题:\n\n" + 
                "\n".join([f"- {issue}" for issue in issues]) + 
                "\n\n是否继续编译？")
            if not response:
                return
        
        self._update_status("正在编译...")
        
        def compile_task():
            try:
                pyc_path = self.compiler.compile_file(self.current_file)
                self.current_pyc = pyc_path
                
                # 使用root.after确保在主线程更新UI
                self.root.after(0, lambda: self._update_output(f"编译成功!\n生成的pyc文件: {pyc_path}"))
                self.root.after(0, lambda: self._update_status(f"编译完成: {os.path.basename(pyc_path)}"))
                self.root.after(0, self._refresh_file_list)
            except Exception as e:
                self.root.after(0, lambda: self._update_output(f"编译错误: {str(e)}"))
                self.root.after(0, lambda: self._update_status("编译失败"))
        
        # 在后台线程执行编译，避免UI冻结
        threading.Thread(target=compile_task, daemon=True).start()
    
    def _check_code_security(self):
        """检查代码安全性"""
        code = self.code_editor.get(1.0, tk.END)
        return self.security_checker.check_code(code)
    
    def _update_security_status(self, is_safe, issues=None):
        """更新安全状态显示"""
        self.security_results.config(state=tk.NORMAL)
        self.security_results.delete(1.0, tk.END)
        
        if is_safe:
            self.security_status.config(text="安全检查: 通过", foreground="green")
            self.security_results.insert(tk.END, "代码安全检查通过，未发现潜在危险。")
        else:
            self.security_status.config(text=f"安全检查: 发现{len(issues)}个问题", foreground="red")
            self.security_results.insert(tk.END, "发现以下潜在安全问题:\n\n" + 
                "\n".join([f"• {issue}" for issue in issues]))
        
        self.security_results.config(state=tk.DISABLED)
    
    def _execute_current_pyc(self):
        """执行当前pyc文件（修改后）"""
        if not self.current_pyc:
            self._update_output("没有当前pyc文件，请先编译或打开一个pyc文件")
            return
        
        self._update_status("正在执行...")
        
        def execute_task():
            try:
                result = self.interpreter.execute_pyc(self.current_pyc)
                self.root.after(0, lambda: self._update_output(f"执行完成\n输出结果:\n{result}"))
                self.root.after(0, lambda: self._update_status(f"执行完成: {os.path.basename(self.current_pyc)}"))
            except Exception as e:
                self.root.after(0, lambda: self._update_output(f"执行错误: {str(e)}"))
                self.root.after(0, lambda: self._update_status("执行失败"))
        
        threading.Thread(target=execute_task, daemon=True).start()
    
    def _update_output(self, text):
        """更新输出显示"""
        self.output_display.config(state=tk.NORMAL)
        self.output_display.delete(1.0, tk.END)
        self.output_display.insert(tk.END, text)
        self.output_display.config(state=tk.DISABLED)
    
    def _update_status(self, text):
        """更新状态标签"""
        self.status_label.config(text=text)    