"""排序算法参考实现（供测试脚本调用）"""
from typing import List, Tuple, Any

def merge_sort(arr: List[Any]) -> List[Any]:
    """稳定排序：归并排序"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(left: List[Any], right: List[Any]) -> List[Any]:
    res, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= 保证稳定性
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:]); res.extend(right[j:])
    return res

def quick_sort(arr: List[Any]) -> List[Any]:
    """不稳定排序：快速排序（随机枢轴优化）"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)

def tim_sort(arr: List[Any]) -> List[Any]:
    """Python 内置 Timsort（稳定）"""
    return sorted(arr)