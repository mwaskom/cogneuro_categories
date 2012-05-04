base = dict(

    # Display setup
    monitor_name="mlw-mbpro",
    monitor_units="deg",
    full_screen=True,
    screen_number=0,

    # Fixation
    fix_size=.15,
    fix_color="white",
    fix_resp_color="#FFD733",

    # Basic Gratings
    stim_size=5,
    stim_contrast=.5,
    stim_sf=3,
    stim_mask="gauss",

    # Category information
    cat_colors=[[(-1, -1, 1),
                 (-1, -.2, 1),
                 (-1, .6, 1)],
                [(-1, 1, .6),
                 (-1, 1, -.2),
                 (-1, 1, -1)]],
    cat_orients=[[285, 315, 345],
                 [15, 45, 75]],

    )

context_dmc = dict(

    experiment_name="context_dmc",

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
    dummy_trs=4,

    # Response settings
    quit_keys=("escape", "q"),
    match_keys=("2", "comma"),
    nonmatch_keys=("3", "period"),

    )
context_dmc.update(base)

category_train = dict(

    # Schedule
    cue_dur=2,
    n_per_block=12,
    acc_threshold=1,
    good_blocks=2,
    stim_dur=.5,
    feedback_dur=.5,
    isi=1,

    # Feedback colors
    right_color="#00FF75",
    wrong_color="#FF4215",

    # Response keys
    cat_one_key="comma",
    cat_two_key="period",
    resp_keys=["comma", "period"],

)
category_train.update(context_dmc)


def add_cmdline_params(parser):

    return parser
