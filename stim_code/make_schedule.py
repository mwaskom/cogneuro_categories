from __future__ import division
import sys
import numpy as np
from numpy.random import (permutation, binomial, multinomial,
                          randint, uniform)
from pandas import DataFrame
import tools


def main(arglist):

    p = tools.Params("context_dmc")



def write_run_schedule(p, run):

    # Generate a schedule of events (context/category conjunction)
    events = tools.optimize_event_schedule(4,
                p.trials_per_run, p.trials_per_run,
                n_search=5000, enforce_balance=True)

    # Set up original groupings
    attend = [range(3) * 2 for i in range(4)]
    igncat = [range(2) * 3 for i in range(4)]
    ignexm = [[range(3), range(3)] for i in range(4)]

    cue_tr = [range(1, 4) * 2 for i in range(4)]
    del_tr = [range(1, 4) * 2 for i in range(4)]
    iti_tr = [range(1, 4) * 2 for i in range(4)]

    # Randomize within groupings
    attend = [permutation(l).tolist() for l in attend]
    igncat = [permutation(l).tolist() for l in igncat]
    ignexm = [[permutation(l).tolist() for l in c] for c in ignexm]

    cue_tr = [permutation(l).tolist() for l in cue_tr]
    isi_tr = [permutation(l).tolist() for l in del_tr]
    iti_tr = [permutation(l).tolist() for l in iti_tr]

    # Set up blank schedule vectors
    context = []
    a_categ = []
    a_exemp = []
    i_categ = []
    i_exemp = []
    cue = []
    isi = []
    iti = []

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

        cue.append(cue_tr[event].pop())
        isi.append(isi_tr[event].pop())
        iti.append(iti_tr[event].pop())

    # Create a Pandas DataFrame
    df = DataFrame(dict(
        context=context,
        attend_cat=a_categ,
        attend_exemp=a_exemp,
        ignore_cat=i_categ,
        ignore_exemp=i_exemp,
        cue_tr=cue,
        isi_tr=isi,
        iti_tr=iti))

    return df

if __name__ == "__main__":
    main(sys.argv[1:])
