from typing import Dict, Any
from abc import ABC, abstractmethod

from jetlinks_plugin.core.plugin import PluginType, Plugin, PluginContext


class PluginDriver(ABC):
    """插件驱动，用于创建插件"""
    
    def __init__(self, plugin_type: PluginType):
        """
        初始化插件驱动
        
        Args:
            plugin_type: 插件类型
        """
        self.type = plugin_type
    
    @abstractmethod
    def create_plugin(self, ctx: PluginContext) -> Plugin:
        """
        创建插件
        
        Args:
            ctx: 插件上下文
            
        Returns:
            创建的插件实例
        """
        pass
    
    def __str__(self) -> str:
        return f"PluginDriver(type={self.type})"
        
    def __repr__(self) -> str:
        return self.__str__()


# 示例实现
class SimplePluginDriver(PluginDriver):
    """简单插件驱动示例实现"""
    
    def __init__(self, plugin_type: PluginType, creator_func=None):
        """
        初始化简单插件驱动
        
        Args:
            plugin_type: 插件类型
            creator_func: 创建插件的函数，如果提供，将使用此函数创建插件
        """
        super().__init__(plugin_type)
        self._creator_func = creator_func
        
    def create_plugin(self, ctx: PluginContext) -> Plugin:
        """
        创建插件
        
        Args:
            ctx: 插件上下文
            
        Returns:
            创建的插件实例
        """
        if self._creator_func:
            return self._creator_func(ctx)
        
        # 默认实现返回一个基本插件
        return BasePlugin(ctx)


class BasePlugin(Plugin):
    """基本插件实现"""
    
    def __init__(self, context: PluginContext):
        """
        初始化基本插件
        
        Args:
            context: 插件上下文
        """
        super().__init__(context)
        self.running = False
        
    def execute_command(self, command_id: str, args: Dict[str, Any]) -> Any:
        """
        执行命令
        
        Args:
            command_id: 命令ID
            args: 命令参数
            
        Returns:
            命令执行结果
        """
        if command_id == "status":
            return {"running": self.running}
        elif command_id == "start":
            return self.start()
        elif command_id == "stop":
            return self.stop()
        else:
            raise ValueError(f"不支持的命令: {command_id}")
    
    def start(self) -> None:
        """启动插件"""
        self.context.monitor().log_info("插件启动中...")
        self.running = True
        self.context.monitor().log_info("插件已启动")
        
    def stop(self) -> None:
        """停止插件"""
        self.context.monitor().log_info("插件停止中...")
        self.running = False
        self.context.monitor().log_info("插件已停止")


# 使用示例
def create_example_plugin():
    """创建示例插件驱动和插件"""
    # 1. 创建插件类型
    plugin_type = PluginType("example", "示例插件")
    
    # 2. 创建插件驱动
    plugin_driver = SimplePluginDriver(plugin_type)
    
    # 3. 创建插件上下文
    config = {
        "name": "测试插件",
        "version": "1.0.0",
        "settings": {
            "timeout": 30,
            "retry": 3
        }
    }
    plugin_context = PluginContext(config)
    
    # 4. 创建插件实例
    plugin = plugin_driver.create_plugin(plugin_context)
    
    return plugin 