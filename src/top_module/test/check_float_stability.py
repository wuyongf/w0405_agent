import time

def check_float_stability(value):
    threshold = 0.05  # ±5%
    max_time = 2  # 2 seconds
    start_time = time.time()
    prev_value = value
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Check if elapsed time is greater than the specified duration
        if elapsed_time >= max_time:
            return True
        
        # Check if the value has changed more than ±5%
        if abs(value - prev_value) > threshold * prev_value:
            return False
        
        prev_value = value
        time.sleep(0.1)  # Wait for 0.1 seconds before checking again

# Example usage
input_float = float(input("Enter a float value: "))
result = check_float_stability(input_float)

if result:
    print("The float has not changed more than ±5% for more than 2 seconds.")
else:
    print("The float has changed more than ±5% within 2 seconds.")