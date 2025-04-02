#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令支持使用示例
"""

import sys
import os
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rx
from rx import Observable
from rx import operators as ops

from src.core.command import Command, SimpleCommandSupport, CommandHandler, CommandSupportProviders
from src.core.metadata import FunctionMetadata, PropertyMetadata, DataTypeId


# 示例命令处理器
class GreetingCommandHandler(CommandHandler):
    """问候命令处理器"""
    
    def metadata(self) -> FunctionMetadata:
        # 创建属性元数据列表描述输入参数
        inputs = [
            PropertyMetadata("name", "姓名")
        ]
        # 创建函数元数据
        metadata = FunctionMetadata("greeting", "问候", inputs, DataTypeId.STRING)
        metadata.with_description("发送问候消息")
        return metadata
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        # 获取名称参数
        name = command.get("name", "Guest")
        
        # 创建问候消息
        greeting = f"你好，{name}！欢迎使用命令系统。"
        
        # 返回结果Observable
        return rx.of(greeting)


class MathCommandHandler(CommandHandler):
    """数学运算命令处理器"""
    
    def metadata(self) -> FunctionMetadata:
        # 创建属性元数据列表描述输入参数
        inputs = [
            PropertyMetadata("a", "第一个数"),
            PropertyMetadata("b", "第二个数"),
            PropertyMetadata("operation", "操作")
        ]
        # 创建函数元数据
        metadata = FunctionMetadata("math", "数学运算", inputs, DataTypeId.DOUBLE)
        metadata.with_description("执行基本的数学运算")
        return metadata
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        try:
            # 获取输入参数
            a = float(command.get("a", 0))
            b = float(command.get("b", 0))
            operation = command.get("operation", "add")
            
            # 根据操作执行不同的运算
            result = 0
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return rx.throw(Exception("除数不能为零"))
                result = a / b
            else:
                return rx.throw(Exception(f"不支持的操作: {operation}"))
            
            # 返回结果Observable
            return rx.of(result)
        except Exception as e:
            return rx.throw(Exception(f"执行运算出错: {str(e)}"))


# 流式命令处理器示例
class StreamProcessHandler(CommandHandler):
    """流处理命令处理器"""
    
    def metadata(self) -> FunctionMetadata:
        inputs = []
        metadata = FunctionMetadata("stream-process", "流处理", inputs, DataTypeId.STRING)
        metadata.with_description("处理输入流")
        return metadata
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        # 获取输入流
        stream = command.get("stream")
        if not stream:
            return rx.throw(Exception("需要一个输入流"))
        
        # 处理流数据：将每个元素转换为字符串并大写
        return stream.pipe(
            ops.map(lambda x: str(x).upper())
        )


def setup_command_system():
    # 创建命令支持
    support = SimpleCommandSupport()
    
    # 注册命令处理器
    support.register_handler(GreetingCommandHandler())
    support.register_handler(MathCommandHandler())
    support.register_handler(StreamProcessHandler())
    
    # 将命令支持注册到全局提供者
    CommandSupportProviders.register("example-service", support)
    
    return support


def run_examples():
    # 设置命令系统
    setup_command_system()
    
    print("===== 问候命令示例 =====")
    # 执行问候命令
    CommandSupportProviders.execute("example-service", "greeting", {"name": "张三"}).subscribe(
        on_next=lambda x: print(f"收到结果: {x}"),
        on_error=lambda e: print(f"出现错误: {e}"),
        on_completed=lambda: print("命令执行完成")
    )
    
    print("\n===== 数学命令示例 =====")
    # 执行数学命令
    operations = ["add", "subtract", "multiply", "divide"]
    for op in operations:
        CommandSupportProviders.execute("example-service", "math", {"a": 10, "b": 2, "operation": op}).subscribe(
            on_next=lambda x, op=op: print(f"{op} 操作结果: {x}"),
            on_error=lambda e, op=op: print(f"{op} 操作出错: {e}"),
            on_completed=lambda: None
        )
    
    # 测试错误情况
    CommandSupportProviders.execute("example-service", "math", {"a": 10, "b": 0, "operation": "divide"}).subscribe(
        on_next=lambda x: print(f"收到结果: {x}"),
        on_error=lambda e: print(f"预期的错误: {e}"),
        on_completed=lambda: None
    )
    
    print("\n===== 流处理命令示例 =====")
    # 创建测试流
    source = rx.from_iterable(["hello", "world", "rx", "python"])
    
    # 执行流处理命令
    CommandSupportProviders.execute_stream("example-service", "stream-process", {}, source).subscribe(
        on_next=lambda x: print(f"流处理结果: {x}"),
        on_error=lambda e: print(f"流处理错误: {e}"),
        on_completed=lambda: print("流处理完成")
    )


if __name__ == "__main__":
    run_examples() 