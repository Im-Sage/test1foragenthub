"""归并排序核心模块。

提供基于分治策略的归并排序实现，支持泛型类型、完整的类型注解及边界情况处理。
适用于后端服务中对列表/序列进行稳定、高效排序的场景。
"""

from typing import TypeVar, List, Sequence, Optional

T = TypeVar("T")


def merge_sort(data: Optional[Sequence[T]]) -> List[T]:
    """对输入序列执行归并排序。

    采用分治策略，递归地将序列拆分为子序列，直到子序列长度为 0 或 1，
    随后通过双指针技术将已排序的子序列合并为完整有序序列。

    Args:
        data: 待排序的序列。支持任意实现了 `__len__` 和 `__getitem__` 的类型。
              若传入 `None`，将安全返回空列表。

    Returns:
        排序后的新列表。原序列不会被修改（纯函数设计）。

    Raises:
        TypeError: 当输入序列中的元素不支持相互比较时抛出。

    Examples:
        >>> merge_sort([3, 1, 4, 1, 5, 9, 2, 6])
        [1, 1, 2, 3, 4, 5, 6, 9]
        >>> merge_sort(None)
        []
        >>> merge_sort([])
        []
        >>> merge_sort([42])
        [42]
    """
    # 妥善处理 None 输入
    if data is None:
        return []

    # 转换为列表以保证切片操作的安全性，并避免修改原数据
    arr = list(data)
    
    # 递归基线条件：空列表或单元素列表已天然有序
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_sorted = merge_sort(arr[:mid])
    right_sorted = merge_sort(arr[mid:])

    return _merge(left_sorted, right_sorted)


def _merge(left: List[T], right: List[T]) -> List[T]:
    """合并两个已排序的列表。

    使用双指针技术遍历左右两个列表，按升序将元素追加到结果列表中。
    当其中一个列表遍历完毕时，将另一个列表的剩余元素直接追加。

    Args:
        left: 左侧已排序列表。
        right: 右侧已排序列表。

    Returns:
        合并后的已排序列表。
    """
    merged: List[T] = []
    i = j = 0
    len_left, len_right = len(left), len(right)

    # 双指针合并核心逻辑
    while i < len_left and j < len_right:
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # 追加剩余未遍历完的片段（时间复杂度 O(1) 的切片追加）
    if i < len_left:
        merged.extend(left[i:])
    if j < len_right:
        merged.extend(right[j:])

    return merged


__all__ = ["merge_sort"]