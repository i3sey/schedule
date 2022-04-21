# ██ ██████  ███████ ███████ ██    ██ 
# ██      ██ ██      ██       ██  ██  
# ██  █████  ███████ █████     ████   
# ██      ██      ██ ██         ██    
# ██ ██████  ███████ ███████    ██    
# Licensed under the GNU aGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

# requires: pytz

import asyncio
import re
from datetime import datetime
from random import randint

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
    async def schedulecmd(self, message: Message) -> None:
        strings = []
        for key,item in self.sh.items():
            strings.append("{}: {}".format(str(key).capitalize(), item))
        result = "\n".join(strings)
        await utils.answer(message, result)
        
        