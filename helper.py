# full_helper.py
import os
import zipfile
import shutil
import subprocess
import aiofiles
import aiohttp
import logging
from Crypto.Cipher import AES

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AES KEY और IV को env से लेंगे (Render या .env से)
AES_KEY = os.getenv("AES_KEY", "0000000000000000").encode()
AES_IV = os.getenv("AES_IV", "0000000000000000").encode()


def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"✅ ZIP extracted to: {extract_to}")
    except Exception as e:
        logger.error(f"❌ Failed to extract zip: {e}")


def decrypt_file(input_path, output_path):
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        decrypted = cipher.decrypt(encrypted)
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        logger.info(f"🔓 Decrypted file: {input_path}")
    except Exception as e:
        logger.error(f"❌ Failed to decrypt file: {e}")


def merge_ts_to_mp4(ts_dir, output_path):
    try:
        ts_files = sorted(f for f in os.listdir(ts_dir) if f.endswith('.ts'))
        if not ts_files:
            logger.warning("⚠️ No TS files found to merge.")
            return False

        list_file = os.path.join(ts_dir, "ts_list.txt")
        with open(list_file, 'w') as f:
            for ts in ts_files:
                f.write(f"file '{os.path.join(ts_dir, ts)}'\n")

        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", list_file, "-c", "copy", output_path
        ]
        subprocess.run(cmd, check=True)
        logger.info(f"🎬 Merged to MP4: {output_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Merge failed: {e}")
        return False


async def download_file(session, url, save_path):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(save_path, 'wb') as f:
                    await f.write(await resp.read())
                logger.info(f"⬇️ Downloaded file: {save_path}")
                return save_path
            else:
                logger.error(f"❌ HTTP Error {resp.status} for {url}")
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
    return None


async def process_zip_from_url(zip_url, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    temp_zip = os.path.join(output_dir, "temp.zip")

    async with aiohttp.ClientSession() as session:
        downloaded = await download_file(session, zip_url, temp_zip)
        if not downloaded:
            return None

    extracted_dir = os.path.join(output_dir, "unzipped")
    os.makedirs(extracted_dir, exist_ok=True)

    extract_zip(temp_zip, extracted_dir)

    # Optional decryption loop
    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(".ts.enc"):
                enc_path = os.path.join(root, file)
                dec_path = os.path.join(root, file.replace(".enc", ""))
                decrypt_file(enc_path, dec_path)
                os.remove(enc_path)

    final_video = os.path.join(output_dir, "merged_output.mp4")
    merged = merge_ts_to_mp4(extracted_dir, final_video)

    os.remove(temp_zip)
    shutil.rmtree(extracted_dir, ignore_errors=True)

    return final_video if merged else None