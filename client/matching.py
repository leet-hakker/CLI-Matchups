import random
import datetime
import math
from haversine import haversine


matches = [{"name": i, "compatibility": 0, "likes": 0, "interests": random.randrange(6), "dislikes": 0, "latitude": random.uniform(47.2921, 49.2921), "longitude": random.uniform(14.6335, 16.6335)} for i in range(100)]

def calculate_distance(A, B):
    return haversine((A["latitude"], A["longitude"]), (B["latitude"], B["longitude"]))

def calculate_compatibility(A, B):
    distance = calculate_distance(A, B)/1000
    dist_factor = 1 - math.pow(distance, 2)

    return (((1+B["likes"]-B["dislikes"])*B["interests"])*dist_factor)


def partition(arr,l,h): 
    i = ( l - 1 ) 
    x = arr[h]["compatibility"] 
  
    for j in range(l , h): 
        if   arr[j]["compatibility"] <= x: 
  
            # increment index of smaller element 
            i = i+1
            arr[i]["compatibility"],arr[j]["compatibility"] = arr[j]["compatibility"],arr[i]["compatibility"] 
  
    arr[i+1]["compatibility"],arr[h]["compatibility"] = arr[h]["compatibility"],arr[i+1]["compatibility"] 
    return (i+1) 
  
# Function to do Quick sort 
# arr[] --> Array to be sorted, 
# l  --> Starting index, 
# h  --> Ending index 
def quick_sort(arr,l,h): 
  
    # Create an auxiliary stack 
    size = h - l + 1
    stack = [0] * (size) 
  
    # initialize top of stack 
    top = -1
  
    # push initial values of l and h to stack 
    top = top + 1
    stack[top] = l 
    top = top + 1
    stack[top] = h 
  
    # Keep popping from stack while is not empty 
    while top >= 0: 
  
        # Pop h and l 
        h = stack[top] 
        top = top - 1
        l = stack[top] 
        top = top - 1
  
        # Set pivot element at its correct position in 
        # sorted array 
        p = partition( arr, l, h ) 
  
        # If there are elements on left side of pivot, 
        # then push left side to stack 
        if p-1 > l: 
            top = top + 1
            stack[top] = l 
            top = top + 1
            stack[top] = p - 1
  
        # If there are elements on right side of pivot, 
        # then push right side to stack 
        if p+1 < h: 
            top = top + 1
            stack[top] = p + 1
            top = top + 1
            stack[top] = h 
    
    return arr

A = {"latitude": 48.2921, "longitude": 15.6335}

start = datetime.datetime.now()

for match in matches:
    match["distance"] = calculate_distance(A, match)
    match["compatibility"] = calculate_compatibility(A, match)


matches = quick_sort(matches, 0, len(matches)-1)
print(matches[0])
print(matches[-1])
print(datetime.datetime.now()-start)
