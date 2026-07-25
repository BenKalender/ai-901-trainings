import asyncio
import aiohttp
import os
from dotenv import load_dotenv
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

async def poll_video_status_async(video_id, session, max_retries=120, wait_seconds=5):
    """Polling: Video'nun status'unu kontrol et (completed olana kadar)"""
    url = f"{base_url}videos/{video_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    for attempt in range(max_retries):
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                print(f"Status: {response.status}")
                print(f"Response: {text}")
            
            response.raise_for_status()
            data = await response.json()
            status = data.get("status")
            
            print(f"[{attempt+1}/{max_retries}] {video_id}: {status}")
            
            if status == "completed":
                print(f"✓ Video is ready: {video_id}")
                return data
            elif status == "failed!":
                raise Exception(f"✗ Video {video_id} has failed!")
        
        await asyncio.sleep(wait_seconds)
    
    raise TimeoutError(f"✗ Video {video_id} timeout")

async def download_video_async(video_id, session, output_filename="output.mp4"):
    """Videoyu async olarak indir"""
    ensure_output_dir(output_dir)
    
    # Full path oluştur
    full_path = os.path.join(output_dir, output_filename)
    
    url = f"{base_url}videos/{video_id}/content?variant=video"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            text = await response.text()
            print(f"Status: {response.status}")
            print(f"Response: {text}")
        
        response.raise_for_status()
        
        # Videoyu dosyaya yaz
        with open(full_path, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                f.write(chunk)
    
    print(f"✓ Video has been downloaded: {full_path}")
    return full_path

async def generate_and_download_video_async(prompt, seconds="4", output_filename="output.mp4"):
    """
    Async: Job oluştur → Poll → İndir
    """
    async with aiohttp.ClientSession() as session:
        try:
            # 1. POST: Job oluştur
            create_url = f"{base_url}videos"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "sora-2",
                "prompt": prompt,
                "size": "1280x720",
                "seconds": seconds
            }
            
            async with session.post(create_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    print(f"Status: {response.status}")
                    print(f"Response: {text}")
                
                response.raise_for_status()
                data = await response.json()
                video_id = data["id"]
                print(f"✓ Job has been created: {video_id}")
            
            # 2. GET: Polling
            await poll_video_status_async(video_id, session)
            
            # 3. Download
            await download_video_async(video_id, session, output_filename)
            
            print(f"\n✓ Succeed! Video path: {os.path.join(output_dir, output_filename)}")
            
        except Exception as e:
            print(f"\n✗ Failure: {e}")
            raise

# KULLANIM - Tek video

prompt = "An old Tiger wandering near a lake just in front of a rainforest"
asyncio.run(generate_and_download_video_async(prompt, "4", "tiger_walk.mp4"))