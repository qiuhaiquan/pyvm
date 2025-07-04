import os
import sys
import ast
import marshal
import importlib.util
import tempfile
from typing import Set, Optional
from modulefinder import ModuleFinder
import zipapp

class PyCompiler:
    def __init__(self):
        self.imported_modules: Set[str] = set()

    def compile_file(self, source_path: str, output_path: Optional[str] = None) -> str:
        """编译Python源文件为pyc文件，使用modulefinder分析依赖并使用zipapp打包"""
        # 使用modulefinder分析依赖
        finder = ModuleFinder()
        finder.run_script(source_path)

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 复制必要的模块到临时目录
        for name, mod in finder.modules.items():
            if mod.__file__:
                module_dir = os.path.join(temp_dir, *name.split('.'))
                os.makedirs(os.path.dirname(module_dir), exist_ok=True)
                if os.path.isfile(mod.__file__):
                    with open(mod.__file__, 'rb') as src, open(module_dir + '.py', 'wb') as dst:
                        dst.write(src.read())

        # 复制主程序文件到临时目录
        main_file_name = os.path.basename(source_path)
        main_file_path = os.path.join(temp_dir, main_file_name)
        with open(source_path, 'rb') as src, open(main_file_path, 'wb') as dst:
            dst.write(src.read())

        # 如果未指定输出路径，生成默认输出路径
        if output_path is None:
            source_dir = os.path.dirname(source_path)
            source_name = os.path.basename(source_path)
            module_name = os.path.splitext(source_name)[0]
            output_path = os.path.join(source_dir, f"{module_name}.pyz")

        # 检查源目录是否有 __main__.py
        has_main_py = os.path.exists(os.path.join(temp_dir, '__main__.py'))
        main_entry = f"{os.path.splitext(main_file_name)[0]}:main" if not has_main_py and hasattr(sys.modules['__main__'], 'main') else None

        # 使用zipapp打包临时目录
        zipapp.create_archive(temp_dir, output_path, main=main_entry)

        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)

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
        import time
        import struct

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

    def get_imported_modules(self) -> Set[str]:
        """获取分析到的导入模块"""
        return self.imported_modules