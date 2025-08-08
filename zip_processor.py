import os
import zipfile
import subprocess
from pathlib import Path
import shutil

def extract_zip(zip_path, extract_to):
    """Unzip the given file to the target directory."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    print(f"📂 Extracting ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ Extracted to: {extract_to}")
    return extract_to


def merge_ts_files(ts_folder, output_mp4):
    """Merge all TS files in folder into a single MP4."""
    ts_files = sorted(Path(ts_folder).glob("*.ts"))
    if not ts_files:
        raise FileNotFoundError("No .ts files found for merging.")

    list_file = Path(ts_folder) / "file_list.txt"
    with open(list_file, "w") as f:
        for ts in ts_files:
            f.write(f"file '{ts.resolve()}'\n")

    cmd = f"ffmpeg -f concat -safe 0 -i '{list_file}' -c copy '{output_mp4}'"
    print(f"🎬 Merging {len(ts_files)} TS files into {output_mp4}")
    subprocess.run(cmd, shell=True, check=True)
    print(f"✅ MP4 created: {output_mp4}")

    os.remove(list_file)
    return output_mp4


def process_zip(zip_path, output_folder):
    """Full process: unzip, detect file type, and process accordingly."""
    temp_dir = Path(output_folder) / "temp_extract"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract
    extract_zip(zip_path, temp_dir)

    # Step 2: Detect file types
    ts_files = list(Path(temp_dir).glob("*.ts"))
    pdf_files = list(Path(temp_dir).glob("*.pdf"))

    if ts_files:
        output_mp4 = Path(output_folder) / "merged_video.mp4"
        return merge_ts_files(temp_dir, output_mp4)

    elif pdf_files:
        pdf_path = Path(output_folder) / pdf_files[0].name
        shutil.move(str(pdf_files[0]), pdf_path)
        print(f"📄 PDF file extracted: {pdf_path}")
        return pdf_path

    else:
        print("⚠️ No TS or PDF found. Extracted files are in temp folder.")
        return temp_dir


if __name__ == "__main__":
    # Example usage
    zip_file = "sample.zip"  # Replace with your ZIP file path
    output_dir = "output"

    try:
        result = process_zip(zip_file, output_dir)
        print(f"✅ Processing complete. Output: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")