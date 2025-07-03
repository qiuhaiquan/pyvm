import unittest
import os
import tempfile
from pyvm.core.compiler import PyCompiler
from pyvm.core.interpreter import PyInterpreter
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

class TestPyInterpreter(unittest.TestCase):
    def setUp(self):
        self.compiler = PyCompiler()
        self.interpreter = PyInterpreter()
    
    def test_execute_pyc(self):
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('Hello from pyc!')")
            temp_file = f.name
        
        try:
            # 编译文件
            pyc_path = self.compiler.compile_file(temp_file)
            
            # 执行pyc文件
            result = self.interpreter.execute_pyc(pyc_path)
            
            # 检查输出
            self.assertIn('Hello from pyc!', result)
        finally:
            # 清理临时文件
            os.unlink(temp_file)
            pyc_dir = os.path.dirname(pyc_path)
            if os.path.exists(pyc_dir) and not os.listdir(pyc_dir):
                os.rmdir(pyc_dir)
    
    def test_execute_code_object(self):
        source_code = "print('Hello from code object!')"
        
        # 解析源代码为AST
        import ast
        tree = ast.parse(source_code, filename='<string>')
        
        # 编译AST为字节码对象
        code_object = compile(tree, filename='<string>', mode='exec')
        
        # 执行字节码对象
        result = self.interpreter.execute_code_object(code_object)
        
        # 检查输出
        self.assertIn('Hello from code object!', result)

if __name__ == '__main__':
    unittest.main()    