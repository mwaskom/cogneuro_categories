p = dict(

    # Display setup
    monitor_name='ben-octocore',
    monitor_units="deg",
    full_screen=True,
    screen_number=0,

    # Fixation
    fix_size=.15,
    fix_color='white',
    fix_antic_color='red',
    fix_resp_color='green',

    # Basic Gratings
    stim_size=5,
    stim_contrast=1,
    stim_sf=3,

    # Category information
    cat_colors=[[(-1, -1, 1),
                 (-1, -.2, 1),
                 (-1, .6, 1)],
                [(-1, 1, .6),
                 (-1, 1, -.2),
                 (-1, 1, -1)]],
    cat_orients=[[285, 315, 345],
                 [15, 45, 75]],

    # Event schedule
    # Note that this gets used by make_schedule
    # And should be hardcoded by runtime
    n_runs=12,
    trials_per_run=24,

    # Timing
    tr=2,
    cue_dur=2,
    stim_samp_dur=.5,
    stim_sfix_dur=1.5,
    stim_targ_dur=.5,
    resp_dur=1.5,

    # Response settings
    quit_keys=("escape", "q"),
    match_keys=('1', ','),
    nonmatch_key=('2', '.'),

    )

context_dmc = p

def add_cmdline_params(parser):

    return parser
