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
        },
        'metrics' : '0',
        'slab' : None
    },
    {
        'data' : {
            "2019-05": 199053,
            "2019-06": 1214372,
            "2019-07": 21316142,
            "2019-08": 69117687,
            "2019-09": 180924014,
            "2019-10": 421442094,
            "2019-11": 1363244139,
            "2019-12": 3708024037
        },
        'metrics' : '1',
        'slab' : None
    }, 
    {
        'data' : {
            "2019-05" : 11126,
            "2019-06" : 38962,
            "2019-07" : 1825721,
            "2019-08" : 5939259,
            "2019-09" : 15804724,
            "2019-10" : 37056677,
            "2019-11" : 131378915,
            "2019-12" : 325859985,
        },
        'metrics' : '2',
        'slab' : '3'
    }, 

    {
        'data' : {
            "2019-05" : 2987,
            "2019-06" : 36981,
            "2019-07" : 59654,
            "2019-08" : 709863,
            "2019-09" : 2287675,
            "2019-10" : 6689012,
            "2019-11" : 18986914,
            "2019-12" : 50812758,
        },
        'metrics' : '2',
        'slab' : '4'
    }, 
    {
        'data' : {
            "2019-05" : 1492,
            "2019-06" : 35536,
            "2019-07" : 320642,
            "2019-08" : 1230294,
            "2019-09" : 3618482,
            "2019-10" : 10325331,
            "2019-11" : 38579809,
            "2019-12" : 49709164,
        },
        'metrics' : '2',
        'slab' : '5'
    }, 
    {
        'data' : {
            "2019-05" : 1492,
            "2019-06" : 35536,
            "2019-07" : 320642,
            "2019-08" : 1230294,
            "2019-09" : 3618482,
            "2019-10" : 10325331,
            "2019-11" : 38579809,
            "2019-12" : 49709164
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
        },
        'metrics' : '4',
        'slab' : '2'
    }]
    for each_dict in data:
        metrics = each_dict['metrics']
        slab = each_dict['slab']
        data = each_dict['data']
        for each_rec in data:
            rec_count = data[each_rec]
            no_of_days = monthrange(int(each_rec.split('-')[0]), int(each_rec.split('-')[1]))[1]
            final_dict = {}
            for i in range(1, no_of_days + 1):        
                temp_count = rec_count / no_of_days             
                dev = temp_count - ((temp_count * round(random.uniform(0.2, 0.8), 1) ) / 100)
                final_dict[i] = int(dev)

            rem_val = rec_count - sum(final_dict.values()) 
            rem_f = rem_val - (rem_val / rec_count) * rec_count

            for i in final_dict:                    
                final_dict[i] = final_dict[i] + (rem_val / no_of_days)

            ri = random.randint(1, no_of_days)
            final_dict[ri] = final_dict[ri] + rem_f
            
            if (rec_count - sum(final_dict.values())) != 0:
                ri = random.randint(1, no_of_days)
                final_dict[ri] = final_dict[ri] + (rec_count - sum(final_dict.values()))
            
            for each_data in final_dict:
                month_date = datetime.strptime(each_rec + '-' + str(each_data), '%Y-%m-%d')
                # day_of_month = month_date.day
                # week_no = (day_of_month - 1) // 7 + 1
                week_no = month_date.isocalendar()[1]

                save_obj, created = DashboardMetrics.objects.get_or_create(metrics = metrics, metrics_slab = slab, date = month_date,\
                        week_no = week_no)
                if created:
                    final_count = final_dict[each_data]
                    if final_dict[each_data] < 0:
                        print metrics, slab, month_date, week_no, final_dict[each_data]
                        print '============================================='
                        final_count = 0
                    print 'Created....'
                    save_obj.count = final_count
                    save_obj.save()
