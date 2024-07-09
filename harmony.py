import requests as rq
from websockets.client import connect
import websockets as ws
import threading
import json
import time
import random
import asyncio

seq_id = None

class HBThread(threading.Thread):
     
    def __init__(self, name, gateway, int):
        threading.Thread.__init__(self)
        self.name = name
        self.gateway = gateway
        self.int = int

    def run(self):
        global seq_id
        while True:

            print('Sending Heartbeat')
            hbr = json.dumps({ "op": 1, "d": seq_id })
            print(hbr)
            asyncio.run(self.gateway.send(hbr))
            print('Sent Heartbeat')
            time.sleep((self.int/1000))
                

            


class DiscordClient:

    def __init__(self, token: str):

        self.token = token
        self.url = rq.get('https://discord.com/api/v9/gateway').json()['url']
        self.hbt = None
        self.gw = None
        self.me = Me(self._get, self._del, self._send)

        print('init')

    async def connect(self):

        print('connecting')










        async with connect(self.url) as gateway:
            print('gateway started')

            self.gw = gateway

            hello = await gateway.recv()
            hb_int = json.loads(hello)['d']['heartbeat_interval']

            ident = json.dumps({
                "op": 2,
                "d": {
                    "token": self.token,
                    "intents": 16782851,
                    "properties": {
                        "os": "linux",
                        "browser": "harmony",
                        "device": "harmony"
                    }
                }
            })


            await gateway.send(ident)
            print('Sent identifier')

            th1 = HBThread('Discord Heartbeat Thread')
            th1.start()


    async def disconnect(self):
        print("Disconnecting...")
        try:
            await self.gw.send(json.dumps({
                "op": 1000,
                "d": {}
            }))
        
        except ws.exceptions.ConnectionClosedOK:
            print('The connection was terminated successfully!')

    def _get(self, endpoint):
        try:
            r = rq.get(

                f"https://discord.com/api/v9/{endpoint}", headers={
                    'Authorization': self.token,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 
                    "Upgrade-Insecure-Requests": "1","DNT": "1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate"
                }
            )
            r.raise_for_status()

            return [r.json(), r.headers]
        
        except rq.exceptions.HTTPError as e:
            print('The request failed with the following error:')
            print(e)
        
        except rq.Timeout:
            print('The request to Discord timed out.')

    def _del(self, endpoint):

        try:
            r = rq.delete(f"https://discord.com/api/v9/{endpoint}", headers={
                'content-type': 'application/json',
                'Authorization': self.token
            })
            r.raise_for_status()

        except rq.exceptions.HTTPError as e:
            print('The request failed with the following error:')
            print(e)
        
        except rq.Timeout:
            print('The request to Discord timed out.')
    
    def _send(self, endpoint, content):



        try:
            r = rq.post(
                
                f"https://discord.com/api/v9/{endpoint}", 

                headers={
                    'content-type': 'application/json',
                    'Authorization': self.token
                },

                data=content

            )
            r.raise_for_status()
        
        except rq.exceptions.HTTPError as e:
            print('The request failed with the following error:')
            print(e)
        
        except rq.Timeout:
            print('The request to Discord timed out.')
    

class Me: 

    def __init__(self, get, drp, post):


        self._get = get
        self._del = drp
        self._send = post


        getself = self._get('users/@me')[0]


        self.id = getself['id']
        self.username = getself['username']
        self.name = getself['global_name']
        self.accent = getself['accent_color']
        self.bio = getself['bio']
        self.avatar = getself['avatar']
    

    async def getGuildList(self):
        guilds = [DiscordGuild(i, self._get, self._del, self._send) for i in (await asyncio.to_thread(self._get('users/@me/guilds')))[0]]
        return guilds


class DiscordGuild:
    def __init__(self, guild, get, drp, post):

        self.id = guild['id']
        self.name = guild['name']
        self.icon = guild['icon']
        self.owner = guild['owner']
        self.features = guild['features']
        self.perms = guild['permissions']

        self._get = get
        self._del = drp
        self._send = post

        self.obj = guild

    def getRaw(self):
        return self.obj

    def getTextChannels(self):
        return [DiscordChannel(i, self._get, self._send) for i in filter(lambda x: True if x["type"] == 0 else False, self._get(f'guilds/{self.id}/channels')[0])]
    
    def getAssignedRoles(self):
        return self._get(f"users/@me/guilds/{self.id}/member")[0]['roles']

    def leave(self):
        self._del(f'users/@me/guilds/{self.id}')

class DiscordChannel:
    def __init__(self, channel, get, post):


        self.obj = channel

        self.lastMsgID = None

        self._get = get
        self._send = post


        self.id = channel['id']
        self.name = channel['name']
        self.type = channel['type']

        #text chan shi
        if self.type == 0:
            self.topic = channel['topic']
            self.parent_id = channel['parent_id'] 
            self.perms = channel['permission_overwrites']
            

        #voice chan shi
        if self.type == 2:
            self.bitrate = channel['bitrate'] 


        #group dm shi     
        if self.type == 3:
            self.icon = channel['icon'] if self.type == 3 else None
            self.recipients = channel['recipients'] if self.type == 3 else None

    def getRaw(self):
        return self.obj
        
    def typeof(self):
            if self.type == 0:
                return "text"
            
            elif self.type == 1:
                return "dm"
            
            elif self.type == 2:
                return "voice"
            
            elif self.type == 3:
                return "group_dm"
            
            elif self.type == 4:
                return "category"
            
            elif self.type == 5:
                return "announcement"
            
            elif self.type == 10:
                return "announcement_thread"
            
            elif self.type == 11:
                return "pub_thread"
            
            elif self.type == 12:
                return "priv_thread"

            elif self.type == 13:
                return "stage"
            
            elif self.type == 14:
                return "server_dir"
            
            elif self.type == 15:
                return "forum"
            
            elif self.type == 16:
                return "thread_only"
            
            else:
                return "unknown"

    def getNMessages(self, n, fromStart = False):

        if self.lastMsgID == None or fromStart == True:
            x = self._get(f'channels/{self.id}/messages?limit={n}')[0]
            self.lastMsgID = x[-1]['id']
            return x
        
        else:
            x = self._get(f'channels/{self.id}/messages?limit={n}&before={self.lastMsgID}')[0]
            self.lastMsgID = x[-1]['id']
            return x

    def sendTextMsg(self, content: str):
        self._send(f"channels/{self.id}/messages", json.dumps({"content": content}))
    
