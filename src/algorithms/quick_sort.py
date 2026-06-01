"""快速排序算法实现（原地分区 + 随机枢轴优化）。"""

import random
from typing import TypeVar, MutableSequence

T = TypeVar("T")


def quick_sort(arr: MutableSequence[T]) -> MutableSequence[T]:
    """对可变序列进行原地快速排序，并返回原序列引用。

    时间复杂度: 平均 O(n log n)，最坏 O(n^2)（已通过随机枢轴缓解）
    空间复杂度: O(log n)（递归调用栈深度）
    
    Args:
        arr: 支持索引与原地修改的序列（如 list），元素需实现 __lt__ 比较。

    Returns:
        排序后的原序列引用。

    Raises:
        TypeError: 输入非可变序列类型。
    """
    if not isinstance(arr, MutableSequence):
        raise TypeError("输入必须是可变序列类型（如 list）")

    def _partition(items: MutableSequence[T], low: int, high: int) -> int:
        pivot_idx = random.randint(low, high)
        items[pivot_idx], items[high] = items[high], items[pivot_idx]
        pivot = items[high]
        i = low - 1
        for j in range(low, high):
            if items[j] <= pivot:
                i += 1
                items[i], items[j] = items[j], items[i]
        items[i + 1], items[high] = items[high], items[i + 1]
        return i + 1

    def _quick_sort_recursive(items: MutableSequence[T], low: int, high: int) -> None:
        if low < high:
            pivot_index = _partition(items, low, high)
            _quick_sort_recursive(items, low, pivot_index - 1)
            _quick_sort_recursive(items, pivot_index + 1, high)

    if arr:
        _quick_sort_recursive(arr, 0, len(arr) - 1)
    return arr