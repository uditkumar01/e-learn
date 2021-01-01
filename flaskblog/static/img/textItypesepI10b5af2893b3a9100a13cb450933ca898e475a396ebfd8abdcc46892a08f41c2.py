from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel, InputPeerUser
import yaml
import sys
import logging
import  configparser
import  json
import re
from  telethon  import  TelegramClient , events
from  telethon . errors  import  SessionPasswordNeededError

# to get channel members
import  telethon . sync

from  pprint  import  pprint

from urlextract import URLExtract

def get_urls(text):
    extractor = URLExtract()
    urls = []
    if text:
        for url in extractor.gen_urls(text):
            urls.append(url)
        return urls
    return []

# def get_URs(text):
#     results




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    client = TelegramClient(config["session_name"], 
                            config["api_id"], 
                            config["api_hash"])
    client.start()

    input_channels_entities = []
    output_channel_entities = []
    for d in client.iter_dialogs():
        if str(d.entity.id) in config["input_channel_names"]:
            input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
        if str(d.entity.id) in config["output_channel_names"]:
            
                output_channel_entities.append(
                [InputPeerUser(d.entity.id, d.entity.access_hash),InputChannel(d.entity.id, d.entity.access_hash)]
            )
            
    if not output_channel_entities:
        logger.error(f"Could not find any output channels in the user's dialogs")
        sys.exit(1)

    if not input_channels_entities:
        logger.error(f"Could not find any input channels in the user's dialogs")
        sys.exit(1)
        
    logging.info(f"Listening on {len(input_channels_entities)} channels. Forwarding messages to {len(output_channel_entities)} channels.")
    
    @client.on(events.NewMessage(chats=input_channels_entities))
    async def handler(event):
        event.message.message ="🔥Udit is pro🔥\n\n"+event.message.message+"\n\n❤️Made by Udit Pro"
        print(get_urls(event.message.message))
        urls = get_urls(event.message.message)
        LEN = len(urls)
        for url in range(LEN):
            if url!=LEN-1:
                z = event.message.message.find(urls[url])
                event.message.message = event.message.message[:z] + event.message.message[z+len(urls[url])+1:]
            else:
                event.message.message = event.message.message.replace(urls[url],'https://t.me/joinchat/AAAAAFcWQf-xUVZzR7njig')
                
        urls = re.findall("[@][\w\d]*",event.message.message)
        LEN = len(urls)
        for ur in range(LEN):
            if ur!=LEN-1:
                event.message.message = event.message.message.replace(urls[ur],'')
            else:
                if 'https://t.me/joinchat/AAAAAFcWQf-xUVZzR7njig' in event.message.message:
                    event.message.message = event.message.message.replace(urls[ur],'')
                else:
                    event.message.message = event.message.message.replace(urls[ur],'https://t.me/joinchat/AAAAAFcWQf-xUVZzR7njig')
        
        if "www." in event.message.message:
            while(True):
                z = event.message.message.find('www.')
                if z:
                    event.message.message[z:z+5]
                else:
                    break
        for output_channel in output_channel_entities:
            
            try:
                print("C"*20)
                await client.send_message(output_channel[0], event.message)
            except:
                print("D"*20)
                await client.send_message(output_channel[1], event.message)

            

    client.run_until_disconnected()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{CONFIG_PATH}}")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.safe_load(f)
    start(config)
