import harmony
import time
import asyncio





if __name__ == '__main__':

    async def main():

        token = 'NjE1Mjk2NTY3ODQyMzA4MTYz.GKeVNn.FRIEC1zu7kLgNYylYyR3Ro76rNZaxxJBsMQXN0'


        client = harmony.DiscordClient(token=token)

        await client.connect()
        print('we connected successfully')

        s = (await client.me.getGuildList())
        print('we got user guilds asyncly')

        print(s)
  



        await client.disconnect()
       

    asyncio.run(main())