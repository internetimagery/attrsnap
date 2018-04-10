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

Snapshot = collections.namedtuple("Snapshot", ["dist", "vals"]) # Single value construct

class Vector(tuple):
    """ Make vector operations cleaner """
    __slots__ = ()
    def __new__(cls, *pos):
        return tuple.__new__(cls, pos[0] if len(pos) == 1 else pos)
    def mul(lhs, rhs):
        return lhs.__class__(a*b for a,b in izip(lhs, rhs))
    def dot(lhs, rhs, zip=izip):
        return sum(a*b for a,b in zip(lhs, rhs))
    def square(s):
        return s.__class__(a*a for a in s)
    def length(s):
        dot = s.dot(s)
        return dot and (dot ** -0.5) * dot
    def normalize(s):
        mag = s.length()
        return s.__class__(mag and a/mag for a in s)
    def sqrt(s):
        return s.__class__(a if a <=0 else (a ** -0.5)*a for a in s)
    def __add__(lhs, rhs, zip=izip):
        return lhs.__class__(a+b for a,b in zip(lhs, rhs))
    def __radd__(rhs, lhs):
        return rhs.__add__(lhs)
    def __sub__(lhs, rhs, rev=False, zip=izip):
        return lhs.__class__(a-b for a,b in zip(*(rhs, lhs) if rev else (lhs, rhs)))
    def __rsub__(rhs, lhs):
        return rhs.__sub__(rhs, lhs, True)
    def __div__(lhs, rhs, rev=False, zip=izip):
        return lhs.__class__(b and a/b for a,b in zip(*(rhs, lhs) if rev else (lhs, rhs)))
    def __rdiv__(rhs, lhs):
        return rhs.__sub__(rhs, lhs, True)
    def __truediv__(lhs, rhs):
        return lhs.__div__(rhs)
    def __rtruediv__(rhs, lhs):
        return rhs.__div__(lhs, True)
    def __mul__(lhs, rhs, rev=False):
        lhs, rhs = (rhs, lhs) if rev else (lhs, rhs)
        try: # Scalar
            return lhs.__class__(a*rhs for a in lhs)
        except TypeError: # Dot product
            return lhs.dot(rhs)
    def __rmul__(rhs, lhs):
        return rhs.__mul__(lhs, True)

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

def optim_random(group, step=0.01, epoch=10, limit=200, threshold=1e-8):
    """ Optimize using random samples. """
    best = Snapshot(dist=group.get_distance(), vals=group.get_values())
    num_attrs = len(group)
    epoch_count = num_attrs * epoch
    yield best
    for _ in xrange(limit):
        prev_best = best
        for _ in xrange(epoch_count):
            candidate = [a + step * random.uniform(-1.0, 1.0) for a in best.vals]
            group.set_values(candidate)
            dist = group.get_distance()
            if dist < best.dist:
                best = Snapshot(dist=dist, vals=candidate)
                yield best
                break
            if step < threshold:
                break
        if prev_best == best:
            break
    yield best

# def optim_simulated_annealing(group, limit=200):
#
#     # Initialize state
#     temp = 0 # What to set temperature?
#     prev_state = best_state = Snapshot(dist=group.get_distance(), val=group.get_values())
#     trials = accepts = improves = 0
#
#     # Move around!
#     for _ in xrange(limit):

#     def anneal(self):
#         """Minimizes the energy of a system by simulated annealing.
#         Parameters
#         state : an initial arrangement of the system
#         Returns
#         (state, energy): the best state and energy found.
#         """
#         step = 0
#         self.start = time.time()
#
#         # Precompute factor for exponential cooling from Tmax to Tmin
#         if self.Tmin <= 0.0:
#             raise Exception('Exponential cooling requires a minimum "\
#                 "temperature greater than zero.')
#         Tfactor = -math.log(self.Tmax / self.Tmin)
#
#         # Note initial state
#         T = self.Tmax
#         E = self.energy()
#         prevState = self.copy_state(self.state)
#         prevEnergy = E
#         self.best_state = self.copy_state(self.state)
#         self.best_energy = E
#         trials, accepts, improves = 0, 0, 0
#         if self.updates > 0:
#             updateWavelength = self.steps / self.updates
#             self.update(step, T, E, None, None)
#
#         # Attempt moves to new states
#         while step < self.steps and not self.user_exit:
#             step += 1
#             T = self.Tmax * math.exp(Tfactor * step / self.steps)
#             self.move()
#             E = self.energy()
#             dE = E - prevEnergy
#             trials += 1
#             if dE > 0.0 and math.exp(-dE / T) < random.random():
#                 # Restore previous state
#                 self.state = self.copy_state(prevState)
#                 E = prevEnergy
#             else:
#                 # Accept new state and compare to best state
#                 accepts += 1
#                 if dE < 0.0:
#                     improves += 1
#                 prevState = self.copy_state(self.state)
#                 prevEnergy = E
#                 if E < self.best_energy:
#                     self.best_state = self.copy_state(self.state)
#                     self.best_energy = E
#             if self.updates > 1:
#                 if (step // updateWavelength) > ((step - 1) // updateWavelength):
#                     self.update(
#                         step, T, E, accepts / trials, improves / trials)
#                     trials, accepts, improves = 0, 0, 0
#
#
#         # Return best state and energy
# return self.best_state, self.best_energy





    # curr_dist =
    #
    #     // Initialize intial solution
    #     Tour currentSolution = new Tour();
    #     currentSolution.generateIndividual();
    #
    #     System.out.println("Initial solution distance: " + currentSolution.getDistance());
    #
    #     // Set as current best
    #     Tour best = new Tour(currentSolution.getTour());
    #
    #     // Loop until system has cooled
    #     while (temp > 1) {
    #         // Create new neighbour tour
    #         Tour newSolution = new Tour(currentSolution.getTour());
    #
    #         // Get a random positions in the tour
    #         int tourPos1 = (int) (newSolution.tourSize() * Math.random());
    #         int tourPos2 = (int) (newSolution.tourSize() * Math.random());
    #
    #         // Get the cities at selected positions in the tour
    #         City citySwap1 = newSolution.getCity(tourPos1);
    #         City citySwap2 = newSolution.getCity(tourPos2);
    #
    #         // Swap them
    #         newSolution.setCity(tourPos2, citySwap1);
    #         newSolution.setCity(tourPos1, citySwap2);
    #
    #         // Get energy of solutions
    #         int currentEnergy = currentSolution.getDistance();
    #         int neighbourEnergy = newSolution.getDistance();
    #
    #         // Decide if we should accept the neighbour
    #         if (acceptanceProbability(currentEnergy, neighbourEnergy, temp) > Math.random()) {
    #             currentSolution = new Tour(newSolution.getTour());
    #         }
    #
    #         // Keep track of the best solution found
    #         if (currentSolution.getDistance() < best.getDistance()) {
    #             best = new Tour(currentSolution.getTour());
    #         }
    #
    #         // Cool system
    #         temp *= 1-coolingRate;
    #     }
    #

################


# https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method
def optim_nelder_mead(group, step=0.01, limit=200, threshold=10e-8, no_improv_break=10, alpha=1.0, gamma=2.0, rho=-0.5, sigma=0.5):
    """ Search using Nelder Mead Optimization """

    # Initial values
    no_improv, num_attrs, start_vals, prev_best = 0, len(group), group.get_values(), group.get_distance()
    record = [Snapshot(dist=prev_best, vals=start_vals)]
    yield record[0]
    for i in xrange(num_attrs):
        vals = list(start_vals[:])
        vals[i] += step
        group.set_values(vals)
        record.append(Snapshot(dist=group.get_distance(), vals=vals))


    # Start walking!
    for _ in xrange(limit):

        # Sort recorded values. Keep track of best.
        record.sort(key=lambda x: x.dist)
        best = record[0].dist

        # Check if we're better off.
        if best < prev_best - threshold:
            no_improv = 0
            prev_best = best
            yield record[0]
        else:
            no_improv += 1
        # Check if we haven't improved in a while...
        if no_improv >= no_improv_break:
            break

        # Center of the search area!
        center = [0.0] * num_attrs
        for val in record[:-1]: # Ignoring one point
            for i, cen in enumerate(val.vals):
                center[i] += cen / (len(record)-1)

        # Reflection
        val_refl = [a + alpha * (a - b) for a, b in izip(center, record[-1].vals)]
        group.set_values(val_refl)
        dist_refl = group.get_distance()
        if record[0].dist <= dist_refl < record[-2].dist:
            del record[-1]
            record.append(Snapshot(dist=dist_refl, vals=val_refl))
            continue

        # Expansion
        if dist_refl < record[0].dist:
            val_exp = [a + gamma * (a - b) for a, b in izip(center, record[-1].vals)]
            group.set_values(val_exp)
            dist_exp = group.get_distance()
            del record[-1]
            record.append(Snapshot(dist=dist_exp, vals=val_exp) if dist_exp < dist_refl else Snapshot(dist=dist_refl, vals=val_refl))
            continue

        # Contraction
        val_cont = [a + rho * (a - b) for a, b in izip(center, record[-1].vals)]
        group.set_values(val_cont)
        dist_cont = group.get_distance()
        if dist_cont < record[-1].dist:
            del record[-1]
            record.append(Snapshot(dist=dist_cont, vals=val_cont))
            continue

        # Reduction
        best = record[0].vals
        new_record = []
        for vals in record:
            vals_redux = [b + sigma * (a - b) for a, b in izip(vals.vals, best)]
            group.set_values(vals_redux)
            dist_redux = group.get_distance()
            new_record.append(Snapshot(dist=dist_redux, vals=vals_redux))
        record = new_record

    # Done!
    yield record[0]



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
    bias = Vector(group.get_bias())
    velocity = momentum = Vector([0]*len(group))
    prev_dist = closest_dist = group.get_distance()
    curr_values = closest_values = Vector(group.get_values())

    yield Snapshot(dist=closest_dist, vals=closest_values)

    # GO!
    for i in xrange(limit):
        group.set_values(curr_values)

        # Check if we have overshot our target.
        # If so, reduce our sample rate and our momentum, so we can turn faster.
        dist = group.get_distance()
        if dist > prev_dist:
            rate *= 0.5
            resistance *= 0.5
            friction *= 0.5
            velocity *= 0.5
            momentum *= 0.5
        prev_dist = dist

        # Check if we are closer than ever before.
        # Record it if so.
        if dist < closest_dist:
            closest_dist = dist
            closest_values = curr_values
            yield Snapshot(dist=closest_dist, vals=closest_values)

        # Check if we are stable enough to stop.
        # If rate is low enough we're not going to move anywhere anyway...
        if rate < tolerance:
            if debug:
                print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        gradient = Vector(group.get_gradient(rate*0.01))
        if i and (gradient - prev_gradient).length() < 0.0000001:
            if debug:
                print("Gradient flat. Done.")
            break
        prev_gradient = gradient

        # Calculate our path
        momentum = momentum*resistance + gradient.mul(bias)*(1-resistance)
        velocity = velocity*friction + gradient.square()*(1-friction)
        curr_values += momentum*-rate / velocity.sqrt()
        momentum = Vector(group.bounds(momentum))

    if debug:
        print("Finished after {} steps".format(i))
    yield Snapshot(dist=closest_dist, vals=closest_values)

def match(templates, start_frame=None, end_frame=None, sub_frame=1.0, matcher=optim_adam, **kwargs):
    """
    Match groups across frames.
    update. function run updating matching progress.
    start_frame (optional). Current frame if not given.
    end_frame (optional). Single frame if not provided else the full range.
    sub_frame (optional). Steps to take. 1.0 default.
    """
    start_time = time.time()
    start_frame = float(utility.get_frame()) if start_frame is None else float(start_frame)
    end_frame = start_frame if end_frame is None else float(end_frame)
    grps = form_heirarchy([groups.Group(t) for t in templates if t.enabled])
    if not grps: raise RuntimeError("No templates provided.")

    print("Matching Groups Now! Using \"%s\"." % matcher.__name__)
    print("Match order: {}".format(", ".join(a.get_name() for a in grps)))
    group_step = 1 / len(grps)
    total_calls = 0 # track total distance calls for reference

    yield 0.0 # Kick us off
    for i in range(int((end_frame - start_frame) / sub_frame)+1):
        frame = i * sub_frame + start_frame
        utility.set_frame(frame)
        for j, grp in enumerate(grps):
            grp.clear_cache()
            total_dist = grp.get_distance() # Set initial scale for progress updates
            total_scale = total_dist or 1.0 / total_dist
            for snapshot in matcher(grp, **kwargs):
                progress = 1 - snapshot.dist * total_scale
                yield progress * group_step + j * group_step
            grp.keyframe(snapshot.vals)
    print("Match complete. Took,", time.time() - start_time)
    print("Used %s calls." % sum(a.get_calls() for a in grps))
    yield 1.0
