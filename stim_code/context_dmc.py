from __future__ import division
import sys
import os.path as op
from textwrap import dedent
import numpy as np
from numpy.random import (permutation, binomial, multinomial,
                          randint, uniform)
from psychopy import visual, core, event
import tools

def run_experiment(arglist):

    # Get the experiment parameters
    p = tools.Params("contxt_dmc")
    p.set_by_cmdline(arglist)

    # Open up the stimulus window
    m = tools.WindowInfo(p)
    win = visual.Window(**m.window_kwargs)


    # Set up the context schedule
    n_blocks = p.blocks_per_run
    block_context = tools.optimize_event_schedule(2, n_blocks,
                        max_repeat=p.max_context_repeat,
                        n_search=1000,
                        enforce_balance=True)

    # Set up the stimulus objects
    fix = visual.PatchStim(win, tex=None, mask="circle",
                       color=p.fix_color, size=p.fix_size)

    r_fix = visual.PatchStim(win, tex=None, mask="circle",
                             color=p.fix_resp_color, size=p.fix_size)
    grate = visual.PatchStim(win, p.stim_tex, p.stim_mask,
                             size=p.stim_size, contrast=p.stim_contrast,
                             sf=p.stim_sf, opacity=p.stim_opacity)
    disk = visual.PatchStim(win, tex=None, mask="circle",
                            color=win.color, size=p.stim_size / 6)
    stims = [grate, disk, fix]

    # Draw the instructions and wait to go
    instruct = dedent("""
    Look at some things and do some stuff""")  # TODO
    tools.WaitText(win, instruct, height=.7)()

    # Start a data file and write the params to it
    f, fname = tools.start_data_file(p.subject, "context_dmc")
    p.to_text_header(f)

    # TODO log by stim, add total time
    header = ["trial", "block", "context",
              "samp_color", "samp_orient",
              "samp_color_cat", "samp_orient_cat",
              "targ_color", "targ_orient",
              "targ_color_cat", "targ_orient_cat",
              "delay", "response", "rt", "acc", "elapsed"]
    tools.save_data(f, *header)

    # Set up output variable
    save_name = op.join("./data", op.splitext(fname)[0])

    # Start a clock and flush the event buffer
    exp_clock = core.Clock()
    trial_clock = core.Clock()
    event.clearEvents()

    # Main experiment loop
    # --------------------
    try:
        pass
    finally:
        # Clean up
        f.close()
        win.close()

if __name__ == "__main__":
    sys.exit(run_experiment(sys.argv[1:]))
