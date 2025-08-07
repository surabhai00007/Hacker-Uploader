import os
import subprocess
import mmap
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import logging
import subprocess
import datetime
import asyncio
import os
import requests
import time
from p_bar import progress_bar
import aiohttp
import aiofiles
import tgcrypto
import concurrent.futures
from pyrogram.types import Message
from pyrogram import Client, filters
from pathlib import Path
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from pyrogram.enums import ParseMode

# Same AES Key aur IV jo encryption ke liye use kiya tha
KEY = b'^#^#&@*HDU@&@*()'
IV = b'^@%#&*NSHUE&$*#)'

# Decryption function
def dec_url(enc_url):
    enc_url = enc_url.replace("helper://", "")  # "helper://" prefix hatao
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted = unpad(cipher.decrypt(b64decode(enc_url)), AES.block_size)
    return decrypted.decode('utf-8')

# Function to split name & Encrypted URL properly
def split_name_enc_url(line):
    match = re.search(r"(helper://\S+)", line)  # Find helper:// ke baad ka encrypted URL
    if match:
        name = line[:match.start()].strip().rstrip(":")  # Encrypted URL se pehle ka text
        enc_url = match.group(1).strip()  # Sirf Encrypted URL
        return name, enc_url
    return line.strip(), None  # Agar encrypted URL nahi mila, to pura line name maan lo

# Function to decrypt file URLs
def decrypt_file_txt(input_file):
    output_file = "decrypted_" + input_file  # Output file ka naam

    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
        for line in f:
            name, enc_url = split_name_enc_url(line)  # Sahi tarike se name aur encrypted URL split karo
            if enc_url:
                dec = dec_url(enc_url)  # Decrypt URL
                out.write(f"{name}: {dec}\n")  # Ek hi : likho
            else:
                out.write(line.strip() + "\n")  # Agar encrypted URL nahi mila to line jaisa hai waisa likho

    return output_file  # Decrypted file ka naam return karega

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_mps_and_keys(api_url):
    response = requests.get(api_url)
    response_json = response.json()
    mpd = response_json.get('MPD')
    keys = response_json.get('KEYS')
    return mpd, keys

def exec(cmd):
        process = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.stdout.decode()
        print(output)
        return output
        #err = process.stdout.decode()
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        print("Waiting for tasks to complete")
        fut = executor.map(exec,cmds)
async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k


async def download(url,name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session: