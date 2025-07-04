import unittest
import os
import tempfile
from pyvm.core.compiler import PyCompiler

class TestPyCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = PyCompiler()

    def test_compile_file(self):
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import math\nprint('Hello, World!')")
            temp_file = f.name

        try:
            # 编译文件
            pyz_path = self.compiler.compile_file(temp_file)

            # 检查pyz文件是否存在
            self.assertTrue(os.path.exists(pyz_path))

            # 检查pyz文件是否有内容
            self.assertTrue(os.path.getsize(pyz_path) > 0)
        finally:
            # 清理临时文件
            os.unlink(temp_file)
            if os.path.exists(pyz_path):
                os.unlink(pyz_path)