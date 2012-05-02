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
    stim_tex="sin",
    stim_mask="circle",
    stim_contrast=1,
    stim_opacity=1,
    stim_sf=1.5,

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
    blocks_per_run=4,
    max_context_repeat=4,

    )

def add_cmdline_params(parser):

    return parser
