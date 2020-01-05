def copy_list(list1, list2, every_diff):
    if not list2:
        return False
    if not list1:
        return False

    list_tmp = []
    for p in list2:
        if isinstance(list1[0],list):
            if not [x[0] for x in list1 if abs(float(x[0]) - p) < every_diff]:
                if p > 0.0:
                    list_tmp.append(p)
        if isinstance(list1[0],float):
            if not [x for x in list1 if abs(float(x) - p) < every_diff]:
                if p > 0.0:
                    list_tmp.append(p)
    return list_tmp


list_a = [1.001,1.005,1.007,1.009]
list_b = [1.003,1.014]
print(copy_list(list_a,list_b,0.001))