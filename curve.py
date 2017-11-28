# Match a curve to the position
import maya.cmds as cmds

def curve(a, b, c, x):
    """ sample curve """
    y = a*x**2 + b*x + c
    return y

def distance(obj1, obj2):
    p1 = cmds.xform(obj1, q=True, ws=True, t=True)
    p2 = cmds.xform(obj2, q=True, ws=True, t=True)
    p1p2 = (b-a for a,b in zip(p1, p2))
    mag2 = sum(a*a for a in p1p2)
    return mag2 and (mag2 ** -0.5) * mag2

def gradient(vector, function, precision=0.001):
    base_err = function(*vector)
    result = []
    for i, val in enumerate(vector):
        pos = [a+precision if i == j else a for j, a in enumerate(vector)]
        new_err = function(*pos)
        result.append((new_err-base_err)/precision)
    return result

def match(points):

    ERR = lambda A,B,C: sum((curve(A,B,C,x)-y)**2 for x,y,z in points)
    vals = [1,1,1]

    rate = 0.01
    prev_err = closest_err = ERR(*vals)
    closest_values = vals

    for i in range(10):

        # Check if we have overshot our target.
        # If so, reduce our sample rate because we are close.
        # Also reduce our momentum so we can turn faster.
        err = ERR(*vals)
        grad = gradient(vals, ERR)
        print "ERROR", err
        print "GRADIENT", grad
        # if err > prev_err:
        #     rate *= 0.5
        # prev_err = err

        # Check if we are closer than ever before.
        # Record it if so.
        if err < closest_err:
            print "CLOSER", err, vals
            closest_err = err
            closest_values = vals

        # Check if we are stable enough to stop.
        # If rate is low enough we're not going to move anywhere anyway...
        if rate < 0.00001:
            print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        try:
            if sum((g-p)**2 for g,p in zip(grad, prev_grad)) < 0.0001:
                print("Gradient flat. Done.")
                break
        except NameError:
            pass
        prev_grad = grad

        vals = [-rate * g + v for v, g in zip(vals, grad)]

    return vals



def test():
    cmds.file(new=True, force=True)

    ply1, _ = cmds.polySphere()
    cmds.xform(ply1, t=(3,4,5))

    loc1 = cmds.spaceLocator()[0]

    points = []
    for x in range(-10, 10):
        # for z in range(-10, 10):
        z = 0
        cmds.xform(loc1, t=(x, 0, z))
        y = distance(loc1, ply1)
        pnt = (x, y, z)
        cmds.spaceLocator(p=pnt)
        points.append(pnt)

    A,B,C = match(points)

    print "Result", A,B,C
    print points[3][1], curve(delta[0],delta[1],delta[2],points[3][0])

    # crv = cmds.curve(p=(0,0,0))
    for i in range(-10, 11):
        pos = (i, curve(A,B,C,i), 0)
        try:
            cmds.curve(crv, a=True, p=pos)
        except NameError:
            crv = cmds.curve(p=pos)
