import os
import sys
import ast
import marshal
import importlib.util
import time
import struct
from typing import Optional


class PyCompiler:
    def __init__(self):
        self.imported_modules = set()

    def compile_file(self, source_path: str, output_path: Optional[str] = None) -> str:
        """编译Python源文件为pyc文件"""
        with open(source_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # 分析导入的模块
        self._analyze_imports(source_code)

        # 编译源代码为代码对象
        code_object = compile(source_code, source_path, 'exec')

        # 如果未指定输出路径，生成默认输出路径
        if output_path is None:
            source_dir = os.path.dirname(source_path)
            source_name = os.path.basename(source_path)
            module_name = os.path.splitext(source_name)[0]
            output_path = os.path.join(source_dir, f"{module_name}.pyc")

        # 写入pyc文件
        self._write_pyc_file(output_path, code_object)

        return output_path

    def _analyze_imports(self, source_code: str) -> None:
        """分析源代码中导入的模块"""
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        self.imported_modules.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imported_modules.add(node.module.split('.')[0])
        except SyntaxError:
            # 如果语法错误，无法分析导入
            pass

    def _write_pyc_file(self, output_path: str, code_object) -> None:
        """写入pyc文件，包含正确的文件头"""
        # 获取Python版本魔数
        magic = importlib.util.MAGIC_NUMBER

        # 创建时间戳（当前时间）
        timestamp = int(time.time())

        # 创建源文件大小（0表示未知）
        source_size = 0

        with open(output_path, 'wb') as f:
            # 写入魔数
            f.write(magic)

            # 写入空字节（在Python 3.7+中用于字节顺序标记）
            f.write(b'\r\n\0\0')

            # 写入时间戳（4字节整数）
            f.write(struct.pack('<I', timestamp))

            # 写入源文件大小（4字节整数，Python 3.2+）
            f.write(struct.pack('<I', source_size))

            # 写入编译后的代码对象
            marshal.dump(code_object, f)

    def get_imported_modules(self) -> set:
        """获取分析到的导入模块"""
        return self.imported_modules