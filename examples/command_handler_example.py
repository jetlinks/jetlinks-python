import rx
from rx import Observable

from ..src.core.command.command import Command
from ..src.core.command.python_bean_command_support import command_handler, create_python_bean_command_support


class MathCommands:
    """数学计算命令示例"""
    
    @command_handler(
        name="加法计算",
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
    
    @command_handler(
        command_id="subtract",
        name="减法计算",
        description="计算两个数的差"
    )
    def sub(self, a: int, b: int) -> int:
        """
        计算两个数的差
        :param a: 第一个数
        :param b: 第二个数
        :return: 差
        """
        return a - b
    
    @command_handler(
        name="乘法计算",
        description="计算两个数的乘积"
    )
    def multiply(self, a: int, b: int) -> int:
        """
        计算两个数的乘积
        :param a: 第一个数
        :param b: 第二个数
        :return: 乘积
        """
        return a * b
    
    @command_handler(
        name="除法计算",
        description="计算两个数的商",
        output_provider="division_output"
    )
    def divide(self, a: int, b: int) -> float:
        """
        计算两个数的商
        :param a: 第一个数
        :param b: 第二个数
        :return: 商
        """
        if b == 0:
            # 抛出异常，将被转换为Observable.error
            raise ValueError("除数不能为零")
        return a / b
    
    @command_handler(
        name="异步计算",
        description="异步计算两个数的和"
    )
    def async_add(self, a: int, b: int) -> Observable:
        """
        异步计算两个数的和
        :param a: 第一个数
        :param b: 第二个数
        :return: 包含结果的Observable
        """
        return rx.just(a + b)
    
    @command_handler(ignore=True)
    def internal_method(self):
        """
        内部方法，不会被注册为命令
        """
        pass
    
    # 用于division_output的方法
    def division_output(self, a: int, b: int):
        """提供除法命令的输出元数据"""
        pass


def main():
    # 创建命令实例
    math_commands = MathCommands()
    
    # 创建命令支持
    command_support = create_python_bean_command_support(math_commands)
    
    # 打印所有可用命令
    print("可用命令:")
    command_support.get_all_command_metadata().subscribe(
        on_next=lambda metadata: print(f"- {metadata.id}: {metadata.name} - {metadata.description}"),
        on_error=lambda err: print(f"Error: {err}")
    )
    
    # 执行加法命令
    add_command = Command("add", {"a": 10, "b": 20})
    print("\n执行加法命令:")
    command_support.execute(add_command).subscribe(
        on_next=lambda result: print(f"结果: {result}"),
        on_error=lambda err: print(f"Error: {err}")
    )
    
    # 执行减法命令
    subtract_command = Command("subtract", {"a": 30, "b": 15})
    print("\n执行减法命令:")
    command_support.execute(subtract_command).subscribe(
        on_next=lambda result: print(f"结果: {result}"),
        on_error=lambda err: print(f"Error: {err}")
    )
    
    # 执行除法命令 - 正常情况
    divide_command = Command("divide", {"a": 20, "b": 5})
    print("\n执行除法命令 (正常):")
    command_support.execute(divide_command).subscribe(
        on_next=lambda result: print(f"结果: {result}"),
        on_error=lambda err: print(f"Error: {err}")
    )
    
    # 执行除法命令 - 异常情况
    divide_by_zero_command = Command("divide", {"a": 10, "b": 0})
    print("\n执行除法命令 (除零):")
    command_support.execute(divide_by_zero_command).subscribe(
        on_next=lambda result: print(f"结果: {result}"),
        on_error=lambda err: print(f"Error: {err}")
    )
    
    # 执行不存在的命令
    unknown_command = Command("unknown", {})
    print("\n执行不存在的命令:")
    command_support.execute(unknown_command).subscribe(
        on_next=lambda result: print(f"结果: {result}"),
        on_error=lambda err: print(f"Error: {err}")
    )


if __name__ == "__main__":
    main() 