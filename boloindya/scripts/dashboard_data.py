import random
from datetime import datetime
from calendar import monthrange
from jarvis.models import DashboardMetrics

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
            "2020-01" : 710198,
            "2020-02" : 998144,
            "2020-03" : 1409132
        },
        'metrics' : '0',
        'slab' : None
    },
    {
        'data' : {
            "2019-05" : 199053,
            "2019-06" : 404341,
            "2019-07" : 902931,
            "2019-08" : 2309761,
            "2019-09" : 4406861,
            "2019-10" : 9509199,
            "2019-11" : 17849819,
            "2019-12" : 33221893,
            "2020-01" : 66031091,
            "2020-02" : 109832011,
            "2020-03" : 160147981,
        },
        'metrics' : '1',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 11126,
            "2019-06" : 38962,
            "2019-07" : 160535,
            "2019-08" : 320883,
            "2019-09" : 650863,
            "2019-10" : 1825940,
            "2019-11" : 5345837,
            "2019-12" : 9651937,
            "2020-01" : 15809341,
            "2020-02" : 21909871,
            "2020-03" : 39811098,
        },
        'metrics' : '2',
        'slab' : '3'
    },
    {
        'data' : {
            "2019-05" : 2987,
            "2019-06" : 36981,
            "2019-07" : 67654,
            "2019-08" : 191009,
            "2019-09" : 289014,
            "2019-10" : 499192,
            "2019-11" : 783018,
            "2019-12" : 1001903,
            "2020-01" : 1498013,
            "2020-02" : 2709812,
            "2020-03" : 4908129,
        },
        'metrics' : '2',
        'slab' : '4'
    }, 
    {
        'data' : {
            "2019-05" : 1492,
            "2019-06" : 35536,
            "2019-07" : 52909,
            "2019-08" : 100309,
            "2019-09" : 209147,
            "2019-10" : 315017,
            "2019-11" : 502194,
            "2019-12" : 721031,
            "2020-01" : 909123,
            "2020-02" : 1698190,
            "2020-03" : 2709109,
        },
        'metrics' : '2',
        'slab' : '5'
    }, 
    {
        'data' : {
            "2019-05" : 1492,
            "2019-06" : 35536,
            "2019-07" : 52909,
            "2019-08" : 100309,
            "2019-09" : 209147,
            "2019-10" : 315017,
            "2019-11" : 502194,
            "2019-12" : 721031,
            "2020-01" : 1309139,
            "2020-02" : 2328091,
            "2020-03" : 4197190,
        },
        'metrics' : '3',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 11,
            "2019-06" : 25,
            "2019-07" : 62,
            "2019-08" : 102,
            "2019-09" : 420,
            "2019-10" : 963,
            "2019-11" : 2196,
            "2019-12" : 3551,
            "2020-01" : 12383,
            "2020-02" : 15858,
            "2020-03" : 27296,
        },
        'metrics' : '4',
        'slab' : '0'
    }, 
    {
        'data' : {
            "2019-05" : 32,
            "2019-06" : 108,
            "2019-07" : 244,
            "2019-08" : 527,
            "2019-09" : 986,
            "2019-10" : 2169,
            "2019-11" : 4453,
            "2019-12" : 9758,
            "2020-01" : 13211,
            "2020-02" : 16789,
            "2020-03" : 19871,
        },
        'metrics' : '4',
        'slab' : '1'
    }, 
    {
        'data' : {
            "2019-05" : 16,
            "2019-06" : 47,
            "2019-07" : 154,
            "2019-08" : 356,
            "2019-09" : 710,
            "2019-10" : 1319,
            "2019-11" : 2236,
            "2019-12" : 104,
            "2020-01" : 219,
            "2020-02" : 451,
            "2020-03" : 743,
        },
        'metrics' : '4',
        'slab' : '2'
    },
    {
        'data' : {
            "2019-05" : 551,
            "2019-06" : 1231,
            "2019-07" : 2573,
            "2019-08" : 5785,
            "2019-09" : 9616,
            "2019-10" : 19054,
            "2019-11" : 30346,
            "2019-12" : 45635,
            "2020-01" : 54943,
            "2020-02" : 68971,
            "2020-03" : 99321,
        },
        'metrics' : '5',
        'slab' : '6'
    },
    {
        'data' : {
            "2019-05" : 0,
            "2019-06" : 0,
            "2019-07" : 0,
            "2019-08" : 0,
            "2019-09" : 0,
            "2019-10" : 1497,
            "2019-11" : 4139,
            "2019-12" : 8281,
            "2020-01" : 20987,
            "2020-02" : 36789,
            "2020-03" : 67891,
        },
        'metrics' : '5',
        'slab' : '7'
    },
    {
        'data' : {
            "2019-05" : 551,
            "2019-06" : 1231,
            "2019-07" : 2573,
            "2019-08" : 5785,
            "2019-09" : 9616,
            "2019-10" : 20551,
            "2019-11" : 34485,
            "2019-12" : 53916,
            "2020-01" : 75930,
            "2020-02" : 105760,
            "2020-03" : 167212,
        },
        'metrics' : '5',
        'slab' : '8'
    },
    {
        'data' : {
            "2019-05" : 543,
            "2019-06" : 1690,
            "2019-07" : 4023,
            "2019-08" : 9608,
            "2019-09" : 18896,
            "2019-10" : 39006,
            "2019-11" : 72891,
            "2019-12" : 125152,
            "2020-01" : 200981,
            "2020-02" : 298761,
            "2020-03" : 389751,
        },
        'metrics' : '6',
        'slab' : None
    },
    {
        'data' : {
            "2019-05" : 113421,
            "2019-06" : 364822,
            "2019-07" : 848519,
            "2019-08" : 2104913,
            "2019-09" : 4391326,
            "2019-10" : 9312593,
            "2019-11" : 17632902,
            "2019-12" : 33019024,
            "2020-01" : 53243913,
            "2020-02" : 93104102,
            "2020-03" : 140019019,
        },
        'metrics' : '7',
        'slab' : None
    }, 
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
            final_dict = {}
            for i in range(1, no_of_days + 1):
                temp_percent = percent_dict_31
                if no_of_days == 30:
                    temp_percent = percent_dict
                # dev = last_value + ((last_value * temp_percent[i]) / 100) # rec_count
                # last_value = int(dev)
                # final_dict[i] = int(dev)
                
                dev = ((rec_count * temp_percent[i]) / 100) # rec_count
                final_dict[i] = int(dev)

                # temp_count = rec_count / no_of_days
                # dev = temp_count - ((temp_count * round(random.uniform(0.2, 0.8), 1) ) / 100)
                # final_dict[i] = int(dev)

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
            
            for each_data in final_dict:
                month_date = datetime.strptime(each_rec + '-' + str(each_data), '%Y-%m-%d')
                week_no = month_date.isocalendar()[1]
                if month_date.year == 2020:
                    week_no += 52
                if month_date.year == 2019 and week_no == 1:
                    week_no = 52

                save_obj, created = DashboardMetrics.objects.get_or_create(metrics = metrics, metrics_slab = slab, date = month_date,\
                        week_no = week_no)
                if created:
                    final_count = final_dict[each_data]
                    if final_dict[each_data] < 0:
                        print metrics, slab, month_date, week_no, final_dict[each_data]
                        print '============================================='
                        final_count = 0
                    # print 'Created....'
                    save_obj.count = final_count
                    save_obj.save()

