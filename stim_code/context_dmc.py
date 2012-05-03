from __future__ import division
import sys
import os.path as op
from textwrap import dedent
from numpy.random import randint
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

    # Get the schedule for this run
    sched_file = "schedules/run_%02d.csv" % p.run
    s = pandas.read_csv(sched_file)

    # Convenience map
    context_map = ["color", "orient"]

    # Draw the instructions and wait to go
    instruct = dedent("""
    Look at some things and do some stuff""")  # TODO
    tools.WaitText(win, instruct, height=.7)()

    # Start a data file and write the params to it
    f, fname = tools.start_data_file(p.subject, "context_dmc")
    p.to_text_header(f)

    # Write the datafile header
    header = ["trial", "context", "match",
              "samp_color", "samp_orient",
              "samp_color_cat", "samp_orient_cat",
              "targ_color", "targ_orient",
              "targ_color_cat", "targ_orient_cat",
              "cue_time", "psi", "isi", "iti",
              "response", "rt", "acc"]
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

        # Dummy scans
        fix.draw()
        win.flip()
        core.wait(p.dummy_trs * p.tr)

        for t in s.trial:

            context = context_map[s.context[t]]

            # Cue period
            cue_stims[context].draw()
            win.flip()
            cue_time = exp_clock.getTime()
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

            c_cat = a_cat if context == "color" else i_cat
            o_cat = a_cat if context == "orient" else i_cat
            c_exemp = a_exemp if context == "color" else i_exemp
            o_exemp = a_exemp if context == "orient" else i_exemp

            if context == "color":
                samp_color = p.cat_colors[a_cat][a_exemp]
                samp_orient = p.cat_orients[i_cat][i_exemp]
            else:
                samp_color = p.cat_colors[i_cat][i_exemp]
                samp_orient = p.cat_orients[a_cat][a_exemp]

            color.setColor(samp_color)
            grate.setOri(samp_orient)

            draw_all(*stims)
            win.flip()
            core.wait(p.stim_samp_dur)

            # Post stim fix and ISI
            fix.draw()
            win.flip()
            total_isi = p.stim_sfix_dur + s.isi_tr[t] * p.tr
            core.wait(total_isi)

            # Target stimulus
            match = s.match[t]
            idx2 = randint(2)
            idx3 = randint(3)
            if match:
                if context == "color":
                    t_c_cat = a_cat
                    t_o_cat = idx2
                elif context == "orient":
                    t_c_cat = idx2
                    t_o_cat = a_cat
            else:
                if context == "color":
                    t_c_cat = int(not a_cat)
                    t_o_cat = idx2
                elif context == "orient":
                    t_c_cat = idx2
                    t_o_cat = int(not a_cat)
            t_c_exemp, t_o_exemp = idx3, idx3
            targ_color = p.cat_colors[t_c_cat][t_c_exemp]
            targ_orient = p.cat_orients[t_o_cat][t_o_exemp]

            color.setColor(targ_color)
            grate.setOri(targ_orient)

            draw_all(*stims)
            win.flip()
            core.wait(p.stim_targ_dur)

            # Response
            r_fix.draw()
            win.flip()
            trial_clock.reset()
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
                    corr = 0 if match else 1
                    response = 2
                    resp_rt = stamp
                    break

            # Write out the trial data
            t_data = [t, context, match,
                      c_exemp, o_exemp,
                      c_cat, o_cat,
                      t_c_exemp, t_o_exemp,
                      t_c_cat, t_o_cat,
                      cue_time, s.psi_tr[t],
                      s.isi_tr[t], s.iti_tr[t],
                      response, resp_rt, corr]
            tools.save_data(f, *t_data)

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
