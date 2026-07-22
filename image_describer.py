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
    api_key=os.getenv("FOUNDRY_KEY"),
    base_url=os.getenv("ENDPOINT"),
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

image_path = "./assets/image-1.jpg"
base64_image = encode_image(image_path)


response = client.responses.create(
    model="gpt-5-mini", 
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What is in this image? Provide 3 bullet points."},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"}
            ],
        }
    ],
)

print(response.output_text)