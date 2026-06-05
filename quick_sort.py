from typing import List, TypeVar

T = TypeVar('T')

def quick_sort(arr: List[T]) -> List[T]:
    """
    原地快速排序算法实现
    :param arr: 待排序的列表（支持任意可比较类型）
    :return: 排序后的列表（原地修改并返回原引用）
    """
    def partition(low: int, high: int) -> int:
        """
        分区函数：选择基准值，将小于等于基准的元素移到左侧，大于的移到右侧
        :param low: 子数组起始索引
        :param high: 子数组结束索引
        :return: 基准值最终所在的索引位置
        """
        pivot = arr[high]  # 选择最后一个元素作为基准（可根据场景优化为随机或三数取中）
        i = low - 1        # i 指向小于等于基准的区域的最后一个元素
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                
        # 将基准值交换到正确的位置
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def _quick_sort_recursive(low: int, high: int) -> None:
        """
        递归排序逻辑
        :param low: 当前子数组起始索引
        :param high: 当前子数组结束索引
        """
        # 边界条件：当子数组长度为 0 或 1 时，无需排序，直接返回
        if low < high:
            pi = partition(low, high)
            # 递归处理基准值左侧和右侧的子数组
            _quick_sort_recursive(low, pi - 1)
            _quick_sort_recursive(pi + 1, high)

    # 处理空列表或 None 的边界情况
    if not arr:
        return arr

    # 启动递归排序，初始范围为整个数组
    _quick_sort_recursive(0, len(arr) - 1)
    return arr