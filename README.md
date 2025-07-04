# Python虚拟机

这是一个简单的Python虚拟机实现，支持将Python代码编译为pyc文件并执行，同时提供图形界面和命令行工具。

## 功能特点

- 编辑Python源代码
- 将Python代码编译为pyc文件
- 执行pyc文件
- 文件管理和浏览
- 支持中文显示

## 安装
   
1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/pyvm.git
   ```
2. 安装依赖（无需额外依赖）

3. 安装项目：
   ```
   python setup.py install
   或者双击setup.exe
   ```

## 使用方法

### 图形界面
```
python -m pyvm gui
```
### 命令行工具

1. 编译Python文件：
   ```
   python -m pyvm compile <源文件> [输出文件]
   ```

2. 执行pyc文件：
   ```
   python -m pyvm execute <pyc文件>
   ```

3. 查看帮助：
   ```
   python -m pyvm help
   ```

## 项目结构
pyvm/
├── core/           # 核心功能模块
│   ├── compiler.py # 编译器
│   └── interpreter.py # 解释器
├── gui/            # 图形界面模块
│   └── main_window.py # 主窗口
├── tests/          # 测试代码
├── __main__.py     # 入口点
└── setup.py        # 打包配置
## 测试

运行测试：python -m unittest discover tests
## 贡献

欢迎贡献代码！请提交Pull Request或创建Issue。

## 许可证

本项目采用MIT许可证。
    