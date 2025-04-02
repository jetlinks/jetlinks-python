# Python命令支持

本模块提供了类似于Java中的`CommandHandler`注解和`JavaBeanCommandSupport`的功能，允许通过装饰器自动注册命令。

## 功能概述

- `command_handler` 装饰器：用于将方法标记为命令处理器
- `PythonBeanCommandSupport`：扫描带有装饰器的方法并注册为命令处理器
- 支持同步和异步（Observable）命令处理
- 支持命令元数据
- 支持扩展属性

## 如何使用

### 1. 创建命令处理类

```python
from scripts.command.python_bean_command_support import command_handler
import rx

class MyCommands:
    """我的命令处理类"""
    
    @command_handler(
        name="加法命令",
        description="计算两个数的和",
        expands={"example": "add(1, 2)"}
    )
    def add(self, a: int, b: int) -> int:
        """
        计算两个数的和
        :param a: 第一个数
        :param b: 第二个数
        :return: 和
        """
        return a + b
    
    @command_handler(command_id="custom-id")
    def custom_id_method(self, message: str) -> str:
        """自定义ID的方法"""
        return f"Echo: {message}"
    
    @command_handler(ignore=True)
    def internal_method(self):
        """
        内部方法，不会被注册为命令
        """
        pass
    
    @command_handler()
    def async_method(self, value: int) -> rx.Observable:
        """返回Observable的异步方法"""
        return rx.just(value * 2)
```

### 2. 创建命令支持

```python
from scripts.command.python_bean_command_support import create_python_bean_command_support

# 创建命令实例
my_commands = MyCommands()

# 创建命令支持
command_support = create_python_bean_command_support(my_commands)
```

### 3. 执行命令

```python
from scripts.command.command import Command

# 创建命令
add_command = Command("add", {"a": 10, "b": 20})

# 执行命令并获取结果
command_support.execute(add_command).subscribe(
    on_next=lambda result: print(f"结果: {result}"),
    on_error=lambda err: print(f"错误: {err}")
)
```

### 4. 获取命令元数据

```python
# 获取所有命令元数据
command_support.get_all_command_metadata().subscribe(
    on_next=lambda metadata: print(f"- {metadata.id}: {metadata.name} - {metadata.description}")
)

# 获取特定命令的元数据
command_support.get_command_metadata("add").subscribe(
    on_next=lambda metadata: print(f"命令: {metadata.name} ({metadata.id})")
)

# 获取扩展属性
add_handler = command_support.handlers["add"]
expands = add_handler.get_expands()
print(f"示例: {expands.get('example')}")
```

## 装饰器参数

`command_handler` 装饰器支持以下参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| command_id | str | 命令ID，默认为函数名 |
| name | str | 命令名称，默认为函数名 |
| description | str | 命令描述，默认为函数文档 |
| ignore | bool | 是否忽略此命令，默认为False |
| output_provider | str | 输出提供者方法名 |
| expands | Dict[str, Any] | 扩展信息 |

## 实现说明

该实现使用了以下关键组件：

- `FunctionMetadata`：用于存储命令元数据
- `MethodCommandHandler`：将方法转换为命令处理器
- `PythonBeanCommandSupport`：扫描并注册所有带有装饰器的方法

扩展属性通过`MethodCommandHandler.get_expands()`方法获取，而不是直接存储在`FunctionMetadata`对象中。

## 示例

完整示例见 `/examples/command_handler_example.py`，其中演示了如何：
1. 创建带有命令处理器的类
2. 注册并执行各种类型的命令
3. 处理命令异常
4. 使用异步命令

## 单元测试

单元测试代码见 `/tests/test_python_bean_command_support.py`，演示了如何测试命令处理器功能。

## 与Java版本的区别

Python实现与Java版本基本一致，但有以下区别：

1. 使用Python装饰器而非Java注解
2. 使用rx观察者模式实现异步处理
3. 简化了参数传递，使用Python的关键字参数
4. 扩展属性通过单独的方法获取
5. 目前不支持参数验证，可以在命令处理方法中自行验证 