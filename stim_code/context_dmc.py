from __future__ import division
import sys
import os.path as op
from textwrap import dedent
from numpy.random import randint
from psychopy import visual, core, event
import psychopy.monitors.calibTools as calib
from matplotlib.mlab import csv2rec
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
                             size=p.stim_size, contrast=p.stim_contrast)
    color = visual.PatchStim(win, None, p.stim_mask,
                             size=p.stim_size, opacity=.4)
    disk = visual.PatchStim(win, tex=None, mask="gauss",
                            color=win.color, size=p.stim_size / 6)
    stims = [grate, color, disk, fix]

    # Set up the cue stimuli
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
    Say whether the two stimuli in each trial match
    on the relevant category dimension

    1 = match                          2 = nonmatch

    Experimenter: press space to begin""")
    tools.WaitText(win, instruct, height=.7)(check_keys=["space"])

    # Possibly wait for the scanner
    if p.fmri:
        tools.wait_for_trigger(win, p)

    # Start a data file and write the params to it
    f, fname = tools.start_data_file(p.subject, p.experiment_name, p.run)
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
        dummy_secs = p.dummy_trs * p.tr
        wait_check_quit(dummy_secs, p.quit_keys)

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
            psi_secs = s.psi_tr[t] * p.tr
            wait_check_quit(psi_secs, p.quit_keys)

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
            isi_secs = p.stim_sfix_dur + (s.isi_tr[t] * p.tr)
            wait_check_quit(isi_secs, p.quit_keys)

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
            trial_clock.reset()
            event.clearEvents()
            win.flip()
            core.wait(p.resp_dur)

            # Collect the response
            corr, resp, resp_rt = collect_response(p, trial_clock, match)

            # ITI interval
            fix.draw()
            win.flip()
            iti_secs = s.iti_tr[t] * p.tr
            core.wait(iti_secs)

            # Possibly check for late response
            if resp == -1:
                corr, resp, resp_rt = collect_response(p, trial_clock, match)

            # Write out the trial data
            t_data = [t, context, match,
                      c_exemp, o_exemp,
                      c_cat, o_cat,
                      t_c_exemp, t_o_exemp,
                      t_c_cat, t_o_cat,
                      cue_time, s.psi_tr[t],
                      s.isi_tr[t], s.iti_tr[t],
                      resp, resp_rt, corr]
            tools.save_data(f, *t_data)
            f.flush()

            # Check for a quit request
            # (We can't check during the ITI because we
            # want to listen for a potentially late response)
            check_quit(p.quit_keys)

    finally:
        # Clean up
        f.close()
        win.close()

    # Calculate some performance data and print it to the screen
    data = csv2rec(op.join("data", fname))
    accuracy = data["acc"].mean()
    rt = data["rt"][data["rt"] > 0].mean()
    missed = (data["response"] == -1).sum()

    print "Run: %d" % p.run
    print "Accuracy: %.2f" % accuracy
    print "Mean RT: %.4f" % rt
    print "Missed responses: %d" % missed


def collect_response(p, clock, match):
    """Get response info specific to this experiment."""
    keys = event.getKeys(timeStamped=clock)
    corr, response, resp_rt = 0, -1, -1
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
    return corr, response, resp_rt


if __name__ == "__main__":
    sys.exit(run_experiment(sys.argv[1:]))
