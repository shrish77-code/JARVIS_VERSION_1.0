import asyncio
import os
from time import sleep
from dotenv import get_key
from PIL import Image
import requests
from bs4 import BeautifulSoup
import io

# =====================================================
# Setup directories
# =====================================================
os.makedirs("Data", exist_ok=True)
os.makedirs(r"Frontend/Files", exist_ok=True)

# =====================================================
# Function: Fetch FIRST image from Google/Bing
# =====================================================
def fetch_first_image(prompt: str):
    try:
        # Bing images search (works without API)
        search_url = f"https://www.bing.com/images/search?q={prompt.replace(' ', '+')}"
        
        print("Searching:", search_url)

        html = requests.get(search_url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Find image URLs
        img_tags = soup.find_all("img")

        for img in img_tags:
            src = img.get("src")
            if src and src.startswith("http"):
                print("Found Image:", src)

                img_data = requests.get(src, timeout=10).content
                return img_data

        print("No valid image found.")
        return None

    except Exception as e:
        print("Error fetching image:", e)
        return None

# =====================================================
# Show images after generation
# =====================================================
def open_images(prompt: str):
    safe = prompt.replace(" ", "-")

    for i in range(1, 5):
        path = f"Data/{safe}{i}.png"
        try:
            img = Image.open(path)
            print("Opening:", path)
            img.show()
            sleep(1)
        except:
            print("Unable to open:", path)

# =====================================================
# Generate 4 images by downloading the first Google result
# =====================================================
async def generate_images(prompt: str):
    print("Downloading first image for:", prompt)

    img_bytes = fetch_first_image(prompt)

    if not img_bytes:
        print("Image download failed.")
        return

    safe = prompt.replace(" ", "-")

    # Save image 4 times
    for i in range(1, 5):
        file_path = f"Data/{safe}{i}.png"
        with open(file_path, "wb") as f:
            f.write(img_bytes)

        print("Saved:", file_path)

    print("\nImages saved successfully!\n")

# =====================================================
# Wrapper
# =====================================================
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# =====================================================
# MAIN LOOP (same structure as your old ImageGeneration.py)
# =====================================================
DATA_PATH = r"Frontend/Files/ImageGeneration.data"

# Create file if not exists
if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w") as f:
        f.write("None,False")

print("Watching for image generation requests...")

while True:
    try:
        with open(DATA_PATH, "r") as f:
            text = f.read().strip()

        if "," not in text:
            sleep(1)
            continue

        prompt, status = text.split(",", 1)
        prompt = prompt.strip()
        status = status.strip()

        if status == "True":
            print("Generating images for prompt:", prompt)

            GenerateImages(prompt)

            # Reset flag
            with open(DATA_PATH, "w") as f:
                f.write(f"{prompt},False")

        sleep(1)

    except Exception as e:
        print("Error:", e)
        sleep(1)
