from __future__ import division
import sys
import os.path as op
from numpy.random import permutation
from pandas import DataFrame
import tools


def main(arglist):

    p = tools.Params("context_dmc")

    for run in range(1, p.n_runs + 1):
        df = build_run_schedule(p, run)
        fname = op.join("schedules", "run_%02d.csv" % run)
        df.to_csv(fname, index_label="trial")


def build_run_schedule(p, run):

    # Generate a schedule of events (context/category conjunction)
    events = tools.optimize_event_schedule(4,
                p.trials_per_run, p.trials_per_run,
                n_search=5000, enforce_balance=True)

    # Set up original groupings
    attend = [range(3) * 2 for i in range(4)]
    igncat = [range(2) * 3 for i in range(4)]
    ignexm = [[range(3), range(3)] for i in range(4)]

    psi_tr = [range(1, 4) * 2 for i in range(4)]
    isi_tr = [range(1, 4) * 2 for i in range(4)]
    iti_tr = [range(1, 4) * 2 for i in range(4)]

    # TODO this is shitty, do it better
    match_event = [range(2) * 3 for i in range(4)]

    # Randomize within groupings
    scramble = lambda x: [permutation(l).tolist() for l in x]
    attend = scramble(attend)
    igncat = scramble(igncat)
    ignexm = [[permutation(l).tolist() for l in c] for c in ignexm]

    cue_tr = scramble(psi_tr)
    isi_tr = scramble(isi_tr)
    iti_tr = scramble(iti_tr)

    # TODO also shitty
    match_event = scramble(match_event)

    # Set up blank schedule vectors
    context = []
    a_categ = []
    a_exemp = []
    i_categ = []
    i_exemp = []
    psi = []
    isi = []
    iti = []
    match = []

    # Build the schedule, event by event
    for i, event in enumerate(events):

        text = int(event < 2)
        context.append(text)

        acat = event % 2
        a_categ.append(acat)
        a_exemp.append(attend[event].pop())

        icat = igncat[event].pop()
        i_categ.append(icat)
        i_exemp.append(ignexm[event][icat].pop())

        psi.append(cue_tr[event].pop())
        isi.append(isi_tr[event].pop())
        iti.append(iti_tr[event].pop())

        match.append(match_event[event].pop())

    # Create a Pandas DataFrame
    df = DataFrame(dict(
        context=context,
        attend_cat=a_categ,
        attend_exemp=a_exemp,
        ignore_cat=i_categ,
        ignore_exemp=i_exemp,
        match=match,
        psi_tr=psi,
        isi_tr=isi,
        iti_tr=iti))

    return df

if __name__ == "__main__":
    main(sys.argv[1:])
