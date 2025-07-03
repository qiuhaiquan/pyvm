import unittest
import os
import tempfile
from pyvm.core.compiler import PyCompiler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

class TestPyCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = PyCompiler()
    
    def test_compile_file(self):
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('Hello, World!')")
            temp_file = f.name
        
        try:
            # 编译文件
            pyc_path = self.compiler.compile_file(temp_file)
            
            # 检查pyc文件是否存在
            self.assertTrue(os.path.exists(pyc_path))
            
            # 检查pyc文件是否有内容
            self.assertTrue(os.path.getsize(pyc_path) > 0)
        finally:
            # 清理临时文件
            os.unlink(temp_file)
            pyc_dir = os.path.dirname(pyc_path)
            if os.path.exists(pyc_dir) and not os.listdir(pyc_dir):
                os.rmdir(pyc_dir)
    
    def test_compile_string(self):
        source_code = "print('Hello from string!')"
        
        try:
            # 编译字符串
            with tempfile.TemporaryDirectory() as temp_dir:
                pyc_path = os.path.join(temp_dir, 'test.pyc')
                self.compiler.compile_string(source_code, pyc_path)
                
                # 检查pyc文件是否存在
                self.assertTrue(os.path.exists(pyc_path))
                
                # 检查pyc文件是否有内容
                self.assertTrue(os.path.getsize(pyc_path) > 0)
        except Exception as e:
            self.fail(f"编译字符串时出错: {str(e)}")

if __name__ == '__main__':
    unittest.main()    