def find_constant_region(lst):
    start_index = None
    end_index = None
    
    for i in range(len(lst)):
        if lst[i] == 700:
            if start_index is None:
                start_index = i
            end_index = i
    
    return start_index, end_index

# Example usage
lst = [500, 600, 700, 700, 700, 700, 700, 700, 800, 900]
start, end = find_constant_region(lst)
print("Start index:", start)
print("End index:", end)