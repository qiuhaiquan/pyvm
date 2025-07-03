import marshal
import sys
import os
import types
import time
from io import StringIO
import contextlib
from pathlib import Path
import importlib.util
sys.path.append(str(Path(__file__).resolve().parent.parent))

class PyInterpreter:
    def __init__(self, module_paths=None):
        self.globals = {
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None,
            '__loader__': None,
            '__spec__': None,
            '__annotations__': {},
            '__builtins__': __import__('builtins'),
        }
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.module_paths = module_paths or []
        
        # 添加安全限制的内置函数
        self._setup_safe_builtins()
    
    def _setup_safe_builtins(self):
        """设置安全的内置函数，限制危险操作"""
        safe_builtins = {}
        
        # 复制原始内置函数
        for name, obj in __builtins__.__dict__.items():
            # 过滤危险函数
            if name in ['eval', 'exec', 'open']:
                continue
            safe_builtins[name] = obj
        
        # 添加受限版本的危险函数
        def safe_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
            if 'w' in mode or 'a' in mode:
                raise PermissionError("写文件操作被安全限制")
            return open(file, mode, buffering, encoding, errors, newline)
        
        safe_builtins['open'] = safe_open
        
        # 替换全局内置函数
        self.globals['__builtins__'] = types.ModuleType('__builtins__')
        for name, obj in safe_builtins.items():
            setattr(self.globals['__builtins__'], name, obj)
    
    def execute_pyc(self, pyc_path, capture_output=True):
        """执行pyc文件（修改后）"""
        with open(pyc_path, 'rb') as f:
            # 读取魔法数字（前四个字节）
            magic = f.read(4)
            
            # 读取时间戳（四个字节）
            timestamp = f.read(4)
            
            # 读取字节码对象
            code_object = marshal.load(f)
        
        # 设置执行环境
        old_globals = self.globals.copy()
        old_sys_path = sys.path.copy()
        
        # 添加用户指定的模块路径
        sys.path.extend(self.module_paths)
        
        # 捕获输出
        if capture_output:
            output = StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    exec(code_object, self.globals)
                    result = output.getvalue()
                except Exception as e:
                    import traceback
                    result = traceback.format_exc()
        else:
            try:
                exec(code_object, self.globals)
                result = None
            except Exception as e:
                import traceback
                result = traceback.format_exc()
        
        # 恢复环境
        self.globals = old_globals
        sys.path = old_sys_path
        
        return result    