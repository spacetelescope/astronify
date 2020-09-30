#!/bin/sh

# Flat light curves:
#python sim_lc.py flat outputs/flat_nonoise.fits -v
#python sim_lc.py flat outputs/flat_noise-1.fits -v -n 1
#python sim_lc.py flat outputs/flat_noise-10.fits -v -n 10

# Transit light curves:
#python sim_lc.py transit outputs/transit_nonoise.fits -v
#python sim_lc.py transit outputs/transit_shallow_withnoise.fits -v --transit_depth 1.5 --transit_period 145 --transit_width 42 -n 0.5

# Sinosoidal light curves:
#python sim_lc.py sine outputs/sine_nonoise.fits -v
#python sim_lc.py sine outputs/sine_shallow_withnoise.fits -v --sine_amp 1.5 --sine_period 142 -n 0.5

# Flare light curves:
python sim_lc.py flare outputs/flare_nonoises.fits -v
