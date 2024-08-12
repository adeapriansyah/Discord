import time
import requests
# Token bot Discord Anda
token = 'TOKEN DISCORD'

# Daftar channel ID, pesan, dan cooldown untuk setiap channel
channels = {
    '846673193426354176': {'message': 'SELL CHEAP ITEM PLATFORM AT TK81\n\n Fire escape 45/1\n Seagull 9/1\n Hover platform 3/1\n Climbing vine 23/1\n Ladder 45/1\n Bountiful bamboo ladder 30/1\n Cave platform 100/1\n Creepstone Platform 20/1\n Rickety ladder 45/1\n Starship deck ladder 7/1\n', 'cooldown': 7200},
    '846661246303469598': {'message': 'SELL CHEAP ITEM SIGN AT TK81\n\nGuestbook 4/1\n bulletin board 4/1\n tavern sign 4/1\n mailbox 5/1\n holographic 2\n Sell open sign 8/1\n Digital sign 2\n message 1\n', 'cooldown': 7200},
    '846671811223355402': {'message': 'SELL CHEAP ITEM DOOR AT TK81\n\nHospital Door 70/1\n Saloon Door 100/1\n Dungeon Door 50/1\n Screen Door 30/1\n Password Door 3/1\n Gateway Adventure 4/1\n Hellgate 4/1\n Time Space 3/1\n Mystery Portal 4/1\n Love Portal 2/1\n Orange Portal  2/1\n Blue Portal 10/1\n Forcefield 3/1\n House Entrance 70/1\n Jail Door 4/1\n Coin Door 40/1\n Hidden Door 90/1\n Air Vent 70/1\n Portcullis 35/1\n Ancient Stone Gate 10/1\n Dragon Gate 12/1\n', 'cooldown': 7200},
    '782718523629633567': {'message': 'SELL CHEAP ITEM BACKGROUND AT TK81\n\nStreetlamp 35/1\n Fireplace 7/1\n Table lamp 100/1\n Moon lamp 30/1\n Flatscreen TV 10/1\n Lovewillow lace 20/1\n Foliage 30/1\n Weeping willow streamers 9/1\n Sequoia tree 12/1\n Starship Light Wall 21/1\n Sandstone wall 45/1\n Mahogany frame 20/1\n Red wood wall 100/1\n Wooden window 100/1\n Grimstone background 100/1\n Wooden background 100/1\n Windows curtain 100/1\n Stained glass 4/1\n Noblemans house 20/1\n Dark walnut wall 35/1\n Cliffside 100/1\n The darkness 25/1\n Black wallpaper 9/1\n Brown wallpaper 9/1\n Grey wallpaper 9/1\n Red wallpaper 9/1\n Aqua wallpaper 9/1\n Green wallpaper 9/1\n White wallpaper 8/1\n Orange wallpaper 9/1\n Blue wallpaper 8/1\n Purple wallpaper 8/1\n Yellow wallpaper 9/1\n Dark Yellow Wallpaper 35/1\n Dark Brown Wallpaper 35/1\n Dark Blue Wallpaper 25/1\n Dark red wallpaper 3/1\n Dark aqua wallpaper 35/1\n Dark green wallpaper 35/1\n Dark Grey wallpaper 20/1\n Dark Orange Wallpaper 35/1\n', 'cooldown': 7200},
    '1104057271215984741': {'message': 'SELL CHEAP ITEM BLOCKS AT TK81\n\n  Clouds Block 10/1 Glowy Block 11/1 Cutaway Block 50/1 Granite Block 30/1 Marble Block 12/1 Hedge Block 150/1 Pillar 7/1 Basic Blue Block 4/1 Heartcastle Stone 35/1 Heartcastle Column 20/1 Crystalized star Block 25/1 Space Dirt 100/1 Granite Column 9/1 Deep Sand 100/1 Adventure Barrier 15/1 Fertile Soil 120/1 Lovewillow 30/1 Weeping willow foliage 30/1 Transmatter Field 3/1 Donation Box 3/1 Bookcase 10/1  Display Shelf 8/1 Giant Clam 15/1 Treasure Chest 15/1 Display Box 5/1 Display Block 3/1 Blue Mailbox 60/1 Pathmaker 80/1 Objective Marker 4/1 Adventure Checkpoint 4/1 Flower Checkpoint 5/1 Checkpoint 9/1', 'cooldown': 21600},
    '806523338797219860': {'message': 'SELL CHEAP ITEM JAMMER AT TK81\n\n  Zombie Jammer 8\n Signal Jammer 1\n Punch Jammer 8\n Ghost Charm  30\n Minimod 85\n Firehouse 5\n Antigravity 230\n Door Mover 3\n Security Camera 7\n Change of Address 13\n Starship Security Camera  5\n Pigeon 6\n', 'cooldown': 7200},
    '774455258407370752': {'message': 'SELL CHEAP ITEM PAINT AT TK81\n\n  Portrait 11\n Paint Brush 20\n Paint bucket - yellow 21/1\n Paint bucket - varnish 21/1\n Paint bucket - red 12/1\n Paint bucket - purple 12/1\n Paint bucket - charcoal 11/1\n Paint bucket - blue 20/1\n Paint bucket - green 21/1\n Paint bucket - aqua 22/1\n', 'cooldown': 7200},
    '782718823488290826': {'message': 'SELL CHEAP ITEM BLAST AT TK81\n\n  DESERT BLAST 80\n JUNGLE BLAST 70\n MARS BLAST 10\n HARVEST MOON BLAST 4\n CAVE BLAST  17\n SURGWORLD BLAST 2\n BOUNTIFUL BLAST 6\n UNDERSEA BLAST 8\n TREASURE BLAST 5\n THERMONUCLEAR BLAST 8\n', 'cooldown': 7200},
    '806494474200547338': {'message': 'SELL CHEAP ITEM LOCKE AT TK81\n\n Birth certificate 16\n VIP entrance 25\n Extract o snap 15\n Wolf Whistle 16', 'cooldown': 7200},
}
# Cooldown time between sending messages in different channels (in seconds)
global_cooldown = 10  # Sesuaikan dengan kebutuhan Anda

# Fungsi untuk mengirim pesan dengan penanganan rate limit
def send_message(channel_id, message, max_retries=3):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'{token}',
        'Content-Type': 'application/json'
    }
    json = {
        'content': message
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=json)

            # Penanganan jika terkena rate limit
            if response.status_code == 429:
                retry_after = response.json().get('rate_limit', 5)
                print(f'Rate limited. Retrying after {retry_after} seconds (Attempt {attempt+1}/{max_retries}).')
                time.sleep(retry_after)
                continue  # Coba lagi setelah waktu `retry_after`

            # Jika pengiriman sukses
            if response.status_code == 200:
                print(f'Pesan terkirim ke channel {channel_id}')
                return True  # Berhasil, keluar dari fungsi

            # Jika gagal dengan status selain 429
            else:
                print(f'Gagal mengirim pesan ke channel {channel_id}: {response.status_code} - {response.text}')
                return False  # Gagal, keluar dari fungsi

        except requests.exceptions.RequestException as e:
            print(f"Terjadi kesalahan: {e}")
            return False  # Error lain, keluar dari fungsi

    print(f'Gagal mengirim pesan ke channel {channel_id} setelah {max_retries} percobaan.')
    return False  # Gagal setelah semua percobaan

# Menyimpan waktu terakhir pengiriman pesan untuk setiap channel
last_sent = {channel_id: 0 for channel_id in channels}

# Loop utama untuk pengiriman pesan otomatis
while True:
    current_time = time.time()
    for channel_id, info in channels.items():
        if current_time - last_sent[channel_id] >= info['cooldown']:
            success = send_message(channel_id, info['message'])
            if success:
                last_sent[channel_id] = current_time  # Update waktu pengiriman hanya jika berhasil
            time.sleep(global_cooldown)  # Tambahkan waktu jeda antara pengiriman pesan ke channel berikutnya
    time.sleep(1)  # Waktu tunggu minimal sebelum memeriksa kembali
