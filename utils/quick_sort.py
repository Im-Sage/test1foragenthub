import random
from typing import List, TypeVar

T = TypeVar('T')

def quick_sort(arr: List[T]) -> List[T]:
    """
    快速排序核心逻辑实现（分治策略）。

    采用 Lomuto 分区方案结合随机基准值优化，有效避免重复元素或已排序序列
    导致的时间复杂度退化。原地修改输入列表以节省内存，并返回该列表引用。

    Args:
        arr (List[T]): 待排序的列表，元素需支持比较操作（<, <=, >）。

    Returns:
        List[T]: 排序后的列表（与原对象为同一引用）。

    Complexity:
        Time: 平均 O(n log n)，最坏 O(n^2)（已通过随机基准值大幅降低触发概率）
        Space: O(log n) 递归调用栈开销

    Examples:
        >>> quick_sort([3, 1, 4, 1, 5, 9])
        [1, 1, 3, 4, 5, 9]
        >>> quick_sort([])
        []
        >>> quick_sort([42])
        [42]
    """
    # 边界条件：空列表或单元素列表无需排序，直接返回
    if len(arr) <= 1:
        return arr

    _quick_sort_recursive(arr, 0, len(arr) - 1)
    return arr


def _quick_sort_recursive(arr: List[T], low: int, high: int) -> None:
    """递归执行分治排序逻辑"""
    # 递归终止条件：子数组长度为 0 或 1
    if low < high:
        pivot_idx = _partition(arr, low, high)
        # 分治：基准值左侧与右侧分别递归
        _quick_sort_recursive(arr, low, pivot_idx - 1)
        _quick_sort_recursive(arr, pivot_idx + 1, high)


def _partition(arr: List[T], low: int, high: int) -> int:
    """
    Lomuto 分区方案（带随机基准值优化）。
    将小于等于基准值的元素移至左侧，大于的移至右侧。
    """
    # 随机选取基准值并与末尾交换，打破重复元素/有序序列的最坏情况
    random_idx = random.randint(low, high)
    arr[random_idx], arr[high] = arr[high], arr[random_idx]

    pivot = arr[high]
    i = low - 1  # i 指向最后一个 <= pivot 的元素索引

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    # 将基准值放置到最终正确位置
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1