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

    all_res_data = list(
        set(crsp_reservoirs + pao_reservoirs + aao_reservoirs + misc_reservoirs)
    )

    usgs_gages = [
        729, 1067, 776, 757, 3684, 1633, 802, 774, 3029, 3028, 716,                 #Rick
        777, 739, 733, 767, 786, 783, 735, 738, 736, 734,                           #Upper Green
        743, 1066, 731, 789, 787, 900,                                              #Heather?
        907, 772, 799, 773, 742, 771, 859, 451,                                     #Susan?
        1113, 1548, 1550, 1555, 1559, 1552, 1562, 1514, 1513, 1095, 1534,           #Albuquerque area office
        1116, 1065, 1542, 1553, 1560, 2722, 2741, 2723                              #Albuquerque area office
    ]

    usgs_gages = list(set(usgs_gages))

    res_data_types = [
        49, 25, 29, 30, 49, 39, 40, 43, 46, 17, 42, 33, 34, 15, 1197, 1198, 47,
        123, 124, 1501
    ]

    gage_data_types = [19, 20]

    lbo_sites = [60000, 60001, 60002, 60003, 60004, 60005, 60006, 60007,
                 60008, 60009, 60010, 60011, 60012, 60013, 60014, 60015,
                 60016, 60017, 60018, 60019, 60020, 60021, 60022, 60023,
                 60024, 60025, 60026, 60027, 60028, 60029, 60030, 60031,
                 60032, 60033, 60034, 60035, 60036, 60037]

    lbo_datatypes = [66, 65, 120, 19, 20, 18, 65]

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
            'dids': res_data_types,
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
        }
    }

    with open('ff_config.json', 'w') as fp:
        json.dump(config_json, fp, indent=4, sort_keys=True)

    print('Succesfully created ff_config.json')
