import unittest
from typing import Dict, Any
import sys
import os

# 添加父目录到Python路径最前面
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import rx
from rx import Observable
from rx import operators as ops

from src import CommandSupportProviders, CommandSupport, SimpleCommandSupport, Command, CommandHandler
from src import FunctionMetadata, DataTypeId


# 模拟的命令处理器类
class MockCommandHandler(CommandHandler):
    def __init__(self, command_id: str, name: str, result: Any = None):
        self._command_id = command_id
        self._name = name
        self._result = result
        
    def metadata(self) -> FunctionMetadata:
        return FunctionMetadata(self._command_id, self._name, [], DataTypeId.STRING)
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        def subscribe(observer, scheduler=None):
            observer.on_next(self._result or command)
            observer.on_completed()
        
        return Observable(subscribe)


# 测试用的流式命令处理器类
class StreamCommandHandler(CommandHandler):
    def metadata(self) -> FunctionMetadata:
        return FunctionMetadata("stream-command", "流式命令", [], DataTypeId.STRING)
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        stream = command.get("stream")
        if not stream:
            return rx.throw(Exception("需要流式数据"))
        
        # 将流中的每个元素转换为大写
        return stream.pipe(
            ops.map(lambda x: str(x).upper())
        )


class TestCommandSupportProviders(unittest.TestCase):
    def setUp(self):
        # 重置CommandSupportProviders中的supports字典
        CommandSupportProviders._supports = {}
        
        # 创建一个简单的命令支持实例，并添加一些测试命令处理器
        self.support = SimpleCommandSupport()
        self.support.register_handler(MockCommandHandler("test-command", "测试命令", "测试结果"))
        self.support.register_handler(MockCommandHandler("echo-command", "回显命令"))
        self.support.register_handler(StreamCommandHandler())
        
        # 将命令支持注册到提供者
        CommandSupportProviders.register("test-service", self.support)
    
    def test_register_and_get(self):
        """测试注册和获取命令支持"""
        # 获取已注册的命令支持
        support = CommandSupportProviders.get("test-service")
        self.assertIsNotNone(support)
        self.assertEqual(support, self.support)
        
        # 获取未注册的命令支持
        support = CommandSupportProviders.get("non-existent-service")
        self.assertIsNone(support)
    
    def test_execute_command(self):
        """测试执行命令"""
        # 执行测试命令
        result = []
        CommandSupportProviders.execute("test-service", "test-command", {}).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(result, ["测试结果"])
        
        # 执行回显命令
        result = []
        test_input = {"key": "value"}
        CommandSupportProviders.execute("test-service", "echo-command", test_input).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(result, [test_input])
    
    def test_execute_nonexistent_service(self):
        """测试执行不存在的服务"""
        # 尝试执行不存在的服务
        error_caught = [False]
        
        def on_error(e):
            self.assertIn("不支持的服务", str(e))
            error_caught[0] = True
        
        CommandSupportProviders.execute("non-existent-service", "test-command", {}).subscribe(
            on_next=lambda x: self.fail("不应该执行到这里"),
            on_error=on_error
        )
        
        self.assertTrue(error_caught[0])
    
    def test_execute_nonexistent_command(self):
        """测试执行不存在的命令"""
        # 尝试执行不存在的命令
        error_caught = [False]
        
        def on_error(e):
            self.assertIn("不支持的命令", str(e))
            error_caught[0] = True
        
        CommandSupportProviders.execute("test-service", "non-existent-command", {}).subscribe(
            on_next=lambda x: self.fail("不应该执行到这里"),
            on_error=on_error
        )
        
        self.assertTrue(error_caught[0])
    
    def test_execute_stream(self):
        """测试执行流式命令"""
        # 创建测试数据流
        source = rx.from_iterable(["hello", "world", "rx"])
        
        # 执行流式命令
        result = []
        CommandSupportProviders.execute_stream("test-service", "stream-command", {}, source).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        # 验证结果
        self.assertEqual(result, ["HELLO", "WORLD", "RX"])
    
    def test_execute_stream_nonexistent_service(self):
        """测试在不存在的服务上执行流式命令"""
        # 创建测试数据流
        source = rx.from_iterable(["hello", "world", "rx"])
        
        # 尝试在不存在的服务上执行流式命令
        error_caught = [False]
        
        def on_error(e):
            self.assertIn("不支持的服务", str(e))
            error_caught[0] = True
        
        CommandSupportProviders.execute_stream("non-existent-service", "stream-command", {}, source).subscribe(
            on_next=lambda x: self.fail("不应该执行到这里"),
            on_error=on_error
        )
        
        self.assertTrue(error_caught[0])


if __name__ == "__main__":
    unittest.main() 