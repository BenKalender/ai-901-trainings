import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from env_utils import doublecheck_env

# Load environment variables from .env
load_dotenv()
# Check and print results
doublecheck_env(".env")

client = OpenAI(
    api_key=os.environ["FOUNDRY_KEY"],
    base_url=os.environ["ENDPOINT"],
)

prompt = "A modern flat illustration of a robot holding a potted plant, clean vector style, pastel colors."

img = client.images.generate(
    model="gpt-image-1-mini",
    prompt=prompt,
    n=1,
    size="1024x1024",
)

image_bytes = base64.b64decode(img.data[0].b64_json)
with open("foundry_generated.png", "wb") as f:
    f.write(image_bytes)

print("Saved: foundry_generated.png")


####################
