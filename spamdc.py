import time
import requests                                         
# Token bot Discord Anda
token='Your Token'
                                                        # Daftar channel ID, pesan, dan cooldown untuk setiap channel
channels = {
    '846673193426354176': {'message': 'SELL CHEAP ITEM PLATFORM AT W3CR\n\n Fire escape 45/1 Seagull 9/1 Hover platform 3/1 Climbing vine 23/1 Ladder 45/1 Bountiful bamboo ladder 30/1 Cave platform 100/1 Creepstone Platform 20/1 Rickety ladder 45/1 Starship deck ladder 7/1', 'cooldown': 7300},
    '846661246303469598': {'message': 'SELL CHEAP ITEM SIGN AT W3CR\n\nGuestbook 4/1 bulletin board 4/1 tavern sign 4/1 mailbox 5/1 holographic 2 Sell open sign 8/1 Digital sign 2 message 1', 'cooldown': 7400},
    '846671811223355402': {'message': 'SELL CHEAP ITEM DOOR AT W3CR\n\nHospital Door 70/1 Saloon Door 100/1 Dungeon Door 50/1 Screen Door 30/1 Password Door 3/1 Gateway Adventure 4/1 Hellgate 4/1 Time Space 3/1 Mystery Portal 4/1 Love Portal 2/1 Orange Portal  2/1 Blue Portal 10/1 Forcefield 3/1 House Entrance 70/1 Jail Door 4/1 Coin Door 40/1 Hidden Door 90/1 Air Vent 70/1 Portcullis 35/1 Ancient Stone Gate 10/1 Dragon Gate 12/1', 'cooldown': 7500},
    '782718523629633567': {'message': 'SELL CHEAP ITEM BACKGROUND AT W3CR\n\nStreetlamp 35/1 Fireplace 7/1 Table lamp 100/1 Moon lamp 30/1 Flatscreen TV 10/1 Lovewillow lace 20/1 Foliage 30/1 Weeping willow streamers 9/1 Sequoia tree 12/1 Starship Light Wall 21/1 Sandstone wall 45/1 Mahogany frame 20/1 Red wood wall 100/1 Wooden window 100/1 Grimstone background 100/1 Wooden background 100/1 Windows curtain 100/1 Stained glass 4/1 Noblemans house 20/1 Dark walnut wall 35/1 Cliffside 100/1 The darkness 25/1 Black wallpaper 9/1 Brown wallpaper 9/1 Grey wallpaper 9/1 Red wallpaper 9/1 Aqua wallpaper 9/1 Green wallpaper 9/1 White wallpaper 8/1 Orange wallpaper 9/1 Blue wallpaper 8/1 Purple wallpaper 8/1 Yellow wallpaper 9/1 Dark Yellow Wallpaper 35/1 Dark Brown Wallpaper35/1 Dark Blue Wallpaper 25/1 Dark red wallpaper 3/1 Dark aqua wallpaper 35/1 Dark green wallpaper 35/1 Dark Grey wallpaper 20/1 Dark Orange Wallpaper 35/1', 'cooldown': 7600},
    '1104057271215984741': {'message': 'SELL CHEAP ITEM BLOCKS AT W3CR\n\n  Clouds Block 10/1 Glowy Block 11/1 Cutaway Block 50/1 Granite Block 30/1 Marble Block 12/1 Hedge Block 150/1 Pillar 7/1 Basic Blue Block 4/1 Heartcastle Stone 35/1 Heartcastle Column 20/1 Crystalized star Block 25/1 Space Dirt 100/1 Granite Column 9/1 Deep Sand 100/1 Adventure Barrier 15/1 Fertile Soil 120/1 Lovewillow 30/1 Weeping willow foliage 30/1 Transmatter Field 3/1 Donation Box 3/1 Bookcase 10/1  Display Shelf 8/1 Giant Clam 15/1 Treasure Chest 15/1 Display Box 5/1 Display Block 3/1 Blue Mailbox 60/1 Pathmaker 80/1 Objective Marker 4/1 Adventure Checkpoint 4/1 Flower Checkpoint 5/1 Checkpoint 9/1', 'cooldown': 21700},
    '806523338797219860': {'message': 'SELL CHEAP ITEM JAMMER AT W3CR\n\n  Zombie Jammer 8 Signal Jammer 1 Punch Jammer 8 Ghost Charm  30 Minimod 85 Firehouse 5 Antigravity 230 Door Mover 3 Security Camera 7 Change of Address 13 Starship Security Camera  5 Pigeon 6', 'cooldown': 7700},
    '774455258407370752': {'message': 'SELL CHEAP ITEM PAINT AT W3CR\n\n  Portrait 11 Paint Brush 20 Paint bucket - yellow 21/1 Paint bucket - varnish 21/1 Paint bucket - red 12/1 Paint bucket - purple 12/1 Paint bucket - charcoal 11/1 Paint bucket - blue 20/1 Paint bucket - green 21/1 Paint bucket - aqua 22/1', 'cooldown': 7800},
    '782718823488290826': {'message': 'SELL CHEAP ITEM BLAST AT W3CR\n\n  DESERT BLAST 80 JUNGLE BLAST 70 MARS BLAST 10 HARVEST MOON BLAST 4 CAVE BLAST  17 SURGWORLD BLAST 2 BOUNTIFUL BLAST 6 UNDERSEA BLAST 8 TREASURE BLAST 5 THERMONUCLEAR BLAST 8', 'cooldown': 7900},
    '806494474200547338': {'message': 'SELL CHEAP ITEM LOCKE AT W3CR\n\n Birth certificate 16 VIP entrance 25 Extract o snap 15 Wolf Whistle 16', 'cooldown': 8000},
}

# Cooldown time between sending messages in different channels (in seconds)
global_cooldown = 10  # Sesuaikan dengan kebutuhan Anda

# Fungsi untuk mengirim pesan
def send_message(channel_id, message):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'{token}',
        'Content-Type': 'application/json'
    }
    json = {
        'content': message
    }
    response = requests.post(url, headers=headers, json=json)
    if response.status_code == 200:
        print(f'Pesan terkirim ke channel {channel_id}')
    else:
        print(f'Gagal mengirim pesan ke channel {channel_id}: {response.status_code}')

# Menyimpan waktu terakhir pengiriman pesan untuk setiap channel
last_sent = {channel_id: 0 for channel_id in channels}

# Loop utama untuk pengiriman pesan otomatis
while True:
    current_time = time.time()
    for channel_id, info in channels.items():
        if current_time - last_sent[channel_id] >= info['cooldown']:
            send_message(channel_id, info['message'])
            last_sent[channel_id] = current_time
            time.sleep(global_cooldown)  # Tambahkan waktu jeda antara pengiriman pesan ke channel berikutnya
    time.sleep(1)  # Waktu tunggu minimal sebelum memeriksa kembali

# Cooldown time between sending messages in different channels (in seconds)
#global_cooldown = 10  # Sesuaikan dengan kebutuhan Anda


# Fungsi untuk mengirim pesan
#def send_message(channel_id, message):
   # url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
  # headers = {
     #   'Authorization': f'{token}',
    #    'Content-Type': 'application/json'
   # }
  #  json = {
 #       'content': message
#    }
    #response = requests.post(url, headers=headers, json=json)
    #if response.status_code == 200:
   #     print(f'Pesan terkirim ke channel {channel_id}')
  #  else:
 #       print(f'Gagal mengirim pesan ke channel {channel_id}: {response.status_code}')
#
# Menyimpan waktu terakhir pengiriman pesan untuk setiap channel
#last_sent = {channel_id: 0 for channel_id in channels}

# Loop utama untuk pengiriman pesan otomatis
#while True:
    #current_time = time.time()
    #for channel_id, info in channels.items():
   #     if current_time - last_sent[channel_id] >= info['cooldown']:
  #          send_message(channel_id, info['message'])
 #           last_sent[channel_id] = current_time
#print(f"Menunggu {global_cooldown_time} detik sebelum mengirim pesan ke channel berikutnya...")

#   time.sleep(global_cooldown)
#    time.sleep(global_cooldown)  # Waktu tunggu minimal sebelum memeriksa kembali
