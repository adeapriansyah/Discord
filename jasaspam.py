    import json
    import time
    import requests
    import os
    import sys
    from datetime import datetime
    from InquirerPy import prompt
    
    
    def simpan_konfigurasi(nama_pelanggan, data):
        with open(f'{nama_pelanggan}.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    # Fungsi untuk memuat konfigurasi pelanggan dari file JSON
    def muat_konfigurasi(filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    else:
                        print(f"Data dalam file {filename} tidak valid. Harus berupa dictionary.")
                        return None
            except json.JSONDecodeError:
                print(f"Kesalahan saat memuat file {filename}: Format JSON tidak valid.")
                return None
        else:
            print(f"File {filename} tidak ditemukan.")
            return None
    # Fungsi untuk memuat daftar channel dari file JSON
    def muat_daftar_channel(filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('channels', {})
        else:
            print(f"File {filename} tidak ditemukan.")
            return {}
    
    # Fungsi untuk mengirim pesan dengan penanganan rate limit
    def send_message(token, channel_id, message, max_retries=3, retry_interval=5):
        url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
        headers = {
            'Authorization': f'{token}',
            'Content-Type': 'application/json'
        }
        json_data = {
            'content': message
        }
    
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=json_data)
    
                if response.status_code == 429:
                    print(f'Rate limited. Retrying after {retry_interval} seconds (Attempt {attempt+1}/{max_retries}).')
                    time.sleep(retry_interval)  # Tunggu selama 5 detik
                    continue
    
                if response.status_code == 200:
                    print(f'Pesan terkirim ke channel {channel_id}')
                    return True
    
                else:
                    print(f'Gagal mengirim pesan ke channel {channel_id}: {response.status_code} - {response.text}')
                    return False
    
            except requests.exceptions.RequestException as e:
                print(f"Terjadi kesalahan: {e}")
                return False
    
        print(f'Gagal mengirim pesan ke channel {channel_id} setelah {max_retries} percobaan.')
        return False
    
    # Fungsi untuk mengedit pesan dengan dropdown daftar channel
    def edit_pesan(nama_pelanggan):
        data = muat_konfigurasi(f'{nama_pelanggan}.json')
        if not data:
            print(f"Tidak ditemukan konfigurasi untuk pelanggan {nama_pelanggan}.")
            return
    
        while True:
            pertanyaan = [
                {
                    "type": "list",
                    "name": "aksi",
                    "message": "Pilih aksi yang ingin dilakukan:",
                    "choices": [
                        "Edit pesan",
                        "Hapus channel",
                        "Tambah channel",
                        "Kembali ke menu utama"
                    ]
                }
            ]
            jawaban = prompt(pertanyaan)
            aksi = jawaban['aksi']
    
            if aksi == "Edit pesan":
                edit_pesan_channel(data, nama_pelanggan)
            elif aksi == "Hapus channel":
                hapus_channel(data, nama_pelanggan)
            elif aksi == "Tambah channel":
                tambah_channel(data, nama_pelanggan)
            else:
                break
    
        simpan_konfigurasi(nama_pelanggan, data)
    
    
    def edit_pesan_channel(data, nama_pelanggan):
        daftar_channel = data.get('channels', {})
        if not daftar_channel:
            print("Tidak ada channel yang tersedia untuk pelanggan ini.")
            return
    
        pertanyaan = [
            {
                "type": "list",
                "name": "channel",
                "message": "Pilih Channel yang ingin diubah pesannya:",
                "choices": [{"name": f"{info.get('nama', 'Tanpa Nama')} - {info.get('message', '')[:20]}", "value": channel_id} for channel_id, info in daftar_channel.items()]
            }
        ]
        jawaban = prompt(pertanyaan)
        channel_id = jawaban['channel']
    
        print("Masukkan Pesan baru yang akan dikirim (Tekan ENTER untuk baris baru, ketik 'Selesai' jika sudah selesai):")
        lines = []
        while True:
            line = input()
            if line.lower() == 'selesai':
                break
            lines.append(line)
        pesan_baru = '\n'.join(lines)
    
        data['channels'][channel_id]['message'] = pesan_baru
        print(f"Pesan di channel {data['channels'][channel_id].get('nama', 'Tanpa Nama')} berhasil diperbarui.")
    
    def hapus_channel(data, nama_pelanggan):
        daftar_channel = data.get('channels', {})
        if not daftar_channel:
            print("Tidak ada channel yang tersedia untuk pelanggan ini.")
            return
    
        filename = 'channels.json'
        semua_channel = muat_daftar_channel(filename)
    
        choices = []
        for channel_id in daftar_channel:
            nama_channel = next((nama for nama, id in semua_channel.items() if id == channel_id), "Channel tidak dikenal")
            choices.append({"name": nama_channel, "value": channel_id})
    
        pertanyaan = [
            {
                "type": "list",
                "name": "channel",
                "message": "Pilih Channel yang ingin dihapus:",
                "choices": choices
            }
        ]
        jawaban = prompt(pertanyaan)
        channel_id = jawaban['channel']
    
        nama_channel = next((nama for nama, id in semua_channel.items() if id == channel_id), "Channel tidak dikenal")
    
        del data['channels'][channel_id]
        print(f"Channel {nama_channel} (ID: {channel_id}) berhasil dihapus.")
    
    def tambah_channel(data, nama_pelanggan):
        filename = 'channels.json'
        daftar_channel = muat_daftar_channel(filename)
    
        if not daftar_channel:
            print("Tidak ada channel yang tersedia untuk ditambahkan.")
            return
    
        pertanyaan = [
            {
                "type": "list",
                "name": "channel",
                "message": "Pilih Channel yang ingin ditambahkan:",
                "choices": [{"name": name, "value": (id, name)} for name, id in daftar_channel.items() if id not in data.get('channels', {})]
            }
        ]
        jawaban = prompt(pertanyaan)
        channel_id, channel_name = jawaban['channel']
    
        print("Masukkan Pesan yang akan dikirim (Tekan ENTER untuk baris baru, ketik 'Selesai' jika sudah selesai):")
        lines = []
        while True:
            line = input()
            if line.lower() == 'selesai':
                break
            lines.append(line)
        pesan = '\n'.join(lines)
        cooldown = int(input("Masukkan Cooldown (dalam detik): "))
    
        if 'channels' not in data:
            data['channels'] = {}
    
        data['channels'][channel_id] = {
            'nama': channel_name,
            'message': pesan,
            'cooldown': cooldown
        }
        print(f"Channel {channel_name} berhasil ditambahkan.")
    
    def setup_pelanggan_baru():
        nama_pelanggan = input("Masukkan nama pelanggan: ")
        token = input("Masukkan Token bot Discord: ")
    
        filename = 'channels.json'
        daftar_channel = muat_daftar_channel(filename)
    
        if not daftar_channel:
            print("Tidak ada channel yang tersedia.")
            return
    
        channels = {}
        while True:
            pertanyaan = [
                {
                    "type": "list",
                    "name": "channel",
                    "message": "Pilih Channel:",
                    "choices": [{"name": name, "value": (id, name)} for name, id in daftar_channel.items()]
                }
            ]
            jawaban = prompt(pertanyaan)
            channel_id, channel_name = jawaban['channel']
    
            print("Masukkan Pesan yang akan dikirim (Tekan ENTER untuk baris baru, ketik 'Selesai' jika sudah selesai):")
            lines = []
            while True:
                line = input()
                if line.lower() == 'selesai':
                    break
                lines.append(line)
            pesan = '\n'.join(lines)
            cooldown = int(input("Masukkan Cooldown (dalam detik): "))
    
            channels[channel_id] = {
                'nama': channel_name,
                'message': pesan,
                'cooldown': cooldown
            }
    
            lanjut = input("Apakah Anda ingin menambahkan channel lagi? (y/n): ").lower()
            if lanjut != 'y':
                break
    
        end_date_input = input("Masukkan Tanggal Akhir (format YYYY-MM-DD HH:MM:SS): ")
        end_date = datetime.strptime(end_date_input, '%Y-%m-%d %H:%M:%S')
    
        data = {
            'token': token,
            'channels': channels,
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        simpan_konfigurasi(nama_pelanggan, data)
    
        print(f"Konfigurasi pelanggan {nama_pelanggan} berhasil disimpan.")
    
    def hapus_pelanggan(nama_pelanggan):
        if os.path.exists(f'{nama_pelanggan}.json'):
            os.remove(f'{nama_pelanggan}.json')
            print(f"Konfigurasi pelanggan {nama_pelanggan} berhasil dihapus.")
        else:
            print(f"Tidak ditemukan konfigurasi untuk pelanggan {nama_pelanggan}.")
    
    # Fungsi utama untuk menjalankan bot dengan konfigurasi yang sudah disimpan
    def jalankan_bot(filename):
        data = muat_konfigurasi(filename)
        if not data:
            print(f"Tidak ditemukan konfigurasi untuk file {filename}.")
            return
    
        token = data['token']
        channels = data.get('channels', {})
        end_date_str = data.get('end_date', None)
    
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            print("Tanggal akhir tidak ditentukan dalam konfigurasi.")
            return
    
        if datetime.now() >= end_date:
            print("Tanggal akhir sudah berlalu. Anda harus mengatur ulang tanggal akhir.")
            end_date_input = input("Masukkan Tanggal Akhir baru (format YYYY-MM-DD HH:MM:SS): ")
            end_date = datetime.strptime(end_date_input, '%Y-%m-%d %H:%M:%S')
            data['end_date'] = end_date.strftime('%Y-%m-%d %H:%M:%S')
            simpan_konfigurasi(filename.replace('.json', ''), data)
    
        last_sent = {channel_id: 0 for channel_id in channels}
    
        # Loop utama untuk pengiriman pesan otomatis
        while True:
            current_time = time.time()
            if datetime.now() >= end_date:
                print("Waktu untuk menjalankan script telah berakhir.")
                break
    
            for channel_id, info in channels.items():
                if current_time - last_sent[channel_id] >= info['cooldown']:
                    success = send_message(token, channel_id, info['message'])
                    if success:
                        last_sent[channel_id] = current_time  # Update waktu pengiriman hanya jika berhasil
                        time.sleep(60)  # Jeda 1 menit sebelum mengirim ke channel berikutnya
                    else:
                        time.sleep(1)  # Jika gagal, tunggu sebentar sebelum mencoba lagi
            time.sleep(1)  # Waktu tunggu minimal sebelum memeriksa kembali
    
    # Fungsi untuk melihat konfigurasi pelanggan
    def lihat_konfigurasi(filename):
        data = muat_konfigurasi(filename)
        if data:
            print(json.dumps(data, indent=4))
        else:
            print(f"Tidak ditemukan konfigurasi untuk file {filename}.")
    
    # Fungsi untuk melihat daftar pelanggan
    def lihat_daftar_pelanggan():
        pelanggan_files = [f for f in os.listdir() if f.endswith('.json') and f != 'channels.json']
        if pelanggan_files:
            print("Daftar pelanggan yang tersedia:")
            for file in pelanggan_files:
                data = muat_konfigurasi(file)
                if data:
                    nama_pelanggan = file.replace('.json', '')
                    token = data.get('token', 'Token tidak tersedia')
                    jumlah_channel = len(data.get('channels', {}))
                    end_date = data.get('end_date', 'Tanggal akhir tidak ditentukan')
                    
                    print(f"\nNama Pelanggan: {nama_pelanggan}")
                    print(f"Token Discord: {token}")
                    print(f"Jumlah Channel: {jumlah_channel}")
                    print(f"End Date: {end_date}")
                else:
                    print(f"Tidak dapat memuat data untuk {nama_pelanggan}.")
        else:
            print("Tidak ada pelanggan yang ditemukan.")
    
    # Fungsi untuk mengecek token Discord dan mendapatkan informasi akun
    def cek_token_discord():
        while True:
            token = input("Masukkan Token Discord: ")
            url = 'https://discord.com/api/v9/users/@me'
            headers = {
                'Authorization': token
            }
    
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    print("\n--- Informasi Akun ---")
                    print(f"ID Akun      : {user_data['id']}")
                    print(f"Nama Akun    : {user_data['username']}")
                    print(f"Discriminator: {user_data['discriminator']}")
                    print(f"Email        : {user_data.get('email', 'Tidak tersedia')}")
                    print(f"Verified     : {'Ya' if user_data['verified'] else 'Tidak'}")
    
                    lanjut = input("\nIngin mengecek token lain? (y/n): ").lower()
                    if lanjut != 'y':
                        break
                else:
                    print(f"Token tidak valid atau ada kesalahan ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Terjadi kesalahan saat menghubungi API Discord: {e}")
    # Modifikasi Menu Utama
    def menu():
        while True:
            print("\n--- Menu Utama ---")
            print("1. Setup pelanggan baru")
            print("2. Lihat daftar pelanggan")
            print("3. Lihat konfigurasi pelanggan")
            print("4. Edit pesan pelanggan")
            print("5. Hapus pelanggan")
            print("6. Lihat tanggal akhir pelanggan")
            print("7. Jalankan bot")
            print("8. Cek Token Discord")
            print("9. Keluar")
    
            pilihan = input("Pilih opsi (1-9): ")
    
            if pilihan == '1':
                setup_pelanggan_baru()
            elif pilihan == '2':
                lihat_daftar_pelanggan()
            elif pilihan == '3':
                nama_pelanggan = input("Masukkan nama pelanggan untuk melihat konfigurasinya: ")
                lihat_konfigurasi(f'{nama_pelanggan}.json')
            elif pilihan == '4':
                nama_pelanggan = input("Masukkan nama pelanggan untuk mengedit pesannya: ")
                edit_pesan(nama_pelanggan)
            elif pilihan == '5':
                nama_pelanggan = input("Masukkan nama pelanggan untuk dihapus: ")
                hapus_pelanggan(nama_pelanggan)
            elif pilihan == '6':
                lihat_tanggal_akhir()
            elif pilihan == '7':
                nama_pelanggan = input("Masukkan nama pelanggan untuk menjalankan bot: ")
                jalankan_bot(f'{nama_pelanggan}.json')
            elif pilihan == '8':
                cek_token_discord()
            elif pilihan == '9':
                print("Keluar dari program.")
                sys.exit()
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")
    
       
    if __name__ == "__main__":
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            jalankan_bot(filename)
        else:
            menu()
    
    
    
    
    「 *TRX DI PROSES ADMIN (mention admin yang menggunakan p)* 」
    
    📆 TANGGAL : Kamis, 12 Desember 2024
    ⌚ JAM     :  (jam padad   )
    ✨ STATUS  : Pending
    📝 Catatan : pesan yang di balas admin
    
    Pesanan (mention yang di balas oleh admin) sedang di proses!
    
    Mohon ditunggu ya ♡