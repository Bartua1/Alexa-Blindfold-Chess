import os
from PIL import Image

# Configuration
IMAGE_DIR = "/Users/bartua1/Documents/ProyectosGitHub/Alexa-Blindfold-Chess/privacyAndComplianceInterface/public/assets/images"
TARGETS = {
    "match.png": (1080, 1440),
    "puzzles.png": (1080, 1440),
    "squares.png": (1080, 1440),
    "background.png": (1920, 1080)
}

def process_images():
    print(f"Scanning directory: {IMAGE_DIR}")
    if not os.path.exists(IMAGE_DIR):
        print("Error: Directory not found.")
        return

    files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')]
    if not files:
        print("No .png files found.")
        return

    for filename in files:
        if filename in TARGETS:
            path = os.path.join(IMAGE_DIR, filename)
            try:
                with Image.open(path) as img:
                    orig_size = img.size
                    target_size = TARGETS[filename]
                    
                    print(f"\nProcessing {filename}:")
                    print(f"  Current Size: {orig_size[0]}x{orig_size[1]}")
                    print(f"  Target Size:  {target_size[0]}x{target_size[1]}")
                    
                    # Resize using LANCZOS for high quality
                    resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                    resized_img.save(path)
                    print(f"  Status: Successfully resized and overwritten.")
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
        else:
            print(f"\nSkipping {filename}: No target size defined.")

if __name__ == "__main__":
    try:
        import PIL
        process_images()
    except ImportError:
        print("Pillow (PIL) is not installed. Please install it with: pip install Pillow")
