def quick_sort(arr):
    """快速排序实现（示例）"""
    if arr is None:
        raise TypeError("输入必须为列表类型")
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)