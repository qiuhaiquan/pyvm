import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
import os
import sys
from pathlib import Path
from pyvm.core.compiler import PyCompiler
from pyvm.core.interpreter import PyInterpreter
from pyvm.core.security import CodeSecurityChecker
import time

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

    def _create_menu(self):
        """创建菜单栏及快捷键绑定"""
        menubar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self._save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编译菜单
        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="编译当前文件", command=self._compile_current_file, accelerator="F5")
        compile_menu.add_command(label="编译并执行", command=self._compile_and_execute, accelerator="F6")
        menubar.add_cascade(label="编译", menu=compile_menu)

        # 执行菜单
        execute_menu = tk.Menu(menubar, tearoff=0)
        execute_menu.add_command(label="执行当前pyc", command=self._execute_current_pyc, accelerator="F9")
        execute_menu.add_command(label="打开并执行pyc", command=self._open_and_execute_pyc)
        menubar.add_cascade(label="执行", menu=execute_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        help_menu.add_command(label="使用说明", command=self._show_help)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

        # 绑定快捷键
        self.root.bind("<Control-n>", lambda event: self._new_file())
        self.root.bind("<Control-o>", lambda event: self._open_file())
        self.root.bind("<Control-s>", lambda event: self._save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self._save_file_as())
        self.root.bind("<Control-q>", lambda event: self.root.quit())
        self.root.bind("<F5>", lambda event: self._compile_current_file())
        self.root.bind("<F6>", lambda event: self._compile_and_execute())
        self.root.bind("<F9>", lambda event: self._execute_current_pyc())

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
        self.file_list.configure(yscrollcommand=scrollbar.set)  # 修改此处，修正意外实参问题

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

    def _new_file(self):
        """创建新文件"""
        if self._check_unsaved_changes():
            self.code_editor.delete(1.0, tk.END)  # 修改此处，使用正确的编辑器对象
            self.current_file = None
            self.root.title("Python VM Editor")

    def _open_file(self, event=None):
        """打开文件对话框"""
        if self._check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
            if file_path:
                self._load_file(file_path)

    def _load_file(self, file_path):
        """加载文件内容到编辑器"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.code_editor.delete(1.0, tk.END)  # 修改此处，使用正确的编辑器对象
            self.code_editor.insert(tk.END, content)
            self.current_file = file_path
            self.root.title(f"Python VM Editor - {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def _save_file(self, event=None):
        """保存当前文件"""
        if self.current_file:
            self._save_file_as(self.current_file)
            return True
        return self._save_file_as()

    def _save_file_as(self, file_path=None):
        """另存为新文件"""
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
        if file_path:
            try:
                content = self.code_editor.get(1.0, tk.END)  # 修改此处，使用正确的编辑器对象
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"Python VM Editor - {os.path.basename(file_path)}")
                return True
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {str(e)}")
        return False

    def _check_unsaved_changes(self):
        """检查是否有未保存的更改"""
        if self.code_editor.edit_modified():  # 修改此处，使用正确的编辑器对象
            response = messagebox.askyesnocancel(
                "保存", "是否保存更改?"
            )
            if response is None:  # 用户点击了取消
                return False
            if response:  # 用户点击了是
                return self._save_file()
        return True

    def _compile_and_execute(self, event=None):
        """编译当前文件并执行生成的pyc"""
        if not self.current_file:
            if not self._save_file():
                return

        try:
            # 编译文件
            pyc_path = self.compiler.compile_file(self.current_file)
            self.current_pyc = pyc_path

            # 更新输出面板
            self._update_output(f"编译成功!\n生成的pyc文件: {pyc_path}\n\n正在执行...")

            # 执行pyc文件
            result = self.interpreter.execute_pyc(pyc_path)
            self._update_output(f"执行完成\n输出结果:\n{result}")

            # 更新状态
            self._update_status(f"编译并执行完成: {os.path.basename(pyc_path)}")  # 修改此处，使用正确的状态更新方法
        except Exception as e:
            self._update_output(f"错误: {str(e)}")
            self._update_status("编译并执行失败")  # 修改此处，使用正确的状态更新方法
            messagebox.showerror("执行错误", str(e))

    def _refresh_file_list(self):
        """刷新文件列表"""
        self.file_list.delete(*self.file_list.get_children())
        try:
            # 获取当前目录下的所有.py和.pyc文件
            for file in os.listdir(os.getcwd()):
                if file.endswith(".py") or file.endswith(".pyc"):
                    file_path = os.path.join(os.getcwd(), file)
                    size = os.path.getsize(file_path)
                    modified = time.ctime(os.path.getmtime(file_path))
                    self.file_list.insert("", "end", text=file, values=(size, modified))
        except Exception as e:
            self._update_output(f"无法加载文件列表: {str(e)}")

    def _on_file_double_click(self, event):
        """处理文件双击事件"""
        item = self.file_list.selection()
        if not item:
            return

        file_name = self.file_list.item(item, "text")
        file_path = os.path.join(os.getcwd(), file_name)

        if file_name.endswith(".py"):
            # 打开Python文件进行编辑
            self._load_file(file_path)
        elif file_name.endswith(".pyc"):
            # 执行pyc文件
            self.current_pyc = file_path
            self._execute_current_pyc()

    def _open_and_execute_pyc(self):
        """打开并执行pyc文件"""
        file_path = filedialog.askopenfilename(
            defaultextension=".pyc",
            filetypes=[("Python字节码文件", "*.pyc"), ("All Files", "*.*")]
        )

        if file_path:
            self.current_pyc = file_path
            self._execute_current_pyc()

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "Python VM 编辑器 v1.0\n\n"
            "一个简单的Python虚拟机实现，支持编译和执行Python代码。\n\n"
            "© 2025 开发者"
        )

    def _show_help(self):
        """显示使用帮助"""
        help_text = """
使用说明:

1. 文件操作:
   - 新建: Ctrl+N
   - 打开: Ctrl+O
   - 保存: Ctrl+S
   - 另存为: Ctrl+Shift+S
   - 退出: Ctrl+Q

2. 编译操作:
   - 编译当前文件: F5
   - 编译并执行: F6

3. 执行操作:
   - 执行当前pyc: F9
   - 打开并执行pyc: 菜单项

4. 界面:
   - 左侧: 文件浏览器
   - 中间: 代码编辑器
   - 底部: 输出结果
        """
        messagebox.showinfo("使用帮助", help_text)