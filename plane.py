# testing plane stuff

def vAdd(v1, v2):
    return tuple(v1[i] + v2[i] for i in range(len(v1)))

def vSub(v1, v2):
    return tuple(v1[i] - v2[i] for i in range(len(v1)))

def vMul(v1, v2):
    return tuple(v1[i] * v2[i] for i in range(len(v1)))

def cross(v1, v2):
    return (
        v1[1] * v2[2] - v2[1] * v1[2],
        v1[2] * v2[0] - v2[2] * v1[0],
        v1[0] * v2[1] - v2[0] * v1[1])

def plane(p1, p2, p3):
    p1p2 = vSub(p2, p1)
    p1p3 = vSub(p3, p1)
    crs = cross(p1p2, p1p3)
    d = vMul(crs, p1)
    return (crs[0], crs[1], crs[2], -sum(vMul(crs, p1)))

print plane((1,2,-2), (3,-2,1), (5,1,-4))
