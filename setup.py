from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jetlinks-core",
    version="0.1.0",
    author="Zhou Hao",
    author_email="admin@hsweb.me",  # 作者邮箱
    description="Python implementation for JetLinks core functionalities",  # 简短描述
    long_description=long_description,  # 长描述
    long_description_content_type="text/markdown",  # 长描述格式
    url="https://github.com/yourusername/jetlinks",  # 项目URL
    packages=find_packages(),  # 自动发现包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",  # 已修改为Apache 2.0
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python版本要求
    install_requires=[
        "rx>=3.2.0",
    ],
    license="Apache License 2.0",  # 添加明确的许可证字段
) 