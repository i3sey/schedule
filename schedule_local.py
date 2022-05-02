"""
██ ██████  ███████ ███████ ██    ██ 
██      ██ ██      ██       ██  ██  
██  █████  ███████ █████     ████   
██      ██      ██ ██         ██    
██ ██████  ███████ ███████    ██    
Licensed under the GNU aGPLv3
https://www.gnu.org/licenses/agpl-3.0.html
"""
from datetime import datetime, timedelta

import pytz

lessonStarts = {}
lessonsEnds = {}

SHIFT = 'Asia/Yekaterinburg'

TimeZone = pytz.timezone(SHIFT)


def days_schedule():
    """Storage to schedule

    Returns:
        dict: schedule of currect day
    """
    if datetime.isoweekday(datetime.now(TimeZone)) == 3:
        sche = {'1': '08:30–09:10',
                '2': '09:20–10:00',
                '3': '10:15–10:55',
                '4': '11:15–11:55',
                '5': '12:15–12:55',
                '6': '13:05–13:45',
                '7': '13:55–14:35'
                }
        return sche
    else:
        sche = {'1': '08:00–08:40',
                '2': '08:50–09:30',
                '3': '09:45–10:25',
                '4': '10:45–11:25',
                '5': '11:45–12:25',
                '6': '12:35–13:15',
                '7': '13:25–14:05'
                }
        return sche


def sort_time(delta_times):
    """converts dict into list and sort it.

    Args:
        timeRem (dict): number of lesson : delta of times

    Returns:
        list: sorted list
    """
    deltas_list = []
    temp_list = list(delta_times.items())
    for val in temp_list:
        deltas_list.append((val[0], val[1].seconds))
    deltas_list.sort(key=lambda i: i[1])
    return deltas_list


def str_timing(sche_dict, utczone):
    """Find delta of currect time and times from dict

    Args:
        ScheDict (dict): dict with schedule
        utczone (pytz.timezone()): timezone

    Returns:
        dict: number of lesson : delta of times
    """
    time_delta = {}
    for i in sche_dict.items():
        now = datetime.now(utczone).time()
        from_sche = datetime.strptime(i[1], "%H:%M")
        delta_1 = timedelta(hours=now.hour,
                            minutes=now.minute,
                            seconds=now.second)
        delta_2 = timedelta(hours=from_sche.hour,
                            minutes=from_sche.minute,
                            seconds=from_sche.second)
        time_delta[i[0]] = (delta_2-delta_1)
    return time_delta


for key, value in days_schedule().items():
    lessonStarts[key] = value.split('–', maxsplit=1)[0]
    lessonsEnds[key] = value.split('–')[1]
start = sort_time(str_timing(lessonStarts, TimeZone))
end = sort_time(str_timing(lessonsEnds, TimeZone))
if start[1][1] < end[1][1]: 
            print(f'До начала {start[0][0]} урока: \
{datetime.strftime(datetime.utcfromtimestamp(start[0][1]), "%H:%M:%S")}, \
урок начнётся в \
{str(lessonStarts[start[0][0]])}')
else:
    print(f'До конца {end[0][0]} урока: \
{datetime.strftime(datetime.utcfromtimestamp(end[0][1]), "%H:%M:%S")}, \
урок закончится в \
{str(lessonsEnds[end[0][0]])}')
