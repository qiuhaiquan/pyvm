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
        self.file_list.configure(yscrollcommand=scrollbar.set)

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
        self.output_display.insert(tk.END, text + '\n')
        self.output_display.see(tk.END)
        self.output_display.config(state=tk.DISABLED)

    def _new_file(self):
        """新建文件"""
        self.code_editor.delete(1.0, tk.END)
        self.current_file = None
        self._update_status("新建文件")
        self.security_status.config(text="安全检查: 未检查", foreground="orange")
        self._update_security_status(True)

    def _open_file(self):
        """打开文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(tk.END, code)
                self._update_status(f"打开文件: {os.path.basename(file_path)}")
                self.security_status.config(text="安全检查: 未检查", foreground="orange")
                self._update_security_status(True)
                self._refresh_file_list()
            except Exception as e:
                self._update_output(f"打开文件出错: {str(e)}")
                self._update_status("打开文件失败")

    def _save_file(self):
        """保存文件"""
        if self.current_file:
            try:
                code = self.code_editor.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                self._update_status(f"保存文件: {os.path.basename(self.current_file)}")
                self._refresh_file_list()
                return True
            except Exception as e:
                self._update_output(f"保存文件出错: {str(e)}")
                self._update_status("保存文件失败")
                return False
        else:
            return self._save_file_as()

    def _save_file_as(self):
        """另存为文件"""
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            self.current_file = file_path
            try:
                code = self.code_editor.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self._update_status(f"另存为: {os.path.basename(file_path)}")
                self._refresh_file_list()
                return True
            except Exception as e:
                self._update_output(f"另存为出错: {str(e)}")
                self._update_status("另存为失败")
                return False
        return False

    def _compile_and_execute(self):
        """编译并执行"""
        if self._compile_current_file():
            self._execute_current_pyc()

    def _open_and_execute_pyc(self):
        """打开并执行pyc文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Compiled Python Files", "*.pyc")])
        if file_path:
            self.current_pyc = file_path
            self._execute_current_pyc()

    def _show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "Python虚拟机\n这是一个简单的Python虚拟机实现，支持将Python代码编译为pyc文件并执行，同时提供图形界面和命令行工具。")

    def _show_help(self):
        """显示使用说明"""
        help_text = """
使用说明：
1. 文件操作：
   - 新建：创建一个新的Python文件。
   - 打开：打开一个已有的Python文件。
   - 保存：保存当前编辑的Python文件。
   - 另存为：将当前编辑的Python文件另存为其他文件。
   - 退出：关闭程序。

2. 编译操作：
   - 编译当前文件：将当前编辑的Python文件编译为pyc文件。
   - 编译并执行：编译当前文件并执行生成的pyc文件。

3. 执行操作：
   - 执行当前pyc：执行当前已编译的pyc文件。
   - 打开并执行pyc：打开一个pyc文件并执行。

4. 安全检查：
   在编译前会进行代码安全检查，若发现潜在危险会提示。
        """
        messagebox.showinfo("使用说明", help_text)

    def _refresh_file_list(self):
        """刷新文件列表"""
        for i in self.file_list.get_children():
            self.file_list.delete(i)
        if self.current_file:
            file_dir = os.path.dirname(self.current_file)
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    modified_time = time.ctime(os.path.getmtime(file_path))
                    self.file_list.insert("", "end", text=file, values=(file_size, modified_time))

    def _on_file_double_click(self, event):
        """文件双击事件"""
        item = self.file_list.selection()[0]
        file_name = self.file_list.item(item, "text")
        if self.current_file:
            file_dir = os.path.dirname(self.current_file)
            file_path = os.path.join(file_dir, file_name)
            if file_path.endswith('.py'):
                self._open_file()

    def _update_status(self, text):
        """更新状态栏逻辑"""
        self.status_label.config(text=text)
