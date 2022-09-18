"""
██ ██████  ███████ ███████ ██    ██ 
██      ██ ██      ██       ██  ██  
██  █████  ███████ █████     ████   
██      ██      ██ ██         ██    
██ ██████  ███████ ███████    ██    
Licensed under the GNU aGPLv3
https://www.gnu.org/licenses/agpl-3.0.html
"""
# requires: pytz
import re

from datetime import datetime, timedelta
from email.mime import message

import pytz
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class ScheduleMod(loader.Module):
    """Lesson time schedule"""

    strings = {
        "name": "lessonSchedule",
        'noneArg': f'<b>Не указаны аргументы.\nВот список поддерживаемых поясов\n{pytz.common_timezones}</b>',
        'setShift': '<b>Смещение установлено.</b>',
        'notCurrect': '<b>Указано неверное смещение</b>',
        "noneSetuped": 'Расписание указано неверно!',
        "sucSetuped": '<b>Расписание установлено, вы можете посмотреть его с помощью <code>.schedule</code></b>',
    }

    async def client_ready(self, client, db) -> None:
        self._client = client
        self._db = db
        self.ts = self._db.get("Schedule", "shift", {})
        self.sh = self._db.get("Schedule", "setup", {})
        #self.sh = {}
        
    
    async def days_schedule(self):
        """Storage to schedule

        Returns:
            dict: schedule of currect day
        """
        if datetime.isoweekday(datetime.now(pytz.timezone(self.ts.get('shift')))) == 1:
            sche = {'1': '08:35–09:15',
                    '2': '09:25–10:05',
                    '3': '10:20–11:00',
                    '4': '11:20–12:00',
                    '5': '12:20–13:00',
                    '6': '13:10–13:50',
                    '7': '14:00–14:40',
                    '8': '14:50-15:30'
                    }
            return sche
        else:
            sche = {'1': '08:00–08:40',
                    '2': '08:50–09:30',
                    '3': '09:45–10:25',
                    '4': '10:45–11:25',
                    '5': '11:45–12:25',
                    '6': '12:35–13:15',
                    '7': '13:25–14:05',
                    '8': '14:15-14:55'
                    }
            return sche
    
    async def sort_time(self, delta_times):
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
    
    async def str_timing(self, sche_dict):
        """Find delta of currect time and times from dict

        Args:
            ScheDict (dict): dict with schedule
            utczone (pytz.timezone()): timezone

        Returns:
            dict: number of lesson : delta of times
        """
        time_delta = {}
        for i in sche_dict.items():
            now = datetime.now(pytz.timezone(self.ts.get('shift'))).time()
            from_sche = datetime.strptime(i[1], "%H:%M")
            delta_1 = timedelta(hours=now.hour,
                                minutes=now.minute,
                                seconds=now.second)
            delta_2 = timedelta(hours=from_sche.hour,
                                minutes=from_sche.minute,
                                seconds=from_sche.second)
            time_delta[i[0]] = (delta_2-delta_1)
        return time_delta
    
    async def shiftcmd(self, message: Message) -> None:
        """Смещение UTC в форме Часть света/Город (например Asia/Yekaterinburg)."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args == "" and not reply:
            await utils.answer(message, self.strings("noneArg"))
            return
        if args == "":
            args = reply.text
            
        try:
            TimeZone = pytz.timezone(args)
        except pytz.UnknownTimeZoneError:
            await utils.answer(message, self.strings("notCurrect"))
        else: 
            self.ts['shift'] = args
            self._db.set("Schedule", "shift", self.ts)
            await utils.answer(message, self.strings('setShift'))
            
    @loader.unrestricted
    async def timecmd(self, message: Message) -> None:
        """Показать текущее время на сервере"""
        TimeZone = pytz.timezone(self.ts.get('shift'))
        shift = datetime.now(TimeZone)
        current_time = shift.strftime("%H:%M")
        await utils.answer(message, current_time)
        
    async def setupcmd(self, message: Message) -> None:
        """Настроить расписание"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args == "" and not reply:
            await utils.answer(message, self.strings("noneSetuped"))
            return
        if args == "":
            args = reply.text
        lesson = re.split(". |\n", args)
        num = []
        less = []
        for element in lesson:
            if element.isnumeric():
                num.append(int(element))
            else:
                less.append(element)
        self.sh = dict(zip(num, less))
        await utils.answer(message, self.strings("sucSetuped"))
        self._db.set("Schedule", "setup", self.sh)
        
    @loader.unrestricted
    async def tscmd(self, message: Message) -> None:
        """Текущее расписание на день"""
        strings = []
        items = await self.days_schedule()
        for key,item in items.items():
            strings.append("{}: {}".format(str(key).capitalize(), item))
        result = "\n".join(strings)
        await utils.answer(message, result)
        
    @loader.unrestricted
    async def tlcmd(self, message: Message) -> None:
        """Конец/Начало близжайшего урока"""
        lessonStarts = {}
        lessonsEnds = {}
        temp = await self.days_schedule()
        for key, value in temp.items():
            lessonStarts[key] = value.split('–', maxsplit=1)[0]
            lessonsEnds[key] = value.split('–')[1]
        start = await self.sort_time(await self.str_timing(lessonStarts))
        end = await self.sort_time(await self.str_timing(lessonsEnds))
        if start[1][1] < end[1][1]:
            answer = f'До начала {start[0][0]} урока: <code>{datetime.strftime(datetime.utcfromtimestamp(start[0][1]), "%H:%M:%S")}</code>\nУрок начнётся в <code>{str(lessonStarts[start[0][0]])}:00</code>'
        else:
            answer = f'До конца {end[0][0]} урока: <code>{datetime.strftime(datetime.utcfromtimestamp(end[0][1]), "%H:%M:%S")}</code>\nУрок закончится в: <code>{str(lessonsEnds[end[0][0]])}:00</code>'
        await utils.answer(message, answer)
        
        
