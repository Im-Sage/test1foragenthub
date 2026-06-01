from typing import List

class SortService:
    """
    提供基础排序服务逻辑。此处以归并排序为例，
    保证 O(n log n) 时间复杂度，适合后端数据预处理场景。
    """
    @classmethod
    def sort_array(cls, arr: List[int]) -> List[int]:
        if not arr or len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = cls.sort_array(arr[:mid])
        right = cls.sort_array(arr[mid:])
        return cls._merge(left, right)

    @classmethod
    def _merge(cls, left: List[int], right: List[int]) -> List[int]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result