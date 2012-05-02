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
    cat_colors=[(-1, -1, 1),
                (-1, -.2, 1),
                (-1, .6, 1),
                (-1, 1, .6),
                (-1, 1, -.2),
                (-1, 1, -1)],
    cat_orients=[285, 315, 345,
                 15, 45, 75],

    # Event schedule
    # Note that this gets used by make_schedule
    # And should be hardcoded by runtime
    n_runs=10,
    trials_per_run=24,

    )

context_dmc = p

def add_cmdline_params(parser):

    return parser
