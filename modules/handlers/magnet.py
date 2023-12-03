"""
:project: telegram-onedrive
:author: L-ING
:copyright: (C) 2023 L-ING <hlf01@icloud.com>
:license: MIT, see LICENSE for more details.
"""

from time import time
from telethon import events
from ltorrent.lt_async.client import Client, CustomStorage
from ltorrent.lt_async.log import LoggerBase
from modules.client import tg_bot
from modules.env import tg_user_name
from modules.utils import check_in_group, check_tg_login, check_od_login, cmd_parser
from modules.log import logger

port = 8080

class MyStorage(CustomStorage):
    def __init__(self):
        CustomStorage.__init__(self)
    
    def write(self, file_piece_list, data):
        pass

    def read(self, files, block_offset, block_length):
        pass

class MyLogger(LoggerBase):
    def __init__(self, callback):
        LoggerBase.__init__(self)
        self.callback = callback
        self.last_call = time()
    
    async def INFO(self, *args):
        merge_string = ' '.join(map(str, args))
        await self.callback(merge_string)

    async def PROGRESS(self, *args):
        now = time()
        if now - self.last_call > 5:
            merge_string = ' '.join(map(str, args))
            await self.callback(merge_string)
            self.last_call = now
    
    async def FILES(self, *args):
        merge_string = ' '.join(map(str, args))
        await self.callback(merge_string)
    
    async def DEBUG(self, *args):
        merge_string = ' '.join(map(str, args))
        logger(merge_string)

@tg_bot.on(events.NewMessage(pattern="/magnet", incoming=True, from_users=tg_user_name))
@check_in_group
@check_tg_login
@check_od_login
async def magnet_handler(event):
    custom_storage = MyStorage()
    my_logger = MyLogger(event.respond)
    client = Client(
        port=port,
        custom_storage=custom_storage,
        stdout=my_logger
    )

    cmd = cmd_parser(event)
    if len(cmd) == 2:
        # /magnet magnet:?xt=urn:btih:xxxxxxxxxxxx
        if cmd[1].startswith('magnet:?'):
            client.load(magnet_link=cmd[1])
            # '0' for all
            await client.select_file(selection='0')
            await client.run()
        else:
            await event.reply('Format wrong.')
    elif len(cmd) == 1:
        # /magnet list magnet:?xt=urn:btih:xxxxxxxxxxxx
        await event.reply('Format wrong.')
    elif len(cmd) == 3 and cmd[1] == 'list' and cmd[2].startswith('magnet:?'):
        client.load(magnet_link=cmd[2])
        await client.list_file()
    elif len(cmd) >2 and cmd[1].startswith('magnet:?'):
        # /magnet magnet:?xt=urn:btih:xxxxxxxxxxxx 1 3-6 9
        client.load(magnet_link=cmd[1])
        await client.select_file(selection=' '.join(cmd[2:]))
        await client.run()

    raise events.StopPropagation
