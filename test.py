def myround():
    x = 157
    base = 50
    nearest_x =  base * round(x/base)
    return nearest_x / base
print(myround())
