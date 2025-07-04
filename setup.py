from setuptools import setup, find_packages

setup(
    name='pyvm',
    version='0.1',
    description='一个简单的Python虚拟机实现，支持将Python代码编译为pyc文件并执行，同时提供图形界面和命令行工具。',
    author='qiuhaiquan',
    author_email='1836244962@qq.com',
    url='https://github.com/yourusername/pyvm.git',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "altgraph",
        "packaging",
        "pefile",
        "pip",
        "pyinstaller",
        "setuptools",
        "pyinstaller-hooks-contrib",
        "pywin32-ctypes",
    ],
    entry_points={
        'console_scripts': [
            'pyvm = pyvm.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)