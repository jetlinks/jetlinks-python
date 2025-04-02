import unittest
from typing import Dict, Any, List
import rx
from rx import Observable
from rx import operators as ops

from src.core.command import SimpleCommandSupport, Command, CommandHandler
from  src.core.metadata import FunctionMetadata, PropertyMetadata, DataTypeId


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


class TestSimpleCommandSupport(unittest.TestCase):
    def setUp(self):
        # 创建一个空的SimpleCommandSupport
        self.support = SimpleCommandSupport()
        
        # 创建测试处理器
        self.handler1 = MockCommandHandler("test-command-1", "测试命令1", "测试结果1")
        self.handler2 = MockCommandHandler("test-command-2", "测试命令2", "测试结果2")
    
    def test_register_and_execute_handler(self):
        """测试注册和执行处理器"""
        # 注册处理器
        self.support.register_handler(self.handler1)
        
        # 检查命令是否存在
        self.assertTrue(self.support.has_command("test-command-1"))
        self.assertFalse(self.support.has_command("test-command-2"))
        
        # 执行命令
        command = Command("test-command-1", {})
        result = []
        self.support.execute(command).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(result, ["测试结果1"])
    
    def test_unregister_handler(self):
        """测试取消注册处理器"""
        # 注册处理器
        self.support.register_handler(self.handler1)
        self.support.register_handler(self.handler2)
        
        # 确认命令已注册
        self.assertTrue(self.support.has_command("test-command-1"))
        self.assertTrue(self.support.has_command("test-command-2"))
        
        # 取消注册handler1
        self.support.unregister_handler("test-command-1")
        
        # 确认handler1已被移除，handler2仍然存在
        self.assertFalse(self.support.has_command("test-command-1"))
        self.assertTrue(self.support.has_command("test-command-2"))
        
        # 尝试执行已删除的命令
        command = Command("test-command-1", {})
        error_caught = [False]
        
        def on_error(e):
            self.assertIn("不支持的命令", str(e))
            error_caught[0] = True
        
        self.support.execute(command).subscribe(
            on_next=lambda x: self.fail("不应该执行到这里"),
            on_error=on_error
        )
        
        self.assertTrue(error_caught[0])
    
    def test_get_command_metadata(self):
        """测试获取命令元数据"""
        # 注册处理器
        self.support.register_handler(self.handler1)
        
        # 获取命令元数据
        metadata_list = []
        self.support.get_command_metadata("test-command-1").subscribe(
            on_next=lambda x: metadata_list.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(len(metadata_list), 1)
        self.assertEqual(metadata_list[0].id, "test-command-1")
        self.assertEqual(metadata_list[0].name, "测试命令1")
        
        # 获取不存在的命令元数据
        metadata_list = []
        self.support.get_command_metadata("non-existent-command").subscribe(
            on_next=lambda x: metadata_list.append(x)
        )
        
        self.assertEqual(len(metadata_list), 0)
    
    def test_get_all_command_metadata(self):
        """测试获取所有命令元数据"""
        # 注册处理器
        self.support.register_handler(self.handler1)
        self.support.register_handler(self.handler2)
        
        # 获取所有命令元数据
        metadata_list = []
        self.support.get_all_command_metadata().subscribe(
            on_next=lambda x: metadata_list.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(len(metadata_list), 2)
        metadata_ids = {metadata.id for metadata in metadata_list}
        self.assertEqual(metadata_ids, {"test-command-1", "test-command-2"})
    
    def test_constructor_with_handlers(self):
        """测试带处理器的构造函数"""
        # 创建带有处理器的支持
        handlers = [self.handler1, self.handler2]
        support = SimpleCommandSupport(handlers)
        
        # 检查命令是否都注册了
        self.assertTrue(support.has_command("test-command-1"))
        self.assertTrue(support.has_command("test-command-2"))
        
        # 执行命令
        command = Command("test-command-2", {})
        result = []
        support.execute(command).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(result, ["测试结果2"])
        
    def test_execute_with_stream(self):
        """测试使用流执行命令"""
        class StreamTestHandler(CommandHandler):
            def metadata(self) -> FunctionMetadata:
                return FunctionMetadata("stream-test", "流测试", [], DataTypeId.STRING)
            
            def execute(self, command: Dict[str, Any]) -> Observable:
                stream = command.get("stream")
                if not stream:
                    return rx.throw(Exception("需要流"))
                return stream.pipe(
                    ops.map(lambda x: f"处理: {x}")
                )
        
        # 注册流处理器
        self.support.register_handler(StreamTestHandler())
        
        # 创建测试流
        source = rx.from_iterable([1, 2, 3])
        
        # 创建命令
        command = Command("stream-test", {})
        command.stream = source
        
        # 执行命令
        result = []
        self.support.execute(command).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: self.fail(f"发生错误: {e}")
        )
        
        self.assertEqual(result, ["处理: 1", "处理: 2", "处理: 3"])


if __name__ == "__main__":
    unittest.main() 