from __future__ import division
import sys
from textwrap import dedent
from numpy.random import randint
from psychopy import visual, core, event
import psychopy.monitors.calibTools as calib
import pandas
import tools
from tools import draw_all, check_quit, wait_check_quit


def run_experiment(arglist):

    # Get the experiment parameters
    p = tools.Params("context_dmc")
    p.set_by_cmdline(arglist)

    # Open up the stimulus window
    calib.monitorFolder = "./calib"
    mon = calib.Monitor(p.monitor_name)
    m = tools.WindowInfo(p, mon)
    win = visual.Window(**m.window_kwargs)

    # Set up the stimulus objects
    fix = visual.PatchStim(win, tex=None, mask="circle",
                       color=p.fix_color, size=p.fix_size)
    r_fix = visual.PatchStim(win, tex=None, mask="circle",
                             color=p.fix_resp_color, size=p.fix_size)
    grate = visual.PatchStim(win, "sin", p.stim_mask, sf=p.stim_sf,
                             size=p.stim_size, opacity=1)
    color = visual.PatchStim(win, None, p.stim_mask,
                             size=p.stim_size, opacity=.4)
    disk = visual.PatchStim(win, tex=None, mask="gauss",
                            color=win.color, size=p.stim_size / 6)
    right_patch = visual.PatchStim(win, tex=None, mask="gauss",
                                   color=p.right_color, size=p.stim_size / 6)
    wrong_patch = visual.PatchStim(win, tex=None, mask="gauss",
                                   color=p.wrong_color, size=p.stim_size / 6)

    stims = [grate, color, disk, fix]
    right = [right_patch, fix]
    wrong = [wrong_patch, fix]

    # Set up the cue stimuli
    color_text = visual.TextStim(win, text="color")
    orient_text = visual.TextStim(win, text="orient")
    cue_stims = dict(color=color_text, orient=orient_text)

    # Draw the instructions and wait to go
    instruct = dedent("""
    Categorize the stimuli see along the instructed
    dimension, based on the feedback you will receive.

    Use the '<' and '>' keys to indicate category identity.

    Green feedback means correct, red means incorrect.
    """)

    tools.WaitText(win, instruct, height=.7)(check_keys=["space"])

    # TODO this?
    # Start a data file and write the params to it
    f, fname = tools.start_data_file(p.subject, p.experiment_name, p.run)
    p.to_text_header(f)

    # Set up accuracy lists
    color_acc = []
    orien_acc = []

    # Main experiment loop
    try:

        # Go until we hit a criterion
        while True:
            pass

    finally:
        f.close()
        win.close()
