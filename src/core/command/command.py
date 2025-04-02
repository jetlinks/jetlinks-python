from typing import Dict, Any, Optional, TypeVar, Generic

T = TypeVar('T')


class Command(Generic[T]):
    """命令基类"""
    
    def __init__(self, command_id: str, inputs: Dict[str, Any]):
        self.id = command_id
        self.inputs = inputs
        self.stream = None
        
    def with_stream(self, stream) -> 'Command[T]':
        """设置流式数据"""
        self.stream = stream
        return self 