import ast
import inspect
import os
import re
from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

class CodeSecurityChecker:
    """代码安全检查器，用于在执行前分析Python代码是否包含危险操作"""
    
    # 危险函数列表
    DANGEROUS_FUNCTIONS = {
        'os': ['system', 'popen', 'popen2', 'popen3', 'popen4', 'execl', 'execle', 'execlp', 
               'execlpe', 'execv', 'execve', 'execvp', 'execvpe', 'fork', 'forkpty'],
        'subprocess': ['run', 'call', 'check_call', 'check_output', 'Popen'],
        'shutil': ['rmtree', 'move', 'copytree'],
        'sys': ['exit', 'setprofile', 'settrace'],
        'builtins': ['eval', 'exec', 'open', 'compile', 'input']
    }
    
    # 危险模块列表
    DANGEROUS_MODULES = ['ctypes', 'imp', 'importlib', 'msvcrt', 'pdb', 'pty', 'readline', 'signal']
    
    def __init__(self, allow_list=None, deny_list=None):
        """
        初始化安全检查器
        
        Args:
            allow_list: 允许的操作白名单
            deny_list: 禁止的操作黑名单
        """
        self.allow_list = allow_list or []
        self.deny_list = deny_list or []
        
    def check_code(self, code: str, filename: str = "<string>") -> Tuple[bool, List[str]]:
        """
        检查代码安全性
        
        Args:
            code: 要检查的Python代码
            filename: 代码文件名称
            
        Returns:
            (安全状态, 危险信息列表)
        """
        try:
            # 解析代码为AST
            tree = ast.parse(code, filename=filename)
            
            # 初始化危险信息列表
            issues = []
            
            # 检查导入的模块
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in self.DANGEROUS_MODULES and name.name not in self.allow_list:
                            issues.append(f"危险导入: import {name.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.DANGEROUS_MODULES and node.module not in self.allow_list:
                        issues.append(f"危险导入: from {node.module} import ...")
            
            # 检查危险函数调用
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # 处理函数调用
                    func_name = self._get_function_name(node.func)
                    if func_name:
                        module_name, func_base_name = self._split_function_name(func_name)
                        
                        # 检查是否在危险函数列表中
                        if module_name in self.DANGEROUS_FUNCTIONS:
                            if func_base_name in self.DANGEROUS_FUNCTIONS[module_name] and \
                               func_name not in self.allow_list:
                                issues.append(f"危险函数调用: {func_name}")
            
            # 检查系统命令执行模式
            if re.search(r'os\.system\(|subprocess\.run\(', code):
                issues.append("发现系统命令执行代码")
            
            # 检查文件操作权限
            if re.search(r'open\([^)]*, *[\'"]w[\'"]', code) or re.search(r'open\([^)]*, *[\'"]a[\'"]', code):
                issues.append("发现写文件操作")
            
            # 检查网络连接
            if re.search(r'socket\.socket\(', code) or re.search(r'urllib\.request\.urlopen\(', code):
                issues.append("发现网络连接操作")
            
            return (len(issues) == 0, issues)
            
        except SyntaxError as e:
            return (False, [f"语法错误: {str(e)}"])
    
    def _get_function_name(self, node) -> str:
        """获取函数调用的完整名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        return ""
    
    def _get_attribute_name(self, node) -> str:
        """获取属性访问的完整名称"""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return ""
    
    def _split_function_name(self, func_name: str) -> Tuple[str, str]:
        """分割函数名称为模块名和函数基本名"""
        parts = func_name.split('.')
        if len(parts) > 1:
            return (parts[0], parts[-1])
        return (None, func_name)    