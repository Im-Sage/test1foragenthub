"""归并排序实现（工业级优化版）"""

from typing import TypeVar, List, Union

T = TypeVar('T')

# 性能阈值：小于此长度切换插入排序，减少递归与函数调用开销
_INSERTION_SORT_THRESHOLD = 15


def merge_sort(arr: Union[List[T], tuple[T, ...]]) -> List[T]:
    """归并排序入口，支持列表/元组，返回新列表。
    
    Args:
        arr: 待排序的可迭代对象（元素需支持 '<=' 比较）
        
    Returns:
        排序后的新列表
        
    Raises:
        TypeError: 输入类型非法或元素不可比较
    """
    if not isinstance(arr, (list, tuple)):
        raise TypeError("输入必须是列表或元组")
    if not arr:
        return []

    # 深拷贝避免修改原数据，同时预分配辅助数组
    data = list(arr)
    aux = data[:]
    _sort_recursive(data, aux, 0, len(data) - 1)
    return data


def _sort_recursive(arr: List[T], aux: List[T], left: int, right: int) -> None:
    """递归分治排序（内部函数）"""
    if left >= right:
        return

    # 小数组优化：切换插入排序
    if right - left < _INSERTION_SORT_THRESHOLD:
        _insertion_sort(arr, left, right)
        return

    mid = (left + right) // 2
    _sort_recursive(arr, aux, left, mid)
    _sort_recursive(arr, aux, mid + 1, right)

    # 提前终止优化：若左右子数组已有序，无需合并
    if arr[mid] <= arr[mid + 1]:
        return

    _merge(arr, aux, left, mid, right)


def _merge(arr: List[T], aux: List[T], left: int, mid: int, right: int) -> None:
    """合并两个有序子区间 [left, mid] 和 [mid+1, right]"""
    i, j, k = left, mid + 1, left

    # 将当前区间复制到辅助数组
    aux[left:right + 1] = arr[left:right + 1]

    while i <= mid and j <= right:
        if aux[i] <= aux[j]:
            arr[k] = aux[i]
            i += 1
        else:
            arr[k] = aux[j]
            j += 1
        k += 1

    # 仅左半区剩余需回写，右半区已在原位
    if i <= mid:
        arr[k:right + 1] = aux[i:mid + 1]


def _insertion_sort(arr: List[T], left: int, right: int) -> None:
    """区间插入排序（内部优化）"""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key