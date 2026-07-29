import os
import time

from dotenv import load_dotenv
import requests

from env_utils import doublecheck_env


# Load environment variables from .env
load_dotenv()
# Check and print results
doublecheck_env(".env")

api_key=os.environ["FOUNDRY_KEY"]
base_url=os.environ["ENDPOINT"]
output_dir=os.environ["VIDEO_OUTPUT_DIR"]

# Output directory'sini kontrol et ve oluştur
def ensure_output_dir(output_dir):
    """Output directory'sinin var olduğundan emin ol, yoksa oluştur"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Output directory has been created: {output_dir}")

# 1. VIDEO JOB OLUŞTUR
def create_video_job(prompt, size="1280x720", seconds="4"):
    url = f"{base_url}videos"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
         #"api-key": api_key
    }
    
    payload = {
        "model": "sora-2",
        "prompt": prompt,
        "size": size,
        "seconds": seconds
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]  # Video ID'sini yanıttan al
    print(f"✓ Video job is created. ID: {video_id}")
    
    return video_id

# 2. JOB STATUSUNU POLL ET
def poll_video_status(video_id, max_retries=120, wait_seconds=5):
    """
    Status kontrol et. Completed olana kadar bekle.
    """
    url = f"{base_url}videos/{video_id}"
    
    headers = {
        "api-key": api_key
    }
    
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        status = data.get("status")  # "pending", "completed", "failed"
        
        print(f"[{attempt+1}/{max_retries}] Status: {status}")
        
        if status == "completed":
            print("✓ Video has been generated!")
            return data
        elif status == "failed":
            error_msg = data.get("error", "Error unknown")
            raise Exception(f"✗ Video generation has failed!: {error_msg}")
        
        time.sleep(wait_seconds)
    
    raise TimeoutError(f"✗ Timeout: Video could not be prepared in {max_retries*wait_seconds} seconds!")

# 3. VİDEOYU İNDİR
def download_video(video_id, output_filename="output.mp4"):
    """
    Tamamlanmış videoyu indir.
    """
    ensure_output_dir(output_dir)
    # Full path oluştur
    full_path = os.path.join(output_dir, output_filename)

    url = f"{base_url}videos/{video_id}/content?variant=video"
    
    headers = {
        "api-key": api_key
    }
    
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    
    with open(full_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"✓ Video has been downloaded: {full_path}")
    return full_path

# MAIN: TÜM SÜRECİ ÇALIŞTIR
def generate_and_download_video(prompt, output_filename="output.mp4"):
    """
    1. Job oluştur
    2. Status'u poll et (completed olana kadar)
    3. Videoyu indir
    """
    try:
        # Adım 1: Job başlat
        video_id = create_video_job(prompt)
        
        # Adım 2: Polling (statusu kontrol et)
        poll_video_status(video_id)
        
        # Adım 3: Videoyu indir
        path_to_video = download_video(video_id, output_filename)
        
        print(f"\n✓ Succeed! Video: {path_to_video}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


prompt = "A house-owned cat, walking nervously in a back alley of a street."
generate_and_download_video(prompt, "cat_video.mp4")