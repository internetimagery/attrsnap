# Match objects together using provided attributes
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is a labor of love, and therefore is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

from __future__ import print_function, division
import collections
import itertools
import element
import utility
import groups
import random
import time

try:
    xrange
    from itertools import izip
except NameError:
    xrange = range
    izip = zip

# Reference:
# https://cs231n.github.io/neural-networks-3/#gradcheck

def form_heirarchy(grps):
    """ Sort groups into an efficient heirarchy """
    cache_dist = {g: g.get_distance() for g in grps} # Keep track of distance values
    sorted_grp = list(grps) # Our list of groups in sorted order
    child_grp = collections.defaultdict(list) # Groups with relation to their children
    precision_move = 0.0001
    precision_check = 0.000000001

    # Check all groups
    for grp1 in grps:
        grp1.shift(precision_move) # Move values slightly
        for grp2 in grps: # Check what happened because of this
            dist = grp2.get_distance()
            diff = abs(dist - cache_dist[grp2])
            if diff > precision_check:
                if grp2 is not grp1: # Don't add self as child of self
                    child_grp[grp1].append(grp2)
            cache_dist[grp2] = dist
        if child_grp[grp1]: # We have some children to sort through
            for i, child in enumerate(sorted_grp):
                if child is grp1:
                    break
                if child in child_grp[grp1]: # Find earliest child and swap positions
                    sorted_grp.remove(grp1)
                    sorted_grp.insert(i, grp1)
                    break
    # Collect any cycles that have been dug up.
    cycles = collections.defaultdict(list)
    for parent in child_grp:
        for child in child_grp[parent]:
            if parent in child_grp[child]:
                cycles[parent].append(child)

    # If we have any cycles. Warn about them.
    if cycles:
        utility.warn("The following groups have cycle issues, and may not evaluate correctly:\n{}".format(", ".join(c.get_name() for c in cycles)))

    # Throw in duplicates for cyclic groups to ensure they get evaluated in differing orders
    new_sorted_grp = []
    for i, grp in enumerate(sorted_grp):
        new_sorted_grp.append(grp)
        if i:
            # Check if the two cyclic groups are side by side
            # TODO: Add functionality for more than two cyclic pairs (ie triplets etc)
            prev_grp = sorted_grp[i-1]
            if grp in cycles and prev_grp in cycles[grp]:
                new_sorted_grp.append(prev_grp)
    return new_sorted_grp

def optim_random(group, step=0.01, limit=10, threshold=1e-8):
    """ Optimize using random samples. """
    best = group.get_snapshot()
    num_attrs = len(group)
    step_limit = num_attrs * limit
    yield best
    while True:
        prev_best = best
        # Look around at possible steps. Found a better one? Move over there and increase our confidence.
        for _ in xrange(step_limit):
            candidate = [a + step * random.uniform(-1.0, 1.0) for a in best.vals]
            group.set_values(candidate)
            candidate_snapshot = group.get_snapshot()
            if candidate_snapshot.dist < best.dist:
                best = candidate_snapshot
                step *= 2
                yield best
                break
        else:
            step *= 0.1
        if step < threshold:
            break
    yield best


# https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method
def optim_nelder_mead(group, step=0.001, limit=500):
    """ Search using Nelder Mead Optimization """

    # Initial values
    simplex = [group.get_snapshot()]
    no_improv, num_attrs, prev_best = 0, len(group), simplex[0].cost

    # Start walking!
    yield simplex[0]
    # for _ in xrange(2): # restart once to ensure we're good.
    for _ in xrange(1): # restart once to ensure we're good.
        # Build our shape
        simplex = simplex[:1]
        for i in xrange(num_attrs):
            vals = list(simplex[0].vals[:])
            vals[i] += step
            group.set_values(vals)
            simplex.append(group.get_snapshot())
        for _ in xrange(limit):
            # Sort recorded values. Keep track of best.
            simplex.sort(key=lambda x: x.cost)
            best = simplex[0].cost

            # Update if we're better off.
            if best < prev_best:
                prev_best = best
                yield simplex[0]

            # Check if we're not getting any closer.
            # 1e-10 low quality, faster
            # 1e-15 higher quality, slower
            # TODO: Revisit this with linear distance
            if simplex[-1].cost - simplex[0].cost < 1e-10:
            # if simplex[-1].dist - simplex[0].dist < 1e-15:
                break

            # Pivot of the search area.
            center = [sum(b) / num_attrs for b in izip(*(a.vals for a in simplex[:-1]))]

            # Reflection
            val_refl = [a + (a - b) for a, b in izip(center, simplex[-1].vals)]
            group.set_values(val_refl)
            refl = group.get_snapshot()
            if simplex[0].cost <= refl.cost < simplex[-2].cost:
                del simplex[-1]
                simplex.append(refl)
                continue

            # Expansion
            if refl.cost < simplex[0].cost:
                val_exp = [a + 2 * (a - b) for a, b in izip(center, simplex[-1].vals)]
                group.set_values(val_exp)
                exp = group.get_snapshot()
                del simplex[-1]
                simplex.append(exp if exp.cost < refl.cost else refl)
                continue

            # Contraction
            val_cont = [a + -0.5 * (a - b) for a, b in izip(center, simplex[-1].vals)]
            group.set_values(val_cont)
            cont = group.get_snapshot()
            if cont.cost < simplex[-1].cost:
                del simplex[-1]
                simplex.append(cont)
                continue

            # Reduction
            best = simplex[0].vals
            new_simplex = []
            for vals in simplex:
                vals_redux = [b + 0.5 * (a - b) for a, b in izip(vals.vals, best)]
                group.set_values(vals_redux)
                new_simplex.append(group.get_snapshot())
            simplex = new_simplex

    # Done!
    yield simplex[0]



def optim_adam(group, rate=0.8, resistance=0.8, friction=0.9, tolerance=1e-6, limit=500, debug=False):
    """
    Match using gradient descent + momentum.
    rate = sample size of each step.
    friction = how much dampening do we get.
    limit = how many steps do we take before giving up?
    """
    # Validate some parameters
    limit = abs(int(limit))
    if resistance >= 1 or friction >= 1 or rate <= 0:
        raise RuntimeError("Variables are out of range.")


    # Initialize variables
    velocity = momentum = [0]*len(group)
    prev = closest = group.get_snapshot()
    curr_values = closest.vals

    yield closest

    # GO!
    for i in xrange(limit):
        group.set_values(curr_values)
        current = group.get_snapshot()

        # Check if we have overshot our target.
        # If so, reduce our sample rate and our momentum, so we can turn faster.
        if current.cost > prev.cost:
            rate *= 0.5
            resistance *= 0.5
            friction *= 0.5
            velocity = [a*0.5 for a in velocity]
            momentum = [a*0.5 for a in momentum]
        prev = current

        # Check if we are closer than ever before.
        # Record it if so.
        if current.cost < closest.cost:
            closest = current
            yield closest

        # Check if we are stable enough to stop.
        # If rate is low enough we're not going to move anywhere anyway...
        if rate < tolerance:
            if debug:
                print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        gradient = group.get_gradient(rate*0.01)
        if i:
            mag = sum(c*c for c in (a - b for a, b in izip(gradient, prev_gradient)))
            length = mag and (mag ** -0.5) * mag
            if length < 1e-8:
                if debug: print("Gradient flat. Done.")
                break
        prev_gradient = gradient

        # Calculate our path
        momentum = [a*resistance + b*(1-resistance) for a, b in izip(momentum, gradient)]
        velocity = [a*friction + b*b*(1-friction) for a, b in izip(velocity, gradient)]
        curr_values = [a + b*-rate / (1e-20 if c <=0 else ((c ** -0.5)*c)) for a, b, c in izip(curr_values, momentum, velocity)]
        momentum = group.bounds(momentum)

    if debug:
        print("Finished after {} steps".format(i))
    yield closest

def linear_jump(grp):
    """ Attempt a straight jump towards the goal. Assuming a linear 1:1 attribute:distance ratio.
        If we are closer, begin otimization from this point. Else return to where we were.
    """
    old_snapshot = grp.get_snapshot()
    gradient = grp.get_gradient()
    new_values = [old_snapshot.dist * a * -1 + b for a, b in izip(gradient, old_snapshot.vals)]
    grp.set_values(new_values)
    new_snapshot = grp.get_snapshot()
    if new_snapshot.dist < old_snapshot.dist: return True
    else: grp.set_values(old_snapshot.vals)
    return False

def match(templates, start_frame=None, end_frame=None, sub_frame=1.0, matcher=optim_adam, prepos=True, match_tolerance=1e-10, **kwargs):
    """
    Match groups across frames.
    update. function run updating matching progress.
    start_frame (optional). Current frame if not given.
    end_frame (optional). Single frame if not provided else the full range.
    sub_frame (optional). Steps to take. 1.0 default.
    matcher (optional). Optimizer to use. adam default.
    prepos (optional). Pre position with small one off attempts to snap the marker before resorting to optimizer. True default.
    """
    start_time = time.time()
    start_frame = float(utility.get_frame()) if start_frame is None else float(start_frame)
    end_frame = start_frame if end_frame is None else float(end_frame)
    grps = form_heirarchy([groups.Group(t) for t in templates if t.enabled])
    if not grps: raise RuntimeError("No templates provided.")

    print("Matching Groups Now! Using \"%s\"." % matcher.__name__)
    print("Match order: {}".format(", ".join(a.get_name() for a in grps)))
    group_step = 1 / len(grps)

    # Continue prepositioning while successful.
    cont_hacky = {a: False for a in grps}
    cont_linear = {a: False for a in grps}

    yield 0.0 # Kick us off
    frames = int((end_frame - start_frame) / sub_frame) + 1
    for i in range(frames):
        frame = i * sub_frame + start_frame
        utility.set_frame(frame)
        for j, grp in enumerate(grps):
            # grp.clear_cache()
            if prepos:
                if not i or cont_hacky[grp]:
                    cont_hacky[grp] = success = utility.hacky_snap(grp)
                    if not i and success: print("Direct Snapped %s." % grp.name) # Hack for translates and rotates
                if not i or cont_linear[grp]:
                    cont_linear[grp] = success = linear_jump(grp)
                    if not i and success: print("Linear Jumpped %s." % grp.name) # Make a quick attempt at linearly shortcutting our way there.
            total_dist = grp.get_distance()
            total_scale = total_dist and 1.0 / total_dist
            for snapshot in matcher(grp, **kwargs):
                if snapshot.dist < match_tolerance: break
                progress = 1 - snapshot.dist * total_scale
                yield progress * group_step + j * group_step
            grp.keyframe(snapshot.vals)
    calls = sum(a.get_calls() for a in grps)
    print("Match complete. Took,", time.time() - start_time)
    print("Used %s calls. %s calls per frame." % (calls, frames and calls / frames))
    yield 1.0
