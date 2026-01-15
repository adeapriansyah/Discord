import json
import time
import requests
import os
import sys
from datetime import datetime, timedelta
from getpass import getpass
from InquirerPy import prompt

def simpan_konfigurasi(nama_pelanggan, data):
    with open(f'{nama_pelanggan}.json', 'w') as f:
        json.dump(data, f, indent=4)

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

def muat_daftar_channel(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('channels', {})
    else:
        print(f"File {filename} tidak ditemukan.")
        return {}

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
                print(f'Rate limited. Mencoba lagi setelah {retry_interval} detik (Percobaan {attempt+1}/{max_retries}).')
                time.sleep(retry_interval)
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

def ambil_token_discord(email, password):
    url = 'https://discord.com/api/v9/auth/login'
    headers = {'Content-Type': 'application/json'}
    data = {'login': email, 'password': password}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                print("\nSukses! Token berhasil diambil.")
                return token, None
            else:
                return None, "Tidak ada token di respon."
        elif response.status_code == 400:
            error_data = response.json()
            if 'mfa' in response.text.lower():
                print("\nAkun memerlukan verifikasi 2FA.")
                ticket = error_data.get('ticket')
                if not ticket:
                    return None, "Tidak ada ticket untuk 2FA."
                token = tangani_2fa(ticket)
                return token, None if token else "Gagal mendapatkan token setelah 2FA."
            else:
                error_message = error_data.get('message', 'Kesalahan tidak diketahui')
                if 'INVALID_LOGIN' in response.text:
                    return None, "Email atau kata sandi salah."
                return None, f"{error_message} Detail: {response.text}"
        else:
            return None, f"Kesalahan API: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Masalah jaringan: {e}"

def tangani_2fa(ticket):
    print("Buka aplikasi autentikator (contoh: Google Authenticator) untuk dapatkan kode 2FA.")
    code = input("Masukkan kode 2FA: ").strip()
    if not code:
        print("Kode 2FA tidak boleh kosong!")
        return None

    url = 'https://discord.com/api/v9/auth/mfa/totp'
    headers = {'Content-Type': 'application/json'}
    data = {'code': code, 'ticket': ticket}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                print("\nSukses! Token berhasil diambil.")
                return token
            else:
                print("\nGagal: Tidak ada token di respon.")
                return None
        else:
            print(f"\nGagal: {response.json().get('message', 'Kode 2FA salah atau kesalahan lain')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"\nGagal: Masalah jaringan - {e}")
        return None

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
            "type": "fuzzy",
            "name": "channel",
            "message": "Pilih Channel yang ingin diubah pesannya:",
            "choices": [{"name": f"{info.get('nama', 'Tanpa Nama')} - {info.get('message', '')[:20]}", "value": channel_id} for channel_id, info in daftar_channel.items()]
        }
    ]
    jawaban = prompt(pertanyaan)
    channel_id = jawaban['channel']

    print("Masukkan Pesan baru yang akan dikirim (Tekan ENTER untuk baris baru, ketik 'd' jika sudah selesai):")
    lines = []
    while True:
        line = input()
        if line.lower() == 'd':
            break
        lines.append(line)
    pesan_baru = '\n'.join(lines)

    data['channels'][channel_id]['message'] = pesan_baru
    print(f"Pesan di channel {data['channels'][channel_id].get('nama', 'Tanpa Nama')} berhasil diperbarui.")
    simpan_konfigurasi(nama_pelanggan, data)

def hapus_channel(data, nama_pelanggan):
    daftar_channel = data.get('channels', {})
    if not daftar_channel:
        print("Tidak ada channel yang tersedia untuk pelanggan ini.")
        return

    filename = 'channels2.json'
    semua_channel = muat_daftar_channel(filename)

    choices = []
    for channel_id, info in daftar_channel.items():
        # Cari nama channel dari channels2.json berdasarkan ID
        channel_name = None
        for name, channel_info in semua_channel.items():
            if channel_info.get('id') == channel_id:
                channel_name = name
                break
        
        # Jika tidak ditemukan, gunakan nama dari data pelanggan
        if not channel_name:
            channel_name = info.get('nama', 'Channel tidak dikenal')
        
        choices.append({"name": f"{channel_name} (ID: {channel_id})", "value": channel_id})

    if not choices:
        print("Tidak ada channel yang dapat dipilih.")
        return

    pertanyaan = [
        {
            "type": "fuzzy",
            "name": "channel",
            "message": "Pilih Channel yang ingin dihapus:",
            "choices": choices
        }
    ]
    jawaban = prompt(pertanyaan)
    channel_id = jawaban['channel']

    # Dapatkan nama channel untuk pesan konfirmasi
    channel_name = "Channel tidak dikenal"
    for name, channel_info in semua_channel.items():
        if channel_info.get('id') == channel_id:
            channel_name = name
            break
    if channel_name == "Channel tidak dikenal":
        channel_name = daftar_channel[channel_id].get('nama', 'Channel tidak dikenal')

    del data['channels'][channel_id]
    print(f"Channel {channel_name} (ID: {channel_id}) berhasil dihapus.")
    simpan_konfigurasi(nama_pelanggan, data)

def tambah_channel(data, nama_pelanggan):
    filename = 'channels2.json'
    daftar_channel = muat_daftar_channel(filename)

    if not daftar_channel:
        print("Tidak ada channel yang tersedia untuk ditambahkan.")
        return

    # Buat daftar pilihan channel yang belum ada di data pelanggan
    choices = []
    for name, info in daftar_channel.items():
        channel_id = info.get('id')
        if channel_id and channel_id not in data.get('channels', {}):
            choices.append({"name": f"{name} (ID: {channel_id})", "value": (channel_id, name)})

    if not choices:
        print("Tidak ada channel baru yang tersedia untuk ditambahkan.")
        return

    pertanyaan = [
        {
            "type": "fuzzy",
            "name": "channel",
            "message": "Pilih Channel yang ingin ditambahkan:",
            "choices": choices
        }
    ]
    jawaban = prompt(pertanyaan)
    channel_id, channel_name = jawaban['channel']

    print("Masukkan Pesan yang akan dikirim (Tekan ENTER untuk baris baru, ketik 'd' jika sudah selesai):")
    lines = []
    while True:
        line = input()
        if line.lower() == 'd':
            break
        lines.append(line)
    pesan = '\n'.join(lines)
    
    # Ambil cooldown dari channels2.json, fallback ke 3600 jika tidak ada
    cooldown = daftar_channel[channel_name].get('cooldown', 3600)

    if 'channels' not in data:
        data['channels'] = {}

    data['channels'][channel_id] = {
        'nama': channel_name,
        'message': pesan,
        'cooldown': cooldown
    }
    print(f"Channel {channel_name} berhasil ditambahkan dengan cooldown {cooldown // 3600} jam.")
    simpan_konfigurasi(nama_pelanggan, data)

def setup_pelanggan_baru():
    while True:
        nama_pelanggan = input("Masukkan nama pelanggan: ").strip()
        if not nama_pelanggan:
            print("Nama pelanggan tidak boleh kosong!")
            continue

        email = input("Masukkan email Discord: ").strip()
        if not email:
            print("Email tidak boleh kosong!")
            continue
        
        password = getpass("Masukkan kata sandi Discord (tidak terlihat): ").strip()
        if not password:
            print("Kata sandi tidak boleh kosong!")
            continue

        print("\nMengambil token Discord...")
        token, error_message = ambil_token_discord(email, password)
        if not token:
            print(f"Gagal mendapatkan token: {error_message}")
            lanjut = input("Coba lagi dengan email/kata sandi lain? (y/n): ").lower()
            if lanjut != 'y':
                print("Setup pelanggan dibatalkan.")
                return
            continue

        # Gunakan email Discord sebagai alamat Gmail
        gmail = email

        filename = 'channels2.json'
        daftar_channel = muat_daftar_channel(filename)

        if not daftar_channel:
            print("Tidak ada channel yang tersedia.")
            return

        default_channel_id = "default_channel"
        default_channel_name = "Channel Default"
        default_message = "Pesan default untuk channel ini."
        default_cooldown = 1

        channels = {
            default_channel_id: {
                'nama': default_channel_name,
                'message': default_message,
                'cooldown': default_cooldown * 3600
            }
        }

        while True:
            hari_input = input("Masukkan jumlah hari untuk tanggal berakhir: ").strip()
            try:
                hari = int(hari_input)
                if hari <= 0:
                    print("Jumlah hari harus lebih dari 0!")
                    continue
                # Hitung tanggal berakhir dari waktu saat ini + jumlah hari
                end_date = datetime.now() + timedelta(days=hari)
                break
            except ValueError:
                print("Input harus berupa angka!")
                lanjut = input("Coba lagi dengan jumlah hari lain? (y/n): ").lower()
                if lanjut != 'y':
                    print("Setup pelanggan dibatalkan.")
                    return
                continue

        data = {
            'token': token,
            'gmail': gmail,
            'channels': channels,
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        simpan_konfigurasi(nama_pelanggan, data)

        print(f"Konfigurasi pelanggan {nama_pelanggan} berhasil disimpan.")
        break

def hapus_pelanggan(nama_pelanggan):
    if os.path.exists(f'{nama_pelanggan}.json'):
        os.remove(f'{nama_pelanggan}.json')
        print(f"Konfigurasi pelanggan {nama_pelanggan} berhasil dihapus.")
    else:
        print(f"Tidak ditemukan konfigurasi untuk pelanggan {nama_pelanggan}.")

def update_tanggal_berakhir(nama_pelanggan):
    data = muat_konfigurasi(f'{nama_pelanggan}.json')
    if not data:
        print(f"Tidak ditemukan konfigurasi untuk pelanggan {nama_pelanggan}.")
        return

    # Tampilkan tanggal berakhir saat ini
    end_date_str = data.get('end_date')
    if end_date_str:
        try:
            current_end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
            print(f"Tanggal berakhir saat ini: {current_end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            print("Tanggal berakhir saat ini tidak valid.")

    while True:
        print("\nPilih opsi:")
        print("1. Tambah hari dari tanggal berakhir saat ini")
        print("2. Set tanggal berakhir baru")
        print("3. Kembali ke menu utama")
        
        pilihan = input("Pilih opsi (1-3): ")

        if pilihan == '1':
            # Tambah hari dari tanggal berakhir saat ini
            if not end_date_str:
                print("Tidak ada tanggal berakhir saat ini. Gunakan opsi 2 untuk set tanggal baru.")
                continue
                
            try:
                current_end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
                hari_input = input("Masukkan jumlah hari yang ingin ditambahkan: ").strip()
                hari = int(hari_input)
                if hari <= 0:
                    print("Jumlah hari harus lebih dari 0!")
                    continue
                
                new_end_date = current_end_date + timedelta(days=hari)
                data['end_date'] = new_end_date.strftime('%Y-%m-%d %H:%M:%S')
                simpan_konfigurasi(nama_pelanggan, data)
                print(f"Tanggal berakhir berhasil diperbarui: {new_end_date.strftime('%Y-%m-%d %H:%M:%S')}")
                break
                
            except ValueError:
                print("Input harus berupa angka!")
                continue

        elif pilihan == '2':
            # Set tanggal berakhir baru
            while True:
                hari_input = input("Masukkan jumlah hari dari sekarang: ").strip()
                try:
                    hari = int(hari_input)
                    if hari <= 0:
                        print("Jumlah hari harus lebih dari 0!")
                        continue
                    
                    new_end_date = datetime.now() + timedelta(days=hari)
                    data['end_date'] = new_end_date.strftime('%Y-%m-%d %H:%M:%S')
                    simpan_konfigurasi(nama_pelanggan, data)
                    print(f"Tanggal berakhir berhasil diperbarui: {new_end_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    break
                    
                except ValueError:
                    print("Input harus berupa angka!")
                    continue

        elif pilihan == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

def jalankan_bot(filename):
    last_sent = {}

    while True:
        data = muat_konfigurasi(filename)
        if not data:
            print(f"Konfigurasi {filename} tidak valid.")
            time.sleep(10)
            continue

        token = data.get('token')
        channels = data.get('channels', {})
        end_date_str = data.get('end_date')

        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S') if end_date_str else None
            if end_date and datetime.now() >= end_date:
                print("Masa berlaku habis. Bot berhenti.")
                return
        except Exception as e:
            print(f"Error parsing date: {e}")

        current_time = time.time()

        for channel_id in channels:
            if channel_id not in last_sent:
                last_sent[channel_id] = 0

        for channel_id, info in channels.items():
            cooldown = info.get('cooldown', 60)

            if (current_time - last_sent.get(channel_id, 0)) >= cooldown:
                success = send_message(token, channel_id, info.get('message', ''))
                if success:
                    last_sent[channel_id] = current_time
                    print(f"Menunggu 60 detik untuk channel berikutnya...")
                    time.sleep(60)
                else:
                    time.sleep(1)

        time.sleep(1)

def lihat_konfigurasi(filename):
    data = muat_konfigurasi(filename)
    if data:
        print(json.dumps(data, indent=4))
    else:
        print(f"Tidak ditemukan konfigurasi untuk file {filename}.")

def lihat_daftar_pelanggan():
    pelanggan_files = [f for f in os.listdir() if f.endswith('.json') and f != 'channels2.json']
    if pelanggan_files:
        print("Daftar pelanggan yang tersedia:")
        for file in pelanggan_files:
            data = muat_konfigurasi(file)
            if data:
                nama_pelanggan = file.replace('.json', '')
                token = data.get('token', 'Token tidak tersedia')
                gmail = data.get('gmail', 'Gmail tidak tersedia')
                jumlah_channel = len(data.get('channels', {}))
                end_date = data.get('end_date', 'Tanggal akhir tidak ditentukan')

                print(f"\nNama Pelanggan: {nama_pelanggan}")
                print(f"Token Discord: {token}")
                print(f"Gmail: {gmail}")
                print(f"Jumlah Channel: {jumlah_channel}")
                print(f"End Date: {end_date}")
            else:
                print(f"Tidak dapat memuat data untuk {nama_pelanggan}.")
    else:
        print("Tidak ada pelanggan yang ditemukan.")

def cari_pelanggan(nama_pelanggan):
    filename = f'{nama_pelanggan}.json'
    if os.path.exists(filename):
        data = muat_konfigurasi(filename)
        if data:
            print("\n--- Informasi Pelanggan ---")
            print(f"Nama Pelanggan: {nama_pelanggan}")
            print(f"Token Discord: {data.get('token', 'Token tidak tersedia')}")
            print(f"Gmail: {data.get('gmail', 'Gmail tidak tersedia')}")
            print(f"Jumlah Channel: {len(data.get('channels', {}))}")
            print(f"End Date: {data.get('end_date', 'Tanggal akhir tidak ditentukan')}")
        else:
            print(f"Tidak dapat memuat data untuk {nama_pelanggan}.")
    else:
        print(f"Tidak ditemukan konfigurasi untuk pelanggan {nama_pelanggan}.")

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

def lihat_tanggal_akhir():
    pelanggan_files = [f for f in os.listdir() if f.endswith('.json') and f != 'channels2.json']
    if pelanggan_files:
        print("Daftar tanggal akhir pelanggan:")
        for file in pelanggan_files:
            data = muat_konfigurasi(file)
            if data:
                nama_pelanggan = file.replace('.json', '')
                end_date = data.get('end_date', 'Tanggal akhir tidak ditentukan')
                print(f"\nNama Pelanggan: {nama_pelanggan}")
                print(f"End Date: {end_date}")
            else:
                print(f"Tidak dapat memuat data untuk {nama_pelanggan}.")
    else:
        print("Tidak ada pelanggan yang ditemukan.")

def menu():
    while True:
        print("\n--- SPAM Discord 24/7 ---")
        print("")
        print("1. Setup pelanggan baru")
        print("2. Lihat daftar pelanggan")
        print("3. Lihat konfigurasi pelanggan")
        print("4. Edit pesan pelanggan")
        print("5. Hapus pelanggan")
        print("6. Lihat tanggal akhir pelanggan")
        print("7. Update tanggal berakhir")
        print("8. Jalankan bot")
        print("9. Cek Token Discord")
        print("10. Cari pelanggan")
        print("11. Keluar")
        print("")
        print("--- Developed By Cygni ---")

        pilihan = input("Pilih opsi (1-11): ")

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
            nama_pelanggan = input("Masukkan nama pelanggan untuk update tanggal berakhir: ")
            update_tanggal_berakhir(nama_pelanggan)
        elif pilihan == '8':
            nama_pelanggan = input("Masukkan nama pelanggan untuk menjalankan bot: ")
            jalankan_bot(f'{nama_pelanggan}.json')
        elif pilihan == '9':
            cek_token_discord()
        elif pilihan == '10':
            nama_pelanggan = input("Masukkan nama pelanggan yang ingin dicari: ")
            cari_pelanggan(nama_pelanggan)
        elif pilihan == '11':
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