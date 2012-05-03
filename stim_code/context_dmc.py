from __future__ import division
import sys
import os.path as op
from textwrap import dedent
import numpy as np
from numpy.random import (permutation, binomial, multinomial,
                          randint, uniform)
from psychopy import visual, core, event
import pandas
import tools


def run_experiment(arglist):

    # Get the experiment parameters
    p = tools.Params("context_dmc")
    p.set_by_cmdline(arglist)

    # Open up the stimulus window
    m = tools.WindowInfo(p)
    win = visual.Window(**m.window_kwargs)

    # Set up the stimulus objects
    fix = visual.PatchStim(win, tex=None, mask="circle",
                       color=p.fix_color, size=p.fix_size)
    r_fix = visual.PatchStim(win, tex=None, mask="circle",
                             color=p.fix_resp_color, size=p.fix_size)
    grate = visual.PatchStim(win, "sin", "circle", sf=p.stim_sf,
                             size=p.stim_size, opacity=1)
    color = visual.PatchStim(win, None, "circle",
                             size=p.stim_size, opacity=.4)
    disk = visual.PatchStim(win, tex=None, mask="circle",
                            color=win.color, size=p.stim_size / 6)
    stims = [grate, color, disk, fix]

    # TODO more options in params.py
    color_text = visual.TextStim(win, text="color")
    orient_text = visual.TextStim(win, text="orient")
    cue_stims = dict(color=color_text, orient=orient_text)

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

    # Get the schedule for this run
    sched_file = "schedules/run_%02d.csv" % p.run
    s = pandas.read_csv(sched_file)

    context_map = ["color", "orient"]

    # Main experiment loop
    # --------------------
    try:

        for t in s.trial:

            context = context_map[s.context[t]]

            # Cue period
            cue_stims[context].draw()
            win.flip()
            core.wait(p.cue_dur)

            # Pre-stim fixation (PSI)
            fix.draw()
            win.flip()
            core.wait(s.psi_tr[t] * p.tr)

            # Sample stimulus
            a_cat = s.attend_cat[t]
            a_exemp = s.attend_exemp[t]

            i_cat = s.ignore_cat[t]
            i_exemp = s.ignore_exemp[t]

            if context == "color":
                stim_color = p.cat_colors[a_cat][a_exemp]
                stim_orient = p.cat_orients[i_cat][i_exemp]
            else:
                stim_color = p.cat_colors[i_cat][i_exemp]
                stim_orient = p.cat_orients[a_cat][a_exemp]

            color.setColor(stim_color)
            grate.setOri(stim_orient)

            draw_all(*stims)
            win.flip()
            core.wait(p.stim_samp_dur)

            # Post stim fix and ISI
            fix.draw()
            win.flip()
            total_isi = p.stim_sfix_dur + s.isi_tr[t] * p.tr
            core.wait(total_isi)

            # Target stimulus
            # TODO ugh this logic sucks
            # TODO also check that it works in general
            match = s.match[t]
            if match:
                if context == "color":
                    stim_color = p.cat_colors[a_cat][randint(3)]
                    stim_orient = p.cat_orients[randint(2)][randint(3)]
                elif context == "orient":
                    stim_color = p.cat_colors[randint(2)][randint(3)]
                    stim_orient = p.cat_colors[a_cat][randint(3)]
            else:
                if context == "color":
                    stim_color = p.cat_colors[int(not a_cat)][randint(3)]
                    stim_orient = p.cat_orients[randint(2)][randint(3)]
                elif context == "orient":
                    stim_color = p.cat_colors[randint(2)][randint(3)]
                    stim_orient = p.cat_colors[int(not a_cat)][randint(3)]

            color.setColor(stim_color)
            grate.setOri(stim_orient)

            draw_all(*stims)
            win.flip()
            core.wait(p.stim_targ_dur)

            # Response
            r_fix.draw()
            win.flip()
            core.wait(p.resp_dur)

            # Collect the response
            keys = event.getKeys(timeStamped=trial_clock)
            corr, response, resp_rt = 0, 0, -1
            for key, stamp in keys:
                if key in p.quit_keys:
                    core.quit()
                elif key in p.match_keys:
                    corr = 1 if match else 0
                    response = 1
                    resp_rt = stamp
                    break
                elif key in p.nonmatch_keys:
                    corr = 1 if not match else 0
                    response = 2
                    resp_rt = stamp
                    break

            # ITI interval
            fix.draw()
            win.flip()
            core.wait(s.iti_tr[t] * p.tr)

    finally:
        # Clean up
        f.close()
        win.close()


def draw_all(*args):
    for stim in args:
        stim.draw()

if __name__ == "__main__":
    sys.exit(run_experiment(sys.argv[1:]))
