#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行所有单元测试的脚本
"""

import unittest
import sys
import os


def run_tests():
    """发现并运行所有测试"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 发现测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(current_dir, 'tests'), pattern='test_*.py')
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 根据测试结果设置退出代码
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests()) 