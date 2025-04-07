"""
.. module:: test_add_flare_signal
   :synopsis: Regression tests for add_flare_signal

.. moduleauthor:: Scott W. Fleming
"""

import pytest
import numpy as np
from astronify.simulator.add_flare_signal import add_flare_signal

fluxes = np.asarray([1.0] * 100)
all_ones = np.asarray([1.0] * len(fluxes))
# params used for below: flare_time = 5, flare_amp = 100., flare_halfwidth = 5
# fmt: off
flare_within_window = np.asarray(
    [
        1.,   1.5,   4.73867187,  20.61875,
        54.45117188, 100.2,  79.50425097,  64.15981633,
        52.70811908,  44.09251539,  37.54729309,  32.51733859,
        28.59999823,  25.5030016,  23.0140085,  20.97856815,
        19.28416612,  17.8486771,  16.61200614,  15.53003747,
        14.57025342,  13.70856202,  12.92699942,  12.2120655,
        11.55351786,  10.94349742,  10.37589439,   9.84588794,
        9.34961192,   8.88391169,   8.44616705,   8.03416297,
        7.64599514,   7.28000052,   6.93470632,   6.60879213,
        6.30106173,   6.01042197,   5.7358667,   5.47646453,
        5.23134925,   4.99971236,   4.78079704,   4.57389328,
        4.37833382,   4.19349072,   4.01877245,   3.85362129,
        3.69751114,   3.54994541,   3.41045527,   3.27859792,
        3.15395508,   3.03613157,   2.92475397,   2.81946941,
        2.71994438,   2.6258637,   2.53692945,   2.45286004,
        2.37338931,   2.29826569,   2.22725134,   2.16012149,
        2.09666363,   2.03667689,   1.97997141,   1.92636768,
        1.87569605,   1.82779613,   1.7825163,   1.73971325,
        1.6992515,   1.66100297,   1.62484662,   1.59066798,
        1.5583589,   1.52781709,   1.4989459,   1.47165395,
        1.44585484,   1.42146692,   1.398413,   1.37662012,
        1.35601929,   1.33654531,   1.31813654,   1.30073471,
        1.28428476,   1.2687346,   1.25403502,   1.2401395,
        1.22700406,   1.21458711,   1.20284936,   1.19175366,
        1.18126488,   1.17134983,   1.16197712,   1.1531171
    ]
)
# fmt: on

# params used for below: flare_time = -10, flare_amp = 100., flare_halfwidth = 5
# fmt: off
flare_partialwithin_window = np.asarray(
    [
        21.00538825, 19.30895006, 17.87178393, 16.63374721, 15.55067206,
        14.58999083, 13.72756681, 12.94539788, 12.22995227, 11.57096202,
        10.96054795, 10.39258472,  9.86223975,  9.36563821,  8.8996192 ,
        8.46155815,  8.04923718,  7.66075016,  7.29443313,  6.94881294,
        6.62256927,  6.31450629,  6.02353143,  5.74863926,  5.48889915,
        5.24344568,  5.01147116,  4.79221953,  4.58498151,  4.38909051,
        4.20391922,  4.02887667,  3.86340566,  3.70698052,  3.55910508,
        3.41931084,  3.28715531,  3.16222047,  3.04411132,  2.93245464,
        2.82689767,  2.72710702,  2.63276756,  2.54358143,  2.45926706,
        2.37955827,  2.30420347,  2.2329648 ,  2.16561739,  2.1019487 ,
        2.04175775,  1.9848546 ,  1.93105963,  1.88020307,  1.83212442,
        1.78667194,  1.74370218,  1.70307952,  1.66467577,  1.62836971,
        1.59404677,  1.56159863,  1.53092287,  1.5019227 ,  1.47450657,
        1.44858798,  1.42408512,  1.40092066,  1.37902149,  1.3583185 ,
        1.33874636,  1.32024329,  1.30275089,  1.28621397,  1.27058034,
        1.25580064,  1.24182825,  1.22861906,  1.21613138,  1.20432581,
        1.19316509,  1.18261398,  1.17263921,  1.16320927,  1.15429442,
        1.14586652,  1.13789897,  1.13036663,  1.12324572,  1.11651376,
        1.11014953,  1.10413292,  1.09844495,  1.09306767,  1.08798411,
        1.08317822,  1.07863484,  1.07433964,  1.07027904,  1.06644025,
    ]
)
# fmt: on

"""
Test cases that result in return arrays:
1. flare_time pushes flare entirely outside the flux array
2. flare_time pushes the flare part-way outside the flux array
3. flare_time sets the flare to entirely consist within the flux array
4. a flare_amp of 0.0 is submitted
5. [TODO pending Issue #83] a float for flare_halfwidth that can be converted to an int is handled

Test cases that result in exceptions being thrown:
1. [TODO pending Issue #85] a negative value for flare_amp is submitted
2. [TODO pending Issue #85] a negative value for flare_halfwidth is submitted
3. [TODO pending Issue #83] a float for flare_halfwidth that can not be converted throws an exception
4. [TODO pending Issue #85] a flare_halfwidth of 0 is submitted
"""


@pytest.mark.parametrize(
    "flare_time, flare_amp, flare_halfwidth, expected_result",
    [
        (-10000, 100.0, 5, all_ones),
        (-10, 100.0, 5, flare_partialwithin_window),
        (5, 100.0, 5, flare_within_window),
        (5, 0.0, 5, all_ones),
    ],
)
def test_add_flare_signal(flare_time, flare_amp, flare_halfwidth, expected_result):
    assert np.allclose(
        add_flare_signal(fluxes, flare_time, flare_amp, flare_halfwidth),
        expected_result,
        atol=0,
        rtol=1e-8,
        equal_nan=True,
    )
