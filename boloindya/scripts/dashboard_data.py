import random
from datetime import datetime, timedelta
from calendar import monthrange
from jarvis.models import DashboardMetrics

"""
To Put weekly data....

metric = 6
weekly_counts = [4732, 4741, 4917, 4812, 15412, 15398, 15491, 15411, 35412, 35567, 35498, 35628, 52378, 52338, 52319, 52489, 68863, 74198, 80112, 98876, 110098, 119057, 128733, 129876, 178976, 262913, 330098, 327284, 309076, 271091, 290765, 289069, 310094, 438763, 574091, 989053, 2794100]

metric = 9
weekly_counts = [4321, 4398, 4498, 4587, 5786, 7813, 9831, 12112, 12498, 13011, 13912, 14231, 16819, 18329, 20022, 18431, 20191, 21781, 23570, 24541, 27917, 29376, 31059, 33369, 49014, 88871, 80157, 94746, 119810, 141056, 151091, 183661, 240094, 338763, 404091, 585053, 2777800]

metric = 0
weekly_counts = [19800, 21980, 28070, 24350, 39801, 51340, 71918, 69721, 85412, 85567, 95498, 107752, 92378, 102338, 192912, 162489, 168863, 104198, 198461, 208876, 210098, 219057, 216590, 229876, 378976, 562913, 930098, 829342, 909076, 971091, 1654745, 1589069, 1810094, 2438763, 2574091, 5878452, 64507432]

metric = 12
weekly_counts = [53956, 68091, 90910, 146643, 154120, 178642, 154910, 154528, 200412, 215567, 245498, 292823, 315490, 355496, 235498, 317516, 415490, 455496, 385998, 447516, 415490, 415496, 685878, 658136, 915490, 1415496, 1885878, 3625136, 2015490, 2415496, 2885878, 2250376, 2415528, 3415473, 3885801, 5069144, 86843819]

metric = 3
weekly_counts = [51987, 59871, 64312, 78170, 91987, 139871, 264310, 272006, 312198, 430541, 784980, 1054461, 1052378, 1552338, 2512109, 3024907, 3052114, 3952031, 4512109, 3928781, 4552114, 7952031, 11512109, 12847390, 11071349, 21647667, 31447813, 30128108, 31320561, 40468010, 50120183, 60102014, 62191452, 60191320, 58013609, 71261291, 91216031]

metric = 13
weekly_counts = [71987, 99871, 94312, 58170, 710198, 703987, 846431, 827200, 931219, 1643054, 1778498, 1805446, 2105237, 2155233, 2551210, 2702490, 3005210, 2995238, 2951221, 3392878, 3555211, 3793901, 4101070, 4284103, 4901389, 4819102, 4521040, 5501424, 5910130, 5510042, 4910431, 6301090, 6019032, 5301024, 6793351, 8021458, 9113218]

c = 0
metric = 13
weekly_counts = [71987, 99871, 94312, 58170, 710198, 703987, 846431, 827200, 931219, 1643054, 1778498, 1805446, 2105237, 2155233, 2551210, 2702490, 3005210, 2995238, 2951221, 3392878, 3555211, 3793901, 4101070, 4284103, 4901389, 4819102, 4521040, 5501424, 5910130, 5510042, 4910431, 6301090, 6019032, 5301024, 6793351, 8021458, 9113218]

for each in DashboardMetrics.objects.filter(metrics__exact=metric, date__gte = '2019-10-07').order_by('date'):
    if each.week_no in [49, 63]: ##Skip these week and updte them manually later... remove if not required
        each.count = 0
    else:
        each.count = weekly_counts[c]
        c += 1
    each.save()

"""
def run():
    data = [{
        'data' : {
            "2019-05" : 2235,
            "2019-06" : 5823,
            "2019-07" : 11142,
            "2019-08" : 22687,
            "2019-09" : 44014,
            
            "2019-10" : 94200,
            "2019-11" : 232780,
            "2019-12" : 374229,
            "2020-01" : 550117,
            "2020-02" : 680398,
            "2020-03" : 875621,
            "2020-04" : 2701329,
            "2020-05" : 5123981,
            "2020-06" : 12701400,
            "2020-07" : 64507432,
        },
        'metrics' : '0',
        'slab' : None
    },
    {
        'data' : {
            "2019-05" : 543,
            "2019-06" : 1690,
            "2019-07" : 2023,
            "2019-08" : 2908,
            "2019-09" : 3296,
            
            "2019-10" : 4800,
            "2019-11" : 15430,
            "2019-12" : 35530,
            "2020-01" : 52380,
            "2020-02" : 80510,
            "2020-03" : 121940,
            "2020-04" : 274817,
            "2020-05" : 290000,
            "2020-06" : 578000,
            "2020-07" : 2794100,
        },
        'metrics' : '6',
        'slab' : None
    },
    {
        'data' : {
            "2019-05" : 3900,
            "2019-06" : 4234,
            "2019-07" : 5220,
            "2019-08" : 7923,
            "2019-09" : 8123,
            
            "2019-10" : 15006,
            "2019-11" : 42891,
            "2019-12" : 95152,
            "2020-01" : 137089,
            "2020-02" : 191519,
            "2020-03" : 227503,
            "2020-04" : 401381,
            "2020-05" : 480000,
            "2020-06" : 730000,
            "2020-07" : 3154400,
        },
        'metrics' : '8',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 113,
            "2019-06" : 560,
            "2019-07" : 1309,
            "2019-08" : 2168,
            "2019-09" : 3563,
            
            "2019-10" : 4451,
            "2019-11" : 8885,
            "2019-12" : 13413,
            "2020-01" : 18400,
            "2020-02" : 22520,
            "2020-03" : 30430,
            "2020-04" : 78197,
            "2020-05" : 148904,
            "2020-06" : 392000,
            "2020-07" : 2777800,
        },
        'metrics' : '9',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 1013,
            "2019-06" : 3648,
            "2019-07" : 8485,
            "2019-08" : 21049,
            "2019-09" : 43913,
            
            "2019-10" : 359600,
            "2019-11" : 639200,
            "2019-12" : 954300,
            "2020-01" : 1224000,
            "2020-02" : 1704500,
            "2020-03" : 2175000,
            "2020-04" : 7842000,
            "2020-05" : 9567240,
            "2020-06" : 14785946,
            "2020-07" : 86843819,
        },
        'metrics' : '12',
        'slab' : None
    }, 

    {
        'data' : {
            "2019-05" : 1492,
            "2019-06" : 35536,
            "2019-07" : 52909,
            "2019-08" : 100309,
            "2019-09" : 209147,
            "2019-10" : 254340,
            "2019-11" : 768174,
            "2019-12" : 2582180,
            "2020-01" : 8141732,
            "2020-02" : 15445035,
            "2020-03" : 36863644,
            "2020-04" : 128853393,
            "2020-05" : 297703296,
            "2020-06" : 1160907960,
            "2020-07" : 7160324952,
        },
        'metrics' : '3',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 192,
            "2019-06" : 30548,
            "2019-07" : 42138,
            "2019-08" : 120113,
            "2019-09" : 219341,
            "2019-10" : 292020,
            "2019-11" : 838008,
            "2019-12" : 1908568,
            "2020-01" : 7206533,
            "2020-02" : 13199721,
            "2020-03" : 20226845,
            "2020-04" : 116427280,
            "2020-05" : 323323201,
            "2020-06" : 988168920,
            "2020-07" : 6024994149,
        },
        'metrics' : '13',
        'slab' : None
    }, 

    # {
    #     'data' : {
    #         "2019-05" : 199053,
    #         "2019-06" : 404341,
    #         "2019-07" : 902931,
    #         "2019-08" : 2309761,
    #         "2019-09" : 4406861,
    #         "2019-10" : 9509199,
    #         "2019-11" : 17849819,
    #         "2019-12" : 33221893,
    #         "2020-01" : 66031091,
    #         "2020-02" : 109832011,
    #         "2020-03" : 160147981,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '1',
    #     'slab' : None
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 11126,
    #         "2019-06" : 38962,
    #         "2019-07" : 160535,
    #         "2019-08" : 320883,
    #         "2019-09" : 650863,
    #         "2019-10" : 1825940,
    #         "2019-11" : 5345837,
    #         "2019-12" : 9651937,
    #         "2020-01" : 15809341,
    #         "2020-02" : 21909871,
    #         "2020-03" : 39811098,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '2',
    #     'slab' : '3'
    # },
    # {
    #     'data' : {
    #         "2019-05" : 2987,
    #         "2019-06" : 36981,
    #         "2019-07" : 67654,
    #         "2019-08" : 191009,
    #         "2019-09" : 289014,
    #         "2019-10" : 499192,
    #         "2019-11" : 783018,
    #         "2019-12" : 1001903,
    #         "2020-01" : 1498013,
    #         "2020-02" : 2709812,
    #         "2020-03" : 4908129,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '2',
    #     'slab' : '4'
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 1492,
    #         "2019-06" : 35536,
    #         "2019-07" : 52909,
    #         "2019-08" : 100309,
    #         "2019-09" : 209147,
    #         "2019-10" : 315017,
    #         "2019-11" : 502194,
    #         "2019-12" : 721031,
    #         "2020-01" : 909123,
    #         "2020-02" : 1698190,
    #         "2020-03" : 2709109,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '2',
    #     'slab' : '5'
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 1492,
    #         "2019-06" : 35536,
    #         "2019-07" : 52909,
    #         "2019-08" : 100309,
    #         "2019-09" : 209147,
    #         "2019-10" : 315017,
    #         "2019-11" : 502194,
    #         "2019-12" : 721031,
    #         "2020-01" : 1309139,
    #         "2020-02" : 2328091,
    #         "2020-03" : 4197190,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '3',
    #     'slab' : None
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 11,
    #         "2019-06" : 25,
    #         "2019-07" : 62,
    #         "2019-08" : 102,
    #         "2019-09" : 420,
    #         "2019-10" : 963,
    #         "2019-11" : 2196,
    #         "2019-12" : 3551,
    #         "2020-01" : 12383,
    #         "2020-02" : 15858,
    #         "2020-03" : 27296,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '4',
    #     'slab' : '0'
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 32,
    #         "2019-06" : 108,
    #         "2019-07" : 244,
    #         "2019-08" : 527,
    #         "2019-09" : 986,
    #         "2019-10" : 2169,
    #         "2019-11" : 4453,
    #         "2019-12" : 9758,
    #         "2020-01" : 13211,
    #         "2020-02" : 16789,
    #         "2020-03" : 19871,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '4',
    #     'slab' : '1'
    # }, 
    # {
    #     'data' : {
    #         "2019-05" : 16,
    #         "2019-06" : 47,
    #         "2019-07" : 154,
    #         "2019-08" : 356,
    #         "2019-09" : 710,
    #         "2019-10" : 1319,
    #         "2019-11" : 2236,
    #         "2019-12" : 104,
    #         "2020-01" : 219,
    #         "2020-02" : 451,
    #         "2020-03" : 743,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '4',
    #     'slab' : '2'
    # },
    # {
    #     'data' : {
    #         "2019-05" : 551,
    #         "2019-06" : 1231,
    #         "2019-07" : 2573,
    #         "2019-08" : 5785,
    #         "2019-09" : 9616,
    #         "2019-10" : 19054,
    #         "2019-11" : 30346,
    #         "2019-12" : 45635,
    #         "2020-01" : 54943,
    #         "2020-02" : 68971,
    #         "2020-03" : 99321,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '5',
    #     'slab' : '6'
    # },
    # {
    #     'data' : {
    #         "2019-05" : 0,
    #         "2019-06" : 0,
    #         "2019-07" : 0,
    #         "2019-08" : 0,
    #         "2019-09" : 0,
    #         "2019-10" : 1497,
    #         "2019-11" : 4139,
    #         "2019-12" : 8281,
    #         "2020-01" : 20987,
    #         "2020-02" : 36789,
    #         "2020-03" : 67891,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '5',
    #     'slab' : '7'
    # },
    # {
    #     'data' : {
    #         "2019-05" : 551,
    #         "2019-06" : 1231,
    #         "2019-07" : 2573,
    #         "2019-08" : 5785,
    #         "2019-09" : 9616,
    #         "2019-10" : 20551,
    #         "2019-11" : 34485,
    #         "2019-12" : 53916,
    #         "2020-01" : 75930,
    #         "2020-02" : 105760,
    #         "2020-03" : 167212,
    #         "2020-04" : ,
    #         "2020-05" : ,
    #         "2020-06" : ,
    #         "2020-07" : ,
    #     },
    #     'metrics' : '5',
    #     'slab' : '8'
    # },
    ]

    percent_dict = { 1 : 0.7,  2 : 0.8,  3 : 0.8,  4 : 1.1,  5 : 1.5,  6 : 1.7,  7 : 2.1,  8 : 2.4,  9 : 2.6,  10 : 2.7,  \
        11 : 2.9,  12 : 3.1,  13 : 3.2,  14 : 3.4,  15 : 3.5,  16 : 3.6,  17 : 3.7,  18 : 3.8,  19 : 3.9,  20 : 4.1,  \
        21 : 4.3,  22 : 4.4,  23 : 4.5,  24 : 4.6,  25 : 4.7,  26 : 4.9,  27 : 5.1,  28 : 5.2,  29 : 5.3,  30 : 5.4 }
    
    percent_dict_31 = { 1 : 0.3, 2 : 0.4, 3 : 0.7, 4 : 0.9, 5 : 1.1, 6 : 1.5, 7 : 1.7, 8 : 2.1, 9 : 2.4, 10 : 2.6, \
        11 : 2.7, 12 : 2.9, 13 : 3.1, 14 : 3.2, 15 : 3.4, 16 : 3.5, 17 : 3.6, 18 : 3.7, 19 : 3.8, 20 : 3.9, 21 : 4.1, \
        22 : 4.3, 23 : 4.4, 24 : 4.5, 25 : 4.6, 26 : 4.7, 27 : 4.9, 28 : 5.1, 29 : 5.2, 30 : 5.3, 31 : 5.4}
    
    for each_dict in data:
        metrics = each_dict['metrics']
        slab = each_dict['slab']
        data = each_dict['data']
        # last_value = 1
        for each_rec in data:
            rec_count = data[each_rec]
            no_of_days = monthrange(int(each_rec.split('-')[0]), int(each_rec.split('-')[1]))[1]
            if each_rec == "2020-07":
                no_of_days = 6
            final_dict = {}
            for i in range(1, no_of_days + 1):
                temp_percent = percent_dict_31
                if no_of_days == 30:
                    temp_percent = percent_dict
                
                dev = ((rec_count * temp_percent[i]) / 100) # rec_count
                final_dict[i] = int(dev)

            rem_val = rec_count - sum(final_dict.values()) 
            try:
                rem_f = rem_val - (rem_val / rec_count) * rec_count
            except Exception as e:
                print e
                rem_f = 0

            for i in final_dict:                    
                final_dict[i] = final_dict[i] + (rem_val / no_of_days)

            ri = random.randint(1, no_of_days)
            final_dict[ri] = final_dict[ri] + rem_f
            
            if (rec_count - sum(final_dict.values())) != 0:
                ri = random.randint(1, no_of_days)
                final_dict[ri] = final_dict[ri] + (rec_count - sum(final_dict.values()))
            
            final_count = 0
            last_week_no = None
            for each_data in final_dict:
                final_count += final_dict[each_data]
                month_date = datetime.strptime(each_rec + '-' + str(each_data), '%Y-%m-%d')
                week_no = month_date.isocalendar()[1]
                if month_date.year == 2020:
                    week_no += 53
                if month_date.year == 2019 and week_no == 1:
                    week_no = 53

                if not last_week_no:
                    last_week_no = week_no
                
                elif last_week_no != week_no:
                    save_obj, created = DashboardMetrics.objects.get_or_create(metrics = metrics, metrics_slab = slab, date = month_date,\
                            week_no = week_no)
                    if created:
                        # final_count = final_dict[each_data]
                        if final_dict[each_data] < 0:
                            print metrics, slab, month_date, week_no, final_dict[each_data]
                            print '============================================='
                            final_count = 0
                        # print 'Created....'
                        save_obj.count = final_count
                        save_obj.save()
                    final_count = 0
                    last_week_no = week_no

