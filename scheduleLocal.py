from datetime import datetime, timedelta

import pytz

lessonStarts = {}
lessonsEnds = {}
timeRem = {}
sche = {'1': '08:00–08:40',
        '2': '08:50–09:30',
        '3': '09:45–10:25',
        '4': '10:45–11:25',
        '5': '11:45–12:25',
        '6': '12:35–13:15',
        '7': '13:25–14:05'
        }
shift = 'Asia/Yekaterinburg'

TimeZone = pytz.timezone(shift)

for key, value in sche.items():
    lessonStarts[key] = value.split('–')[0]
    lessonsEnds[key] = value.split('–')[1]
for i in lessonStarts.items():
    a = datetime.now(TimeZone).time()
    b = datetime.strptime(i[1], "%H:%M")
    d1 = timedelta(hours=a.hour, minutes=a.minute, seconds=a.second)
    d2 = timedelta(hours=b.hour, minutes=b.minute, seconds=b.second)
    timeRem[i[0]] = str((d2-d1))
    
  
enter = input('Введи урок: ')
t = str(timeRem[enter]).replace('-1 day, ', '')
print(f'До начала {enter} урока: {t}, урок начнётся в {lessonStarts[enter]}')

#TODO
#Научиться находить ближайший урок
