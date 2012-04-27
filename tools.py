from __future__ import division

import os
import time
import argparse
import cPickle
from glob import glob
from subprocess import call
import numpy as np
from numpy.random import permutation, multinomial
from psychopy import core, event, visual


class Params(object):
    """Stores all of the parameters needed during the experiment.

    Some parameters are set upon initialization from the file 'params.py',
    others are set from the command line.

    """
    def __init__(self, exp_name, p_file='params'):
        """Initializer for the params object.

        Parameters
        ----------
        exp_name: string, name of the dict we want from the param file

        p_file: string, the name of a parameter file

        """
        self.exp_name = exp_name
        im = __import__(p_file)
        param_dict = getattr(im, exp_name)
        for key, val in param_dict.items():
            setattr(self, key, val)

    def set_by_cmdline(self, arglist):
        """Get runtime parameters off the commandline."""
        # Create the parser, set default args
        parser = argparse.ArgumentParser()
        parser.add_argument("-subject", default="test")
        parser.add_argument("-debug", action="store_true")

        # Add additional arguments by experiment
        try:
            add_args = getattr(self, "_add_%s_args" % self.exp_name)
            parser = add_args(parser)
        except AttributeError:
            pass
        print parser

        # Parse the arguments
        args = parser.parse_args(arglist)

        # Check for required arguments
        # (They're mutally exclusive so argparse's
        # build in required functionality won't work
        if (self.exp_name == "percep" and 
            not any([args.group, args.free])):
            raise ValueError("Must set either -group or -free")

        # Add command line args to the class dict
        self.__dict__.update(args.__dict__)

        if self.debug:
            self.full_screen = False

    def _add_percep_args(self, parser):
        """Add command line args for percep experiment."""
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-free', action="store_true")
        group.add_argument('-group', action="store_true")
        parser.add_argument("-pklfile")
        return parser

    def save(self, fid):
        """Save the parameters to a text file."""
        for key, val in self.__dict__.items():
            if not key.startswith("_"):
                fid.write("# %s : %s \n" % (key, val))


def start_data_file(subject_id, exp):
    """Start a file object into which you will write the data.

    Makes sure sure not to over-write previously existing files.

    """
    list_data_dir = os.listdir('./data')

    i = 1
    data_file = '%s_%s_%s_%d.csv' % (subject_id, exp,
                                     time.strftime('%m%d%Y'), i)
    while data_file in list_data_dir:
        i += 1
        data_file = '%s_%s_%s_%d.csv' % (subject_id, exp,
                                       time.strftime('%m%d%Y'), i)

    #Open the file for writing into:
    f = file('./data/%s' % data_file, 'w')

    #Write some header information
    f.write('# time : %s\n' % (time.asctime()))

    return f, data_file


def max_brightness(monitor):
    """Maximize the brightness on a laptop."""
    if monitor in ["mlw-mbpro", "WendyO"]:
        try:
            call(["brightness", "1"])
        except OSError:
            print "Could not modify screen brightness"


def save_data(f, *arg):

    for a in arg[0:-1]:
        f.write('%s,' % a)

    #Don't put a comma after the last one:
    f.write('%s\n' % arg[-1])

    return f


class WaitText(object):
    """A class for showing text on the screen until a key is pressed. """
    def __init__(self, win, text='Press a key to continue', **kwargs):
        """Set the text stimulus information.

        Will do the default thing(show 'text' in white on gray background),
        unless you pass in kwargs, which will just go through to
        visual.TextStim (see docstring of that class for more details)

        """
        self.win = win
        self.text = visual.TextStim(win, text=text, **kwargs)

    def __call__(self, duration=np.inf):
        """Dislpay text until a key is pressed or until duration elapses."""
        clock = core.Clock()
        t = 0
        #Keep going for the duration
        while t < duration:
            t = clock.getTime()
            self.text.draw()
            self.win.flip()
            for key in event.getKeys():
                if key:
                    return


def get_oddball_delta(params):
    """Figure out the SF delta for oddballs."""

    if params.debug:
        return .5
    if params.pklfile is not None:
        staircase = cPickle.load(open(params.pklfile))
    else:
        pkl_list = sorted(glob("data/%s_staircase_*.psydat" % params.subject))
        try:
            staircase = cPickle.load(open(pkl_list[-1]))
        except IndexError:
            raise RuntimeError("Could not find staircase file.")
    oddball_delta = np.mean(staircase.intensities[-params.staircase_tail:])

    return oddball_delta


def max_three_in_a_row(seq):
    """Only allow sequences with 3 or fewer tokens in a row.

    This assumes the tokens are represnted by integers in [0, 9].

    """
    seq_str = "".join(map(str, seq))
    for item in np.unique(seq):
        item_str = str(item)
        check_str = "".join([item_str for i in range(4)])
        if check_str in seq_str:
            return False
    return True


def max_four_in_a_row(seq):
    """Only allow sequences with 4 or fewer tokens in a row.

    This assumes the tokens are represnted by integers in [0, 9].

    """
    seq_str = "".join(map(str, seq))
    for item in np.unique(seq):
        item_str = str(item)
        check_str = "".join([item_str for i in range(5)])
        if check_str in seq_str:
            return False
    return True


def make_schedule(n_cat, n_total, max_repeat):
    """Generate an event schedule subject to a repeat constraint."""

    # Make the uniform transition matrix
    ideal_tmat = [1 / n_cat] * n_cat
    # Build the transition matrices for when we've exceeded our repeat limit
    const_mat_list = []
    for i in range(n_cat):
        const_mat_list.append([1 / (n_cat - 1)] * n_cat)
        const_mat_list[-1][i] = 0

    # Convenience function to make the transitions
    cat_range = np.arange(n_cat)
    draw = lambda x: np.asscalar(cat_range[multinomial(1, x).astype(bool)])

    # Generate the schedule
    schedule = []
    for i in xrange(n_total):
        trailing_set = set(schedule[-max_repeat:])
        # Check if we're at our repeat limit
        if len(trailing_set) == 1:
            tdist = const_mat_list[trailing_set.pop()]
        else:
            tdist = ideal_tmat
        # Assign this iteration's state
        schedule.append(draw(tdist))

    return schedule


def optimize_event_schedule(n_cat, n_total, max_repeat,
                            n_search=1000, enforce_balance=False):
    """Generate an event schedule optimizing CB1 and even conditions.

    Parameters
    ----------
    n_cat: int
        Total number of event types
    n_total: int
        Total number of events
    max_repeat: int
        Maximum number of event repetitions allowed
    n_search: int
        Size of the searc space
    enforce_balance: bool
        If true, raises a ValueError if event types are not balanced

    Returns
    -------
    schedule: numpy array
        Optimal event schedule with 0-based event ids

    """
    # Determine the idea transition matrix
    ev_count = [n_total / n_cat] * n_cat
    ideal = cb1_ideal(ev_count)

    # Generate the space of schedules
    schedules = []
    bal_costs = np.zeros(n_search)
    cb1_costs = np.zeros(n_search)
    for i in xrange(n_search):
        sched = make_schedule(n_cat, n_total, max_repeat)
        schedules.append(sched)

        # Determine balance cost
        hist = np.histogram(sched, n_cat)[0]
        bal_costs[i] = np.sum(np.abs(hist - hist.mean()))

        # Determine CB1 cost
        cb1_mat = cb1_prob(sched, ev_count)
        cb1_costs[i] = cb1_cost(ideal, cb1_mat)

    # Possibly error out if schedules are not balanced
    if enforce_balance and bal_costs.min():
        raise ValueError("Failed to generate balanced schedule")

    # Zscore the two costs and sum
    zscore = lambda x: (x - x.mean()) / x.std()
    bal_costs = zscore(bal_costs)
    cb1_costs = zscore(cb1_costs)
    costs = bal_costs + cb1_costs

    # Return the best schdule
    return np.array(schedules[np.argmin(costs)])


def cb1_optimize(ev_count, n_search=1000, constraint=None):
    """Given event counts, return a first order counterbalanced schedule.

    Note that this is a stupid brute force algorithm. It's bascially a Python
    port of Doug Greve's C implementation of this in optseq with the addition
    of a constraint option.

    Inputs
    ------
    ev_count: sequence
        desired number of appearences for each event t
    constraint: callable
        arbitrary function that takes a squence and returns a boolean
    n_search: int
        iterations of search algorithm

    """
    # Figure the total event count
    ev_count = np.asarray(ev_count)
    n_total = ev_count.sum()

    # Set up a default constraint function
    if constraint is None:
        constraint = lambda x: True

    # Create the ideal FOCB matrix
    ideal = cb1_ideal(ev_count)

    # Make an unordered schedule
    sched_list = []
    for i, n in enumerate(ev_count, 1):
        sched_list.append(np.ones(n, int) * i)
    sched = np.hstack(sched_list)

    # Create n_search random schedules and pick the best one
    sched_costs = np.zeros(n_search)
    best_sched = sched
    for i in xrange(n_search):
        iter_sched = sched[permutation(int(n_total))]
        if not constraint(iter_sched):
            continue
        iter_cb1_mat = cb1_prob(iter_sched, ev_count)
        iter_cost = cb1_cost(ideal, iter_cb1_mat)
        sched_costs[i] = iter_cost
        if (not i) or (cb1_cost == sched_costs[:i].min()):
            best_sched = iter_sched

    # Make sure we could permute
    if np.array_equal(best_sched, sched):
        raise ValueError("Could not satisfy constraint")

    return best_sched


def cb1_ideal(ev_count):
    """Calculate the ideal FOCB matrix"""
    n_events = len(ev_count)
    ideal = np.zeros((n_events, n_events))
    ideal[:] = ev_count / np.sum(ev_count)
    return ideal


def cb1_prob(sched, ev_count):
    """Calculate the empirical FOCB matrix from a schedule."""
    n_events = len(ev_count)
    cb_mat = np.zeros((n_events, n_events))
    for i, event in enumerate(sched[:-1]):
        next_event = sched[i + 1]
        cb_mat[event - 1, next_event - 1] += 1

    for i, count in enumerate(ev_count):
        cb_mat[i] /= count

    return cb_mat


def cb1_cost(ideal_mat, test_mat):
    """Calculate the error between ideal and empirical FOCB matricies."""
    cb1err = np.abs(ideal_mat - test_mat)
    cb1err /= ideal_mat
    cb1err = cb1err.sum()
    cb1err /= ideal_mat.shape[0] ** 2
    return cb1err
