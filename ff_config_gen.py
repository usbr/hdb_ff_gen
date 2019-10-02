# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 08:42:01 2019

@author: buriona
"""

import json
from os import path

if __name__ == '__main__':

    alt_path = path.join('T:\\', 'Power', 'Reservoir Operations', 'flat_files')

    one_off_sites = [919, 743]
    one_off_datatypes = [19, 20, 34, 33]

    testing_sites = [917, 729]
    testing_datatypes = [29, 30, 49, 42, 43, 17, 19, 20]

    crsp_reservoirs = [
        912, 913, 914, 915, 1119, 917, 916, 958, 914, 920, 933, 919,                #UCR
        934, 3083, 935                                                              #susan
    ]

    pao_reservoirs = [                                                              #gary henrie
        957, 959, 947, 941, 942, 940, 938, 946, 925, 3608, 3607, 3609,
        964, 953, 3606, 936, 954, 944, 949, 963, 952, 962, 928, 930,
        960, 927, 931, 956, 932
    ]

    aao_reservoirs = [
        1094, 2686, 2685, 2730, 943, 937, 2684, 2729, 2696, 2744
    ]

    misc_reservoirs = [
        1998, 1999, 2000, 948, 2002, 2003, 2005
    ]

    lc_reservoirs = [
        1037, 3446, 3620, 1022, 1469, 1034, 3840, 4074, 919, 2745, 923, 921,
        3258, 922, 1103, 1038, 3579, 3578, 1033, 1099
    ]

    eco_reservoirs = [
        100081, 100089, 100120, 100001, 100010, 100017, 100104, 100100, 100031,
        100049, 100053, 100118, 100163, 100257]

    eco_gages = [
        100090, 100055, 100011, 100062, 100027, 100047, 100111, 100073]

    all_res_data = list(
        set(crsp_reservoirs + pao_reservoirs + aao_reservoirs + misc_reservoirs)
    )

    usgs_gages = [
        1714, 1735, 1542, 1548, 1550, 1552, 1553, 1733, 1555, 1559, 1560, 1737,
        1562, 1065, 1066, 1067, 1095, 1717, 1720, 1734, 1113, 1738, 1116, 1633,
        3684, 1718, 1731, 1728, 1716, 1721, 2722, 2723, 2741, 1729, 1712, 716,
        729, 731, 733, 734, 735, 736, 738, 739, 742, 743, 757, 1732, 767, 1709,
        771, 772, 773, 774, 776, 777, 783, 786, 787, 789, 799, 802, 1711, 1736,
        859, 1723, 1705, 1719, 900, 1708, 1713, 907, 1715, 1730, 451, 1722,
        3028, 3029, 726, 1513, 1514, 1710, 1534
    ]

    usgs_gages = list(set(usgs_gages))

    res_data_types = [
        49, 25, 29, 30, 49, 39, 40, 43, 46, 17, 42, 33, 34, 15, 1197, 1198, 47,
        123, 124, 1501
    ]

    eco_res_data_types = [
        17, 49
    ]
    eco_gage_data_types = [
        19
    ]

    gage_data_types = [19, 20]

    lbo_sites = [60000, 60001, 60002, 60003, 60004, 60005, 60006, 60007,
                 60008, 60009, 60010, 60011, 60012, 60013, 60014, 60015,
                 60016, 60017, 60018, 60019, 60020, 60021, 60022, 60023,
                 60024, 60025, 60026, 60027, 60028, 60029, 60030, 60031,
                 60032, 60033, 60034, 60035, 60036, 60037]

    lbo_datatypes = [66, 65, 120, 19, 20, 18, 65]

    snotel_ids = [
        226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
        240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253,
        254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,
        268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281,
        283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296,
        297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310,
        311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324,
        325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338,
        339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352,
        353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366,
        367, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381,
        383, 384, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082,
        1140, 2683, 2662, 2663, 2664, 2666, 2667, 2668, 2669, 2670, 2671, 2672,
        2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 3692, 3693,
        3698, 3700, 3702, 3704, 3706, 3708, 3709, 3711, 3713, 3715, 3717, 3719,
        3721, 3723, 3726, 3728, 3730, 3732, 3734, 3736, 3738, 3740, 3742, 3744,
        3746, 3748, 3750, 3694, 3753, 3755, 3757, 3761, 3759, 3763, 4088, 4089,
        4090, 4091, 4092
    ]

    snotel_datatypes = [50]

    lbo_requests = {
        'LBO_SITES': {
            'sids': lbo_sites,
            'dids': lbo_datatypes,
            'interval': 'day',
            'period': 'por'
        }
    }

    testing_requests = {
        'test_ff': {
            'sids': testing_sites,
            'dids': testing_datatypes,
            'interval': 'day',
            'period': 'por'
        }
    }

    one_off_requests = {
        'one_off_data': {
            'sids': one_off_sites,
            'dids': one_off_datatypes,
            'interval': 'day',
            'period': 'por'
        }
    }

    prod_requests_v2 = {
        'GAUGE_DATA': {
            'sids': usgs_gages,
            'dids':gage_data_types,
            'interval': 'day',
            'period': 'por'
        },
        'RESERVOIR_DATA': {
            'sids': all_res_data,
            'dids': res_data_types,
            'interval': 'day',
            'period': 'por'
        }
    }

    prod_requests_lc = {
        'LC_RESERVOIR_DATA': {
            'sids': lc_reservoirs,
            'dids': res_data_types,
            'interval': 'day',
            'period': 'por'
        }
    }

    prod_requests_eco = {
        'ECO_RESERVOIR_DATA': {
            'sids': eco_reservoirs,
            'dids': eco_res_data_types,
            'interval': 'day',
            'period': 'por'
        },
        'ECO_GAUGE_DATA': {
            'sids': eco_gages,
            'dids': eco_gage_data_types,
            'interval': 'day',
            'period': 'por'
        }
    }

    snow_requests = {
        'SNOTELS': {
            'sids': snotel_ids,
            'dids': snotel_datatypes,
            'interval': 'day',
            'period': 'por'
        }
    }

    config_json = {
        'prod': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': prod_requests_v2,
            'sftp_push': True
        },
        'prod_rhel': {
            'alt_path': r'/wrg/exec/pub/flat_files',
            'hdb': 'uc',
            'requests': prod_requests_v2,
            'sftp_push': False
        },
        'prod_lc': {
            'alt_path': None,
            'hdb': 'lc',
            'requests': prod_requests_lc,
            'sftp_push': False
        },
        'prod_eco': {
            'alt_path': None,
            'hdb': 'eco',
            'requests': prod_requests_eco,
            'sftp_push': False
        },
        'local': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': prod_requests_v2,
            'sftp_push': False
        },
        'default': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': prod_requests_v2,
            'sftp_push': False
        },
        'testing': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': testing_requests,
            'sftp_push': False
        },
        'one_off': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': one_off_requests,
            'sftp_push': False
        },
        'lbo': {
            'alt_path': r'C:\Users\buriona\Documents',
            'hdb': 'lbo',
            'requests': lbo_requests,
            'sftp_push': False
        },
        'snow': {
            'alt_path': None,
            'hdb': 'uc',
            'requests': snow_requests,
            'sftp_push': False
        }
    }

    with open('ff_config.json', 'w') as fp:
        json.dump(config_json, fp, indent=4, sort_keys=True)

    print('Succesfully created ff_config.json')
