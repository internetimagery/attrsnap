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

    rate = 0.8
    friction = 0.8
    velocity = [0]*len(vals)
    prev_err = closest_err = ERR(*vals)
    closest_values = vals

    for i in range(1):

        # Check if we have overshot our target.
        # If so, reduce our sample rate because we are close.
        # Also reduce our momentum so we can turn faster.
        err = ERR(*vals)
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
        if rate < 0.00001:
            print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        grad = gradient(vals, ERR)
        try:
            if sum((g-p)**2 for g,p in zip(grad, prev_grad)) < 0.0001:
                print("Gradient flat. Done.")
                break
        except NameError:
            pass
        prev_grad = grad

        # Update our momentum
        prev_velocity = velocity
        velocity = [v * friction - g * rate for v, g in zip(velocity, grad)]
        vals = [p * -friction + v * (1+friction) for p, v in zip(prev_velocity, velocity)]




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

    delta = match(points)




    # # crv = cmds.curve(p=(0,0,0))
    # for i in range(-10, 11):
    #     a,b,c = 3,5,0.8
    #     pos = (i, curve(a,b,c,i), 0)
    #     try:
    #         cmds.curve(crv, a=True, p=pos)
    #     except NameError:
    #         crv = cmds.curve(p=pos)
