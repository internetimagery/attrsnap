# Match a curve to the position
import maya.cmds as cmds
import math

# sharpness 1 < s < 2
#
# class Dyn3(object):
#     def __call__(s, x, translateX, translateY, scale, sharpness=1):
#         # sharpness = min(max(sharpness, 1), 2)
#         return scale * abs(translateX + x) ** sharpness + translateY
#     def __len__(s):
#         return 3

class Basic(object):
    def __call__(s, x, translateX, translateY, scale):
        return (translateX + abs(x))*scale+translateY
    def __len__(s):
        return 3

class Dyn(object):
    def __call__(s, x, translateX, translateY, scale, sharpness=1):
        sharpness = min(max(sharpness, 1), 2)
        return scale * abs(translateX + x) ** sharpness + translateY
    def __len__(s):
        return 4

class Dyn2(object):
    def __init__(s, X):
        s.translateX = X
    def __call__(s, x, translateX, translateY, scale, sharpness=1):
        sharpness = min(max(sharpness, 1), 2)
        translateX = s.translateX
        return scale * abs(translateX + x) ** sharpness + translateY
    def __len__(s):
        return 4


class Dyn1(object):
    def __call__(s, x, translateX, translateY, scale, sharpness):
        sharpness = 1
        return scale * abs(translateX + x) ** sharpness + translateY
    def __len__(s):
        return 4

class Bell(object):
    def __call__(s, x, a, b, c):
        return a ** -(x-b)**2/(2*c**2)
    def __len__(s):
        return 3

class Sin(object):
    def __call__(s, x, a, b, c):
        return a * math.sin(b * x) + c
    def __len__(s):
        return 3

class Abs(object):
    def __call__(s, x, a, b, c):
        return a * abs(x - b) + c
    def __len__(s):
        return 3

class Poly2(object):
    def __call__(s, x, a, b, c):
        a *= 0.2
        b *= 0.2
        return a*x**2 + b*x + c
    def __len__(s):
        return 3

class Poly3(object):
    def __call__(s, x, a, b, c, d):
        return a*x**3 + b*x**2 + c*x + d
    def __len__(s):
        return 4


def distance(obj1, obj2):
    p1 = cmds.xform(obj1, q=True, ws=True, t=True)
    p2 = cmds.xform(obj2, q=True, ws=True, t=True)
    p1p2 = (b-a for a,b in zip(p1, p2))
    mag2 = sum(a*a for a in p1p2)
    return mag2 and (mag2 ** -0.5) * mag2

def length(vec):
    mag2 = sum(a*a for a in vec)
    return (mag2 ** -0.5) * mag2

def gradient(vector, points, curve, precision=0.001):
    base_err = least_squares(vector, points, curve)
    result = []
    for i, val in enumerate(vector):
        pos = [a+precision if i == j else a for j, a in enumerate(vector)]
        new_err = least_squares(pos, points, curve)
        result.append((new_err-base_err)/precision)
    return result

def least_squares(vals, points, curve):
    dist = sum((curve(x, *vals)-y)**2 for x,y,z in points)
    return dist# and math.log(dist,10)
    # return sum((curve(x, *vals)-y)**2 for x,y,z in points)


def fit(points, curve, vals=None, rate=0.00000001, friction=0.8):

    vals = [1]*len(curve) if vals is None else vals

    prev_err = closest_err = least_squares(vals, points, curve)
    closest_values = vals
    velocity = [0]*len(vals)

    for i in range(100000):

        # Check if we have overshot our target.
        # If so, reduce our sample rate because we are close.
        # Also reduce our momentum so we can turn faster.
        err = least_squares(vals, points, curve)
        grad = gradient(vals, points, curve)
        # if not i:
        #     print "GRADLEN", length(grad)
        if err > prev_err:
            rate *= 0.5
            velocity = [a*0.5 for a in velocity]
        prev_err = err

        # Check if we are closer than ever before.
        # Record it if so.
        if err < closest_err:
            closest_err = err
            closest_values = vals

        # Check if we are stable enough to stop.
        # If rate is low enough we're not going to move anywhere anyway...
        # if rate < 0.00001:
        #     print("Rate below tolerance. Done.")
        #     break

        # Check if we are sitting on a flat plateau.
        try:
            if sum((g-p)**2 for g,p in zip(grad, prev_grad)) < 0.0001:
                print("Gradient flat. Done. After %s tries" % i)
                break
        except NameError:
            pass
        prev_grad = grad

        # Update our momentum
        prev_velocity = velocity
        velocity = [v*friction - g * rate for v,g in zip(velocity, grad)]
        vals = [p * -friction + v * (1+friction) + vv for p, v, vv in zip(prev_velocity, velocity, vals)]
        # curr_values += prev_velocity * -friction + velocity * (1+friction)
        #
        #
        # vals = [-rate * g + v for v, g in zip(vals, grad)]

    print "closest", closest_err
    return closest_values



def test():
    cmds.file(new=True, force=True)

    ply1, _ = cmds.polySphere()
    cmds.xform(ply1, t=(3,4,5))

    loc1 = cmds.spaceLocator()[0]

    points = []
    for x in range(-10, 10, 1):
        # for z in range(-10, 10):
        z = 0
        cmds.xform(loc1, t=(x, 0, z))
        y = distance(loc1, ply1)
        pnt = (x, y, z)
        cmds.spaceLocator(p=pnt)
        points.append(pnt)

    # curve = Dyn3()
    curve = Basic()
    vals = fit(points, curve)
    # curve2 = Dyn2(vals[0])
    # vals = fit(points, curve2, vals)
    # curve = Dyn()
    # vals = [-2.7, 6.3, 0.08, 1.8]

    print "Result", vals

    # crv = cmds.curve(p=(0,0,0))
    for i in range(-10, 11):
        pos = (i, curve(i, *vals), 0)
        try:
            cmds.curve(crv, a=True, p=pos)
        except NameError:
            crv = cmds.curve(p=pos)
