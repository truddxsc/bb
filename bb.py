from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string
import json
import base64
import os
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Variabel API Key AntiCaptcha
API_KEY = '8406681c0b91eef882ba9c7ea9e60cbe'

# Fungsi untuk generate nama acak
def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=7))

# Fungsi untuk mendapatkan kode verifikasi dari Gmail
def get_verification_code():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    # Load token.json untuk autentikasi
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    service = build('gmail', 'v1', credentials=creds)

    # Mengambil email dari Atlassian yang berisi kode verifikasi
    result = service.users().messages().list(userId='me', q='from:noreply@atlassian.com is:unread').execute()
    messages = result.get('messages', [])

    if not messages:
        print("Tidak ada email baru dari Atlassian.")
        return None
    
    # Membaca isi email dan mencari kode OTP
    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    msg_str = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    
    # Cari OTP yang biasanya berupa 6 digit angka
    otp_code = ''.join([x for x in msg_str if x.isdigit()][:6])
    return otp_code if len(otp_code) == 6 else None

# Fungsi untuk menyelesaikan reCAPTCHA dengan AntiCaptcha
def solve_recaptcha_anticaptcha(site_key, url):
    task_payload = {
        'clientKey': API_KEY,
        'task': {
            'type': 'NoCaptchaTaskProxyless',
            'websiteURL': url,
            'websiteKey': site_key
        }
    }
    
    # Memulai tugas reCAPTCHA
    task_response = requests.post('https://api.anti-captcha.com/createTask', json=task_payload).json()
    task_id = task_response['taskId']

    # Memeriksa status penyelesaian reCAPTCHA
    task_result_payload = {
        'clientKey': API_KEY,
        'taskId': task_id
    }
    while True:
        result = requests.post('https://api.anti-captcha.com/getTaskResult', json=task_result_payload).json()
        if result['status'] == 'ready':
            return result['solution']['gRecaptchaResponse']
        time.sleep(5)

# Fungsi utama untuk menjalankan otomatisasi
def automate_signup():
    # Konfigurasi ChromeDriver
    options = Options()
    driver = webdriver.Chrome(options=options)

    try:
        # Buka halaman sign-up Atlassian
        driver.get("https://id.atlassian.com/signup")
        time.sleep(10)

        # Generate email dan nama random
        random_name = generate_random_name()
        email = f"mr.platra13+{random_name}@butyusa.com"

        # Isi email dan tekan ENTER
        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys(email)
        email_input.send_keys(u'\ue007')  # Tekan ENTER
        time.sleep(10)

        # Cek apakah reCAPTCHA muncul
        try:
            site_key = driver.find_element(By.CSS_SELECTOR, ".g-recaptcha").get_attribute("data-sitekey")
            if site_key:
                print("reCAPTCHA ditemukan, memulai penyelesaian...")
                captcha_response = solve_recaptcha_anticaptcha(site_key, driver.current_url)
                driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_response}";')
                time.sleep(10)
        except Exception:
            print("Tidak ada reCAPTCHA yang muncul, melanjutkan proses...")

        # Klik tombol 'Sign up' jika tidak ada reCAPTCHA atau setelah CAPTCHA selesai
        signup_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signup-submit"))
        )
        signup_button.click()
        time.sleep(10)

        # Ambil kode OTP dari Gmail
        otp_code = get_verification_code()
        if otp_code:
            print(f"Kode verifikasi: {otp_code}")

            # Masukkan kode OTP
            for i, digit in enumerate(otp_code):
                otp_input = driver.find_element(By.CSS_SELECTOR, f'[data-testid="otp-input-index-{i}"]')
                otp_input.send_keys(digit)

            time.sleep(5)

        # Isi nama random
        name_input = driver.find_element(By.ID, "displayName-uid2")
        name_input.send_keys(random_name)

        # Isi password
        password_input = driver.find_element(By.ID, "password-uid3")
        password_input.send_keys("AyLevy123@")
        password_input.send_keys(u'\ue007')  # Tekan ENTER
        time.sleep(10)

        # Tampilkan email yang berhasil dibuat
        print(f"Email yang berhasil dibuat: {email}")

    finally:
        # Tutup browser
        driver.quit()

# Fungsi looping utama
def main_loop(n):
    for _ in range(n):
        automate_signup()

# Menjalankan program
if __name__ == "__main__":
    main_loop(1)  # Ubah angka ini untuk mengatur berapa kali loop dijalankan
