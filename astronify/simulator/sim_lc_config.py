
class SimLcConfig:
    """
    Class that holds the default configuration parameters
    for simulated light curves.
    """

    # General Parameters
    sim_lc_ofile = ""
    sim_lc_length = 500
    sim_lc_noise = 0.
    sim_lc_visualize = False
    sim_lc_yoffset = 100.
    
    # Transit Parameters
    sim_lc_transit_depth = 10.
    sim_lc_transit_period = 50.
    sim_lc_transit_start = 10
    sim_lc_transit_width = 5
    
    # Sinusoidal Parameters
    sim_lc_sine_amp = 10.
    sim_lc_sine_period = 50.

    # Flare Parameters
    sim_lc_flare_time = 10
    sim_lc_flare_amp = 100.
    sim_lc_flare_halfwidth = 5
