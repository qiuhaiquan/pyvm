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
        """设置安全的内置函数，兼容__builtins__为字典或模块的情况"""
        safe_builtins = {}

        # 兼容__builtins__为字典或模块的情况
        if isinstance(__builtins__, dict):
            builtins_dict = __builtins__
        else:
            builtins_dict = vars(__builtins__)  # 获取模块的__dict__

        # 复制原始内置函数
        for name, obj in builtins_dict.items():
            # 过滤危险函数
            if name in ['eval', 'exec', 'open']:
                continue
            safe_builtins[name] = obj

        def safe_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
            if 'w' in mode or 'a' in mode:
                raise PermissionError("写文件操作被安全限制")
            return open(file, mode, buffering, encoding, errors, newline)

        safe_builtins['open'] = safe_open

        # 替换全局内置函数
        self.globals['__builtins__'] = types.ModuleType('__builtins__')
        for name, obj in safe_builtins.items():
            setattr(self.globals['__builtins__'], name, obj)

    def execute_code_object(self, code_object):
        """执行Python代码对象并返回结果"""
        try:
            # 使用初始化时设置的安全全局命名空间
            exec(code_object, self.globals)

            # 返回全局命名空间中的结果（如果有）
            return self.globals.get('__result__', None)
        except Exception as e:
            raise RuntimeError(f"执行代码对象失败: {str(e)}") from e

    def execute_pyc(self, pyc_path):
        """执行pyc文件并返回结果"""
        if not os.path.exists(pyc_path):
            raise FileNotFoundError(f"pyc文件不存在: {pyc_path}")

        with open(pyc_path, 'rb') as f:
            # 手动解析pyc文件头部
            magic = f.read(4)
            if len(magic) < 4:
                raise ValueError("无效的pyc文件")

            # 跳过时间戳和其他元数据
            if sys.version_info >= (3, 7):
                # Python 3.7+ 有更复杂的头部
                f.read(4)  # 时间戳
                if sys.version_info >= (3, 8):
                    f.read(4)  # size字段
            else:
                f.read(4)  # 旧版本只有时间戳

            # 读取代码对象
            try:
                code_object = marshal.load(f)
            except Exception as e:
                raise ValueError(f"解析pyc文件失败: {str(e)}") from e

        # 使用安全的全局命名空间执行代码
        try:
            exec(code_object, self.globals)
            return self.globals.get('__result__', None)
        except Exception as e:
            raise RuntimeError(f"执行pyc文件失败: {str(e)}") from e