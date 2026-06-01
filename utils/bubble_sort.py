from typing import List, Any


def bubble_sort(arr: List[Any]) -> List[Any]:
    """
    使用冒泡排序算法对列表进行升序排序。

    该实现包含双重循环比较、相邻元素交换机制，
    以及基于无交换标志的提前终止优化。适用于数据量较小或基本有序的序列。

    Args:
        arr (list): 待排序的列表，元素需为可比较类型（如 int, float, str）。

    Returns:
        list: 排序后的列表（原地修改并返回原引用）。

    Raises:
        TypeError: 当输入不是列表，或列表中包含不可比较的元素时抛出。
        
    Examples:
        >>> bubble_sort([5, 3, 8, 4, 2])
        [2, 3, 4, 5, 8]
        >>> bubble_sort([])
        []
    """
    if not isinstance(arr, list):
        raise TypeError(f"期望输入类型为 list，实际得到 {type(arr).__name__}")

    n = len(arr)
    if n <= 1:
        return arr

    # 外层循环控制需要比较的轮数
    for i in range(n - 1):
        swapped = False  # 提前终止优化标志
        # 内层循环执行相邻元素的两两比较
        for j in range(n - i - 1):
            try:
                # 若前一个元素大于后一个元素，则交换位置
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            except TypeError as e:
                raise TypeError(f"列表元素类型不一致或不可比较: {e}")

        # 若某一轮遍历中未发生任何交换，说明列表已有序，提前结束排序
        if not swapped:
            break

    return arr