def bubble_sort(arr):
    """冒泡排序：时间复杂度 O(n²)，优化后最佳情况 O(n)"""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print(f"排序前: {data}")
    print(f"排序后: {bubble_sort(data)}")