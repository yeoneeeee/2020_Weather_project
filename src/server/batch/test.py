import numpy as np
import csv
# a = np.loadtxt('code.csv',delimiter=',',dtype=np.str)
# temp = [i[2] for i in a]
# print(temp)
# np.savetxt('location_code.csv', temp, fmt='%s,', newline='')

def read_code():
    with open('location_code.csv', 'r') as f:
        rdr = csv.reader(f)
        res = [item for item in rdr]
    return res

r = read_code()
print(r)

