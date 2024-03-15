from gates import G_compare
a = 37
b = 37

# convert a num into a list (binary), little endian

def num2list(n):
    l = []
    for i in range(2):
        l.append(n%2)
        n = n//2
    return l


for i in range(0, 4):
    for j in range(0, 4):
        i_list = num2list(i)
        j_list = num2list(j)
        print(i, j, G_compare(i_list, j_list))
