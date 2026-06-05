def merge_sort(arr):
    """
    Sorts a list using the Merge Sort algorithm.
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # Recursively sort both halves
    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)

    return merge(left_half, right_half)

def merge(left, right):
    """
    Merges two sorted lists into one sorted list.
    """
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append remaining elements
    result.extend(left[i:])
    result.extend(right[j:])

    return result

if __name__ == "__main__":
    # Example usage
    data = [12, 11, 13, 5, 6, 7]
    print("Given array is", data)
    sorted_data = merge_sort(data)
    print("Sorted array is", sorted_data)