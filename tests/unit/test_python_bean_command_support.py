import unittest
import rx
from rx import Observable

from src import Command
from src.core.command import command_handler, create_python_bean_command_support


class TestCommands:
    """测试命令类"""
    
    @command_handler(
        name="测试加法",
        description="测试加法命令",
        expands={"test": True}
    )
    def add(self, a: int, b: int) -> int:
        """加法测试"""
        return a + b
    
    @command_handler(command_id="custom-id")
    def custom_id_method(self, message: str) -> str:
        """带有自定义ID的方法"""
        return f"Echo: {message}"
    
    @command_handler(ignore=True)
    def ignored_method(self):
        """被忽略的方法"""
        return "This should be ignored"
    
    @command_handler()
    def error_method(self):
        """抛出异常的方法"""
        raise ValueError("Test error")
    
    @command_handler()
    def rx_method(self, value: int) -> Observable:
        """返回Observable的方法"""
        return rx.just(value * 2)


class PythonBeanCommandSupportTest(unittest.TestCase):
    """测试PythonBeanCommandSupport"""
    
    def setUp(self):
        self.commands = TestCommands()
        self.command_support = create_python_bean_command_support(self.commands)
    
    def test_command_registration(self):
        """测试命令注册"""
        # 应该注册3个命令 (add, custom-id, error_method, rx_method)，忽略1个 (ignored_method)
        metadata_list = []
        self.command_support.get_all_command_metadata().subscribe(
            on_next=lambda metadata: metadata_list.append(metadata)
        )
        
        self.assertEqual(4, len(metadata_list))
        
        # 验证命令ID存在
        command_ids = [metadata.id for metadata in metadata_list]
        self.assertIn("add", command_ids)
        self.assertIn("custom-id", command_ids)
        self.assertIn("error_method", command_ids)
        self.assertIn("rx_method", command_ids)
        self.assertNotIn("ignored_method", command_ids)
    
    def test_execute_command(self):
        """测试执行命令"""
        # 测试加法命令
        add_command = Command("add", {"a": 5, "b": 7})
        result = None
        error = None
        
        def on_next(value):
            nonlocal result
            result = value
        
        def on_error(err):
            nonlocal error
            error = err
        
        self.command_support.execute(add_command).subscribe(
            on_next=on_next,
            on_error=on_error
        )
        
        self.assertEqual(12, result)
        self.assertIsNone(error)
    
    def test_custom_id_command(self):
        """测试自定义ID的命令"""
        # 测试自定义ID命令
        custom_command = Command("custom-id", {"message": "Hello"})
        result = None
        
        def on_next(value):
            nonlocal result
            result = value
        
        self.command_support.execute(custom_command).subscribe(
            on_next=on_next
        )
        
        self.assertEqual("Echo: Hello", result)
    
    def test_error_command(self):
        """测试抛出异常的命令"""
        error_command = Command("error_method", {})
        result = None
        error = None
        
        def on_next(value):
            nonlocal result
            result = value
        
        def on_error(err):
            nonlocal error
            error = err
        
        self.command_support.execute(error_command).subscribe(
            on_next=on_next,
            on_error=on_error
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIsInstance(error, ValueError)
        self.assertEqual("Test error", str(error))
    
    def test_rx_command(self):
        """测试返回Observable的命令"""
        rx_command = Command("rx_method", {"value": 10})
        result = None
        
        def on_next(value):
            nonlocal result
            result = value
        
        self.command_support.execute(rx_command).subscribe(
            on_next=on_next
        )
        
        self.assertEqual(20, result)
    
    def test_unknown_command(self):
        """测试不存在的命令"""
        unknown_command = Command("unknown", {})
        result = None
        error = None
        
        def on_next(value):
            nonlocal result
            result = value
        
        def on_error(err):
            nonlocal error
            error = err
        
        self.command_support.execute(unknown_command).subscribe(
            on_next=on_next,
            on_error=on_error
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("不支持的命令", str(error))
    
    def test_metadata(self):
        """测试元数据"""
        metadata = None
        handler = None
        
        # 获取处理器
        for cmd_id, cmd_handler in self.command_support.handlers.items():
            if cmd_id == "add":
                handler = cmd_handler
                break
        
        self.assertIsNotNone(handler)
        
        # 获取元数据
        def on_next(value):
            nonlocal metadata
            metadata = value
        
        self.command_support.get_command_metadata("add").subscribe(
            on_next=on_next
        )
        
        self.assertIsNotNone(metadata)
        self.assertEqual("add", metadata.id)
        self.assertEqual("测试加法", metadata.name)
        self.assertEqual("测试加法命令", metadata.description)
        
        # 测试扩展属性
        self.assertTrue(handler.get_expands()["test"])


if __name__ == "__main__":
    unittest.main() 