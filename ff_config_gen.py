# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 08:42:01 2019

@author: buriona
"""
#This is simply a helper file that creates the json config, not neccesary but nice


# testing config (changes often)
testing_sdis = [
    7899, 7803, 9365, 9275, 9095, 9305, 9065, 9185, 9605
]
testing_sites = [
    
]

testing_datatypes = [
    
]

testing_requests = {
    'water_quality': {
        'sdis': testing_sdis,
        'sids': testing_sites,
        'dids': testing_datatypes,
        # 'mode': 'accounting',
        'interval': 'day',
        'period': 'POR'
    }
}

# alb accounting config

alb_accounting_sites = [
    4630, 3371, 4631, 4636, 4629, 3350, 4632, 4634, 4635, 3356, 3389, 
    3373, 3455, 3383, 3349, 3352, 4637, 4638, 3399, 3373, 2686, 2685, 
    2729, 1095, 2696
]

alb_accounting_datatypes = [
    17, 1158, 2742, 19, 42
]

alb_accounting_sdis = [
    20148, 19907
]

alb_accounting_requests = {
    'alb_accounting': {
        'sdis': alb_accounting_sdis,
        'sids': alb_accounting_sites,
        'dids': alb_accounting_datatypes,
        'mode': 'accounting',
        'interval': 'day',
        'period': 'por'
    }
}

# UC configuration 

crsp_reservoirs = [
    912, 913, 914, 915, 1119, 917, 916, 958, 914, 920, 933, 919,                #UCR
    934, 3083, 935                                                              #susan
]

pao_reservoirs = [                                                              #gary henrie
    957, 959, 947, 941, 942, 940, 938, 946, 925, 3608, 3607, 3609,
    964, 953, 936, 954, 944, 949, 963, 952, 962, 928, 930,
    960, 927, 931, 956, 932, 3866
]

aao_reservoirs_corps = [
    2730, 2729, 2696, 2744
]

aao_reservoirs_bor = [
    1094, 2686, 2685, 943, 937, 2684, 2688, 2687
]

aao_reservoirs = aao_reservoirs_bor + aao_reservoirs_corps

wcao_reservoirs = [948, 945, 939, 955, 951]

misc_reservoirs = [
    1998, 1999, 2000, 2002, 2003, 2005, 3606, 924, 961
]

uc_res_data = list(
    set(crsp_reservoirs + pao_reservoirs + aao_reservoirs + misc_reservoirs + wcao_reservoirs)
)

uc_res_datatypes = [
    15, 17, 25, 29, 30, 31, 32, 33, 34, 39, 40, 42, 43, 46, 47, 49,
    123, 124, 1197, 1198, 1501, 89
]
    
uc_rise_sites = list(
    set(uc_res_data) - set(misc_reservoirs) - set(aao_reservoirs_corps)
)

uc_gages = [
    1536,1537,1539,1541,1542,3590,1544,1545,3081,3591,1548,1549,1550,1551,
    1552,1553,3084,1555,3085,1045,1558,1559,1048,1049,1050,1051,1560,1561,
    1562,1563,1565,1568,1065,1066,1067,3629,4662,4663,1095,1113,1115,1116,
    3679,3680,1633,3681,3684,1644,1645,1652,1653,1654,1655,1657,1658,1659,
    1662,2690,2691,2692,1670,1671,1672,1673,1674,2698,4242,2707,4243,2713,
    2717,2718,2720,2721,2722,2723,2726,2728,1705,3240,1708,1709,1710,1711,
    1712,1713,1714,1715,1716,1717,1718,1719,1720,1721,1722,1723,2740,2741,
    2742,2743,1728,1729,1730,1731,1732,1733,1734,1735,1736,1737,1738,716,
    717,718,719,720,721,722,723,726,729,731,733,734,735,736,737,738,739,
    740,741,742,743,756,757,758,3829,3830,764,765,766,767,768,770,771,772,
    773,774,775,776,777,779,781,783,784,786,788,789,790,791,1300,1301,1302,
    1303,1304,799,801,802,3876,3877,3878,3894,3896,827,828,3904,833,
    834,3905,3906,837,838,3907,840,3908,843,3909,3910,846,3911,859,900,
    907,908,3498,3502,3503,3504,3505,451,3528,2738,3028,3029,
    1505,4065,1509,1510,3764,1512,1513,1514,1515,1516,1517,1519,1526,1527,
    1528,1530,3068,1534
]

uc_gages = list(set(uc_gages))
uc_gage_datatypes = [19, 20, 31, 1191, 1211]

uc_requests_test = {
    'reservoir_data': {
        'sids': uc_res_data[0:5],
        'dids': uc_res_datatypes,
        'interval': 'day',
        'period': 365
    },
    # 'gage_data': {
    #     'sids': uc_gages,
    #     'dids': uc_gage_datatypes,
    #     'interval': 'day',
    #     'period': 365
    # }
}

uc_requests_daily = {
    'reservoir_data': {
        'sids': uc_res_data,
        'dids': uc_res_datatypes,
        'interval': 'day',
        'period': 365
    },
    'gage_data': {
        'sids': uc_gages,
        'dids': uc_gage_datatypes,
        'interval': 'day',
        'period': 365
    }
}

uc_requests_weekly = {
    'reservoir_data': {
        'sids': uc_res_data,
        'dids': uc_res_datatypes,
        'interval': 'day',
        'period': 1830
    },
    'gage_data': {
        'sids': uc_gages,
        'dids': uc_gage_datatypes,
        'interval': 'day',
        'period': 1830
    }
}

uc_requests_monthly = {
    'reservoir_data': {
        'sids': uc_res_data,
        'dids': uc_res_datatypes,
        'interval': 'day',
        'period': 'por'
    },
    'gage_data': {
        'sids': uc_gages,
        'dids': uc_gage_datatypes,
        'interval': 'day',
        'period': 'por'
    }
}

uc_rise_rsync = '''rsync -avzh -e "ssh -i /home/app_user/.ssh/nep_rise_rsync" --remove-source-files --include '*.json' --exclude '*' /wrg/hdb/apps/python/ff_gen/rise/uchdb2/ svc-dro-uchdb2@140.215.112.124:/home/svc-dro-uchdb2/DATA'''

# LC configuration

lc_gages = [
    1097, 1018, 1061, 1060, 751, 1016, 3873, 3432, 3434, 1015, 
    3433, 1008, 1104
]

lc_gage_datatypes = [19, 66, 2367]

lc_reservoirs = [921, 922, 923]

lc_res_datatypes = [43, 17, 49, 121, 42]

lc_sites = lc_gages + lc_reservoirs

lc_datatypes = lc_gage_datatypes + lc_res_datatypes

lc_rise_sites = [
    751, 921, 922, 1018, 923, 1008, 1015, 1016, 1018, 1060, 1061, 3432, 
    3433, 3434
]

lc_requests_test = {
    'reservoir_data': {
        'sids': lc_reservoirs,
        'dids': lc_res_datatypes,
        'interval': 'day',
        'period': 'por'
    },
    'gage_data': {
        'sids': lc_gages,
        'dids': lc_gage_datatypes,
        'interval': 'day',
        'period': 'por'
    },
}

lc_requests_daily = {
    'reservoir_data': {
        'sids': lc_reservoirs,
        'dids': lc_res_datatypes,
        'interval': 'day',
        'period': 365
    },
    'gage_data': {
        'sids': lc_gages,
        'dids': lc_gage_datatypes,
        'interval': 'day',
        'period': 365
    },
}

lc_requests_weekly = {
    'reservoir_data': {
        'sids': lc_reservoirs,
        'dids': lc_res_datatypes,
        'interval': 'day',
        'period': 1830
    },
    'gage_data': {
        'sids': lc_gages,
        'dids': lc_gage_datatypes,
        'interval': 'day',
        'period': 1830
    }
}

lc_requests_monthly = {
    'reservoir_data': {
        'sids': lc_reservoirs,
        'dids': lc_res_datatypes,
        'interval': 'day',
        'period': 'por'
    },
    'gage_data': {
        'sids': lc_gages,
        'dids': lc_gage_datatypes,
        'interval': 'day',
        'period': 'por'
    }
}

lc_rise_rsync = '''rsync -avzh -e "ssh -i /home/app_user/.ssh/nep_rise_rsync" --remove-source-files --include '*.json' --exclude '*' /wrg/hdb/apps/python/ff_gen/rise/lchdb2/ svc-dro-lchdb2@140.215.112.124:/home/svc-dro-lchdb2/DATA'''

# PN configuration

pn_sites = ['and', 'jck', 'sco', 'mck']
pn_datatypes = ['af','fb','qu','qd']

pn_requests = {
    'pn_sites': {
        'sids': pn_sites,
        'dids': pn_datatypes,
        'interval': 'day',
        'period': 'por'
    }
}

# GP configuration

gp_sites = [
    'agr', 'alcr', 'ancr', 'arne', 'audl', 'bbne', 'bbr', 'bbrsfd', 'bfr',
    'bhr', 'bhsx', 'blr', 'boyr', 'cane', 'carterco', 'ccdt', 'ccks',
    'ccr', 'cfrsat', 'dane', 'dfr', 'eapr', 'flaresco', 'frr', 'gdwy',
    'gibr', 'glaresco', 'gler', 'graresco', 'greresco', 'guwy', 'htoothr',
    'jamr', 'keyr', 'ksks', 'kwks', 'lane', 'ler', 'lerm', 'lfrm', 'limr',
    'lmne', 'ltr', 'lvks', 'marysr', 'mcdh', 'mrne', 'mtelfbco', 'nasty',
    'nelr', 'olydamco', 'patr', 'pbr', 'pinresco', 'pshr', 'ptr', 'puer',
    'rueresco', 'semr', 'sharesco', 'sher', 'shr', 'srdm', 'swtr', 'turq',
    'twiresco', 'waks', 'wbks', 'wcne', 'wcr', 'wilresco'
]

gp_datatypes = ['qdx', 'af', 'fb', 'qd', 'qj', 'qrd', 'in', 'qehd', 'qsd']

gp_requests = {
    'gp_sites': {
        'sids': gp_sites,
        'dids': gp_datatypes,
        'interval': 'day',
        'period': 'por'
    }
}

# ECO config 

eco_res_data = [
    100001, 100065, 100002, 100081, 100010, 100089, 100156, 100120, 100091,
    100017, 100100, 100257, 100003, 100038, 100031, 100113, 100032, 100049,
    100163, 100275, 100053, 100118
]

eco_gages = [
    100011, 100093, 100114, 100055, 100090, 100064, 100097, 100051,
    100078, 100056, 100015, 101778, 101779, 101782, 100385, 100409,
    100037, 100073, 100124, 100083, 100094, 101780, 100054, 100111,
    101769, 100116, 100155, 100013, 100020, 101774, 100033, 100099, 100026,
    100095, 100062, 100101, 100379, 101804, 100869, 100870, 100871,
    100872, 101781, 100279, 100024, 100050, 100061, 100121, 100129,
    100040, 101772, 100027, 100021, 101783, 100662, 100956, 100664, 101784,
    101785, 101761, 100102, 100082, 100009, 100057, 100067, 100123, 101786,
    100086, 100276, 100022, 100087, 100039, 100079, 100098, 100042,
    100075, 100868, 100669, 100653, 100654, 100671, 100110, 100047, 100052,
    100070, 100077, 100069, 101770, 100085, 101787, 100673, 100672,
    100128, 100109, 100874, 100139, 100646
]

eco_res_datatypes = [17, 49]

eco_gage_datatypes = [19]

eco_rise_sites = None
eco_rise_rsync = None

eco_requests_daily = {
    'reservoir_data': {
        'sids': eco_res_data,
        'dids': eco_res_datatypes,
        'interval': 'day',
        'period': 365
    },
    'gage_data': {
        'sids': eco_gages,
        'dids': eco_gage_datatypes,
        'interval': 'day',
        'period': 365
    }
}

eco_requests_weekly = {
    'reservoir_data': {
        'sids': eco_res_data,
        'dids': eco_res_datatypes,
        'interval': 'day',
        'period': 1830
    },
    'gage_data': {
        'sids': eco_gages,
        'dids': eco_gage_datatypes,
        'interval': 'day',
        'period': 1830
    }
}

eco_requests_monthly = {
    'reservoir_data': {
        'sids': eco_res_data,
        'dids': eco_res_datatypes,
        'interval': 'day',
        'period': 'por'
    },
    'gage_data': {
        'sids': eco_gages,
        'dids': eco_gage_datatypes,
        'interval': 'day',
        'period': 'por'
    }
}

config_json = {
    'default': {
        'alt_path': None,
        'hdb': 'uc',
        'requests': uc_requests_daily,
        'rise_sites': None,
        'sftp_push': None
    },
    'test': {
        'alt_path': None,
        'hdb': 'yao',
        'requests': testing_requests,
        'rise_sites': None,
        'sftp_push': None
    },
    'uc_test': {
        'alt_path': None,
        'hdb': 'uc',
        'requests': uc_requests_test,
        'rise_sites': uc_rise_sites,
        'sftp_push': uc_rise_rsync
    },
    'lc_test': {
        'alt_path': None,
        'hdb': 'lc',
        'requests': lc_requests_test,
        'rise_sites': lc_rise_sites,
        'sftp_push': None
    },
    'uc_rhel_daily': {
        'alt_path': '/wrg/exec/pub/flat_files',
        'hdb': 'uc',
        'requests': uc_requests_daily,
        'rise_sites': uc_rise_sites,
        'sftp_push': uc_rise_rsync
    },
    'uc_rhel_weekly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'uc',
        'requests': uc_requests_weekly,
        'rise_sites': uc_rise_sites,
        'sftp_push': uc_rise_rsync
    },
    'uc_rhel_monthly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'uc',
        'requests': uc_requests_monthly,
        'rise_sites': uc_rise_sites,
        'sftp_push': uc_rise_rsync
    },
    'lc_rhel_daily': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'lc',
        'requests': lc_requests_daily,
        'rise_sites': lc_rise_sites,
        'sftp_push': lc_rise_rsync
    },
    'lc_rhel_weekly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'lc',
        'requests': lc_requests_weekly,
        'rise_sites': lc_rise_sites,
        'sftp_push': lc_rise_rsync
    },
    'lc_rhel_monthly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'lc',
        'requests': lc_requests_monthly,
        'rise_sites': lc_rise_sites,
        'sftp_push': lc_rise_rsync
    },
    'alb_accounting_rhel': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'uc',
        'requests': alb_accounting_requests,
        'rise_sites': None,
        'sftp_push': None
    },
    'pn_rhel_daily': {
        'alt_path': '/wrg/exec/pub/flat_files',
        'hdb': 'pn',
        'requests': pn_requests,
        'rise_sites': None,
        'sftp_push': False
    },
    'gp_rhel_daily': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'gp',
        'requests': gp_requests,
        'rise_sites': None,
        'sftp_push': False
    },
    'eco_rhel_daily': {
        'alt_path': '/wrg/exec/pub/flat_files',
        'hdb': 'eco',
        'requests': eco_requests_daily,
        'rise_sites': eco_rise_sites,
        'sftp_push': eco_rise_rsync
    },
    'eco_rhel_weekly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'eco',
        'requests': eco_requests_weekly,
        'rise_sites': eco_rise_sites,
        'sftp_push': eco_rise_rsync
    },
    'eco_rhel_monthly': {
        'alt_path': r'/wrg/exec/pub/flat_files',
        'hdb': 'eco',
        'requests': eco_requests_monthly,
        'rise_sites': eco_rise_sites,
        'sftp_push': eco_rise_rsync
    },
}

if __name__ == '__main__':
    
    import json
    
    with open('ff_config.json', 'w') as fp:
        json.dump(config_json, fp, indent=4, sort_keys=False)

    print('Succesfully created ff_config.json')
