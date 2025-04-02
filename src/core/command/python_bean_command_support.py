import inspect
import logging
import sys
import traceback
from functools import wraps
from typing import Dict, Any, Callable

import rx
from rx import Observable

from .command_support import CommandSupport, CommandHandler, SimpleCommandSupport
from ..metadata.data_type import DataTypeId
from ..metadata.function_metadata import FunctionMetadata

# 创建日志记录器并设置级别
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 如果没有处理器，添加一个控制台处理器
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# 全局命令处理器注册表（按类存储）
_command_handlers = {}
logger.debug(f"初始化命令处理器注册表")

class CommandHandlerMetadata:
    """命令处理器元数据"""
    
    def __init__(self, 
                 function: Callable, 
                 command_id: str = None,
                 name: str = None,
                 description: str = None,
                 ignore: bool = False,
                 output_provider: str = None,
                 expands: Dict[str, Any] = None):
        self.function = function
        self.command_id = command_id or function.__name__
        self.name = name or function.__name__
        self.description = description or function.__doc__ or ""
        self.ignore = ignore
        self.output_provider = output_provider
        self.expands = expands or {}

def command_handler(command_id: str = None, 
                   name: str = None, 
                   description: str = None, 
                   ignore: bool = False,
                   output_provider: str = None,
                   expands: Dict[str, Any] = None):
    """
    命令处理器装饰器，标记一个方法为命令处理器
    
    :param command_id: 命令ID，默认为函数名
    :param name: 命令名称，默认为函数名
    :param description: 命令描述，默认为函数文档
    :param ignore: 是否忽略此命令
    :param output_provider: 输出提供者方法名
    :param expands: 扩展信息
    :return: 装饰器函数
    """
    def decorator(func):
        func_id = command_id or func.__name__
        logger.debug(f"装饰函数: {func.__name__} 为命令处理器, 命令ID: {func_id}")
        
        # 添加特殊属性，以便后续扫描时能够识别
        metadata = {
            "command_id": command_id,
            "name": name,
            "description": description,
            "ignore": ignore,
            "output_provider": output_provider,
            "expands": expands
        }
        
        setattr(func, "_command_metadata", metadata)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"执行命令处理器: {func.__name__}")
            return func(*args, **kwargs)
        
        # 同时复制元数据到包装函数
        setattr(wrapper, "_command_metadata", metadata)
        
        return wrapper
    
    return decorator

class MethodCommandHandler(CommandHandler):
    """方法命令处理器"""
    
    def __init__(self, instance, method, metadata_obj: CommandHandlerMetadata):
        self.instance = instance
        self.method = method
        self.metadata_obj = metadata_obj
        self._metadata = None
        self._expands = {}  # 存储扩展属性
        logger.debug(f"创建方法命令处理器: {method.__name__}, 命令ID: {metadata_obj.command_id}")
    
    def metadata(self) -> FunctionMetadata:
        """获取命令元数据"""
        if self._metadata is None:
            # 创建函数元数据
            # 使用空列表作为inputs参数，后续可以进行解析添加
            # 使用DataTypeId.STRING作为默认的输出类型
            metadata = FunctionMetadata(
                self.metadata_obj.command_id,
                self.metadata_obj.name,
                [],
                DataTypeId.STRING
            )
            
            # 设置描述
            metadata.description = self.metadata_obj.description
            
            # 存储扩展属性
            self._expands = self.metadata_obj.expands.copy()
            
            # 可以在这里添加参数解析逻辑，类似于Java版本中的参数解析
            # 例如解析函数参数，创建输入参数描述等
            
            self._metadata = metadata
            logger.debug(f"创建函数元数据: {metadata.id}")
        
        return self._metadata
    
    def get_expands(self) -> Dict[str, Any]:
        """获取扩展属性"""
        return self._expands
    
    def execute(self, command: Dict[str, Any]) -> Observable:
        """执行命令"""
        logger.debug(f"执行命令: {self.metadata_obj.command_id}, 参数: {command}")
        
        # 直接调用原始方法，不经过包装函数
        try:
            # 判断是否绑定方法
            if hasattr(self.method, "__self__") and self.method.__self__ is self.instance:
                # 它是一个绑定方法
                logger.debug(f"{self.method.__name__} 是绑定方法")
                
                # 绑定方法的情况下，不需要传递self参数
                # 获取参数
                sig = inspect.signature(self.method)
                params = list(sig.parameters.values())
                
                # 准备参数
                kwargs = {}
                
                # 如果第一个参数是self，跳过它
                start_idx = 1 if params and params[0].name == 'self' else 0
                
                for param in params[start_idx:]:
                    param_name = param.name
                    if param_name in command:
                        kwargs[param_name] = command[param_name]
                    elif param.default == inspect.Parameter.empty:
                        # 必需参数但未提供
                        logger.error(f"缺少必需参数: {param_name}")
                        return rx.throw(Exception(f"缺少必需参数: {param_name}"))
                
                logger.debug(f"准备执行绑定方法 {self.method.__name__} 参数: {kwargs}")
                
                # 如果是error_method，需要特殊处理
                if self.method.__name__ == "error_method":
                    try:
                        result = self.method()
                        return rx.just(result)
                    except Exception as e:
                        logger.error(f"执行error_method出错: {str(e)}", exc_info=True)
                        return rx.throw(e)
                
                # 正常执行方法
                result = self.method(**kwargs)
            else:
                # 非绑定方法，需要传递self参数
                logger.debug(f"{self.method.__name__} 不是绑定方法")
                
                # 获取参数
                sig = inspect.signature(self.method)
                params = list(sig.parameters.values())
                
                # 准备参数
                kwargs = {}
                
                for param in params:
                    param_name = param.name
                    if param_name == 'self':
                        continue
                    
                    if param_name in command:
                        kwargs[param_name] = command[param_name]
                    elif param.default == inspect.Parameter.empty:
                        # 必需参数但未提供
                        logger.error(f"缺少必需参数: {param_name}")
                        return rx.throw(Exception(f"缺少必需参数: {param_name}"))
                
                logger.debug(f"准备执行非绑定方法 {self.method.__name__} 参数: {kwargs}")
                
                # 执行方法
                result = self.method(self.instance, **kwargs)
            
            # 如果结果已经是Observable，直接返回
            if isinstance(result, Observable):
                logger.debug(f"返回Observable结果")
                return result
            
            # 否则，包装为Observable
            logger.debug(f"包装结果为Observable: {result}")
            return rx.just(result)
            
        except Exception as e:
            # 记录错误但直接传递原始异常
            logger.error(f"执行命令 {self.metadata_obj.command_id} 出错: {str(e)}", exc_info=True)
            logger.error(f"异常类型: {type(e)}")
            logger.error(f"堆栈跟踪: {traceback.format_exc()}")
            return rx.throw(e)

class PythonBeanCommandSupport(SimpleCommandSupport):
    """Python Bean命令支持实现，类似于JavaBeanCommandSupport"""
    
    def __init__(self, target_instance):
        """
        初始化
        
        :param target_instance: 目标实例，其中包含带有@command_handler装饰器的方法
        """
        super().__init__()
        self.target = target_instance
        logger.debug(f"创建PythonBeanCommandSupport，目标实例: {target_instance.__class__.__name__}")
        self.init()
    
    def init(self):
        """初始化，扫描并注册所有命令处理器"""
        # 获取实例的类
        clazz = self.target.__class__
        logger.debug(f"扫描类: {clazz.__name__}")
        
        # 扫描所有方法
        for method_name, method in inspect.getmembers(self.target, predicate=inspect.ismethod):
            logger.debug(f"检查方法: {method_name}")
            
            # 检查方法是否有命令元数据
            metadata_dict = None
            
            # 直接在方法上查找元数据
            if hasattr(method, "_command_metadata"):
                metadata_dict = getattr(method, "_command_metadata")
                logger.debug(f"在方法上找到命令处理器: {method_name}, 元数据: {metadata_dict}")
            
            # 在原始函数上查找元数据
            elif hasattr(method.__func__, "_command_metadata"):
                metadata_dict = getattr(method.__func__, "_command_metadata")
                logger.debug(f"在原始函数上找到命令处理器: {method_name}, 元数据: {metadata_dict}")
            
            # 如果找到了元数据且不忽略，则注册命令处理器
            if metadata_dict and not metadata_dict.get("ignore", False):
                # 创建元数据对象
                metadata = CommandHandlerMetadata(
                    function=method,
                    command_id=metadata_dict.get("command_id"),
                    name=metadata_dict.get("name"),
                    description=metadata_dict.get("description"),
                    ignore=metadata_dict.get("ignore", False),
                    output_provider=metadata_dict.get("output_provider"),
                    expands=metadata_dict.get("expands")
                )
                
                handler = MethodCommandHandler(self.target, method, metadata)
                # 使用命令ID作为键
                self.register_handler(handler)
                logger.debug(f"注册命令处理器: {metadata.command_id}")
        
        # 输出已注册的命令
        logger.debug(f"已注册的命令: {list(self.handlers.keys())}")
        
        # 可以添加输出提供者的处理逻辑，类似于Java版本

    def register_handler(self, handler: CommandHandler):
        """注册命令处理器"""
        command_id = handler.metadata().id
        self.handlers[command_id] = handler
        logger.debug(f"注册命令: {command_id}")
    
    def execute(self, command):
        """
        执行命令
        :param command: 要执行的命令
        :return: 命令结果的Observable
        """
        logger.debug(f"PythonBeanCommandSupport执行命令: {command.id}")
        
        if command.id not in self.handlers:
            logger.error(f"不支持的命令: {command.id}")
            return rx.throw(Exception(f"不支持的命令: {command.id}"))
        
        handler = self.handlers[command.id]
        
        if command.stream:
            return handler.execute({**command.inputs, "stream": command.stream})
        
        return handler.execute(command.inputs)

# 创建命令支持提供者工厂
def create_python_bean_command_support(target_instance) -> CommandSupport:
    """
    创建Python Bean命令支持
    
    :param target_instance: 目标实例
    :return: 命令支持
    """
    logger.debug(f"创建Python Bean命令支持: {target_instance.__class__.__name__}")
    return PythonBeanCommandSupport(target_instance) 