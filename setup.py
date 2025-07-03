from setuptools import setup, find_packages

setup(
    name='pyvm',
    version='1.0.0',
    description='一个简单的Python虚拟机实现',
    long_description='一个简单的Python虚拟机实现，支持将Python代码编译为pyc文件并执行，提供图形界面和命令行工具。',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/pyvm',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pyvm = pyvm.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[],
    python_requires='>=3.6',
)    