import sys
import argparse
from pathlib import Path
from pyvm.core.compiler import PyCompiler
from pyvm.core.interpreter import PyInterpreter
sys.path.append(str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description='Python虚拟机 - 编译和执行Python代码')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # 编译命令
    compile_parser = subparsers.add_parser('compile', help='编译Python文件为pyc文件')
    compile_parser.add_argument('source', help='源文件路径')
    compile_parser.add_argument('output', nargs='?', help='输出pyc文件路径')
    
    # 执行命令
    execute_parser = subparsers.add_parser('execute', help='执行pyc文件')
    execute_parser.add_argument('pyc_file', help='pyc文件路径')
    execute_parser.add_argument('--path', action='append', help='添加模块搜索路径')
    
    # 图形界面命令
    gui_parser = subparsers.add_parser('gui', help='启动图形界面')
    
    args = parser.parse_args()
    
    if args.command == 'compile':
        # 编译命令
        compiler = PyCompiler()
        output_path = compiler.compile_file(args.source, args.output)
        print(f"已编译为: {output_path}")
        print(f"导入的模块: {', '.join(compiler.get_imported_modules()) or '无'}")
    
    elif args.command == 'execute':
        # 执行命令
        module_search_paths = args.path or []
        interpreter = PyInterpreter(module_search_paths)
        interpreter.execute_pyc(args.pyc_file)

    if args.command == 'gui':
        from pyvm.gui.main_window import main
        main()


    else:
        # 图形界面命令
        from pyvm.gui.main_window import main
        main()

if __name__ == "__main__":
    main()    