from __future__ import division
import sys
from textwrap import dedent
import numpy as np
from numpy.random import randint
from psychopy import visual, core, event
import psychopy.monitors.calibTools as calib
import tools
from tools import draw_all, wait_check_quit


def run_experiment(arglist):

    # Get the experiment parameters
    p = tools.Params("category_train")
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
                            color=win.color, size=p.stim_size / 4)
    right_patch = visual.PatchStim(win, tex=None, mask="gauss",
                                   color=p.right_color, size=p.stim_size / 6)
    wrong_patch = visual.PatchStim(win, tex=None, mask="gauss",
                                   color=p.wrong_color, size=p.stim_size / 6)

    stims = [grate, color, disk, fix]
    right = [right_patch, fix]
    wrong = [wrong_patch, fix]
    feedback = [wrong, right]

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
    #f, fname = tools.start_data_file(p.subject, p.experiment_name, p.run)
    #p.to_text_header(f)

    # Set up accuracy lists
    contexts = ["color", "orient"]
    color_acc = np.zeros(p.n_per_block)
    orient_acc = np.zeros(p.n_per_block)
    acc_arrays = dict(orient=orient_acc, color=color_acc)
    context_done = dict(color=0, orient=0)
    is_trained = dict(color=False, orient=False)
    train_blocks = dict(color=0, orient=0)

    # Main experiment loop
    try:

        trained = False
        while not trained:

            # Only do context that needs training
            while True:
                context = contexts[randint(2)]
                if not is_trained[context]:
                    break

            # Context cue
            cue_stims[context].draw()
            win.flip()
            wait_check_quit(p.cue_dur, p.quit_keys)

            # Prestim fix
            fix.draw()
            win.flip()
            wait_check_quit(p.isi)

            # Iterate through the block
            for t in range(p.n_per_block):

                # Set up the stimulus
                a_category = randint(2)
                a_exemplar = randint(3)
                i_category = randint(2)
                i_exemplar = randint(3)

                if context == "color":
                    col = p.cat_colors[a_category][a_exemplar]
                    ori = p.cat_orients[i_category][i_exemplar]
                else:
                    col = p.cat_colors[i_category][i_exemplar]
                    ori = p.cat_orients[a_category][a_exemplar]

                color.setColor(col)
                grate.setOri(ori)

                # Draw the stimulus
                draw_all(*stims)
                win.flip()
                core.wait(p.stim_dur)

                # Draw the resp fix and wait
                r_fix.draw()
                win.flip()
                response = wait_for_response(p)
                correct = int(response == a_category)
                acc_arrays[context][t] = correct

                # Draw the feedback
                draw_all(*feedback[correct])
                win.flip()
                wait_check_quit(p.feedback_dur)

                # Draw the ISI fix
                fix.draw()
                win.flip()
                wait_check_quit(p.isi)

            if acc_arrays[context].mean() >= p.acc_threshold:
                context_done[context] += 1
            if context_done[context] == p.good_blocks:
                is_trained[context] = True

            # Update the block counts
            train_blocks[context] += 1

            # Check if training is done
            trained = all(is_trained.values())

    finally:
        #f.close()
        win.close()

    # Print out information about training
    print "Training done!"
    print "Total color blocks: %d" % train_blocks["color"]
    print "Total orient blocks: %d" % train_blocks["orient"]


def wait_for_response(p):
    """Get response info specific to this experiment."""
    listen_keys = p.resp_keys + list(p.quit_keys)
    response = None
    while response is None:
        for key in event.getKeys(keyList=listen_keys):
            if key in p.quit_keys:
                core.quit()
            elif key == p.cat_one_key:
                response = 0
                break
            elif key == p.cat_two_key:
                response = 1
                break
    return response

if __name__ == "__main__":
    run_experiment(sys.argv[1:])
