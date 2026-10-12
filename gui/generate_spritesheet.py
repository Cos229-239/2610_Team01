from PIL import Image
import os

# Get absolute paths to check multiple possible asset locations
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Check both project root assets/ and gui/assets/
possible_asset_dirs = [
    os.path.join(project_root, "assets"),
    os.path.join(current_dir, "assets"),
    "assets"
]

assets_dir = None
for d in possible_asset_dirs:
    if os.path.exists(d) and any(f.endswith(".png") for f in os.listdir(d) if f != "zombie_spritesheet_v1.png"):
        assets_dir = d
        break

if not assets_dir:
    assets_dir = os.path.join(project_root, "assets") # Default fallback

print(f"Using assets directory: {assets_dir}")

# Create a 512x256 transparent RGBA image for the sprite sheet
width, height = 512, 256
sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))

bio_path = os.path.join(assets_dir, "biohazard_source.png")
skull_path = os.path.join(assets_dir, "skull_source.png")
zombie_path = os.path.join(assets_dir, "zombie_source.png")

# Fallback: grab any available PNGs if exact names aren't matched
if os.path.exists(assets_dir):
    all_files = sorted([f for f in os.listdir(assets_dir) if f.endswith(".png") and f != "zombie_spritesheet_v1.png"])
    print(f"Found PNGs: {all_files}")
    if all_files:
        if not os.path.exists(bio_path): bio_path = os.path.join(assets_dir, all_files[0])
        if not os.path.exists(skull_path): skull_path = os.path.join(assets_dir, all_files[min(1, len(all_files)-1)])
        if not os.path.exists(zombie_path): zombie_path = os.path.join(assets_dir, all_files[min(2, len(all_files)-1)])

try:
    bio_img = Image.open(bio_path).convert("RGBA")
    skull_img = Image.open(skull_path).convert("RGBA")
    zombie_img = Image.open(zombie_path).convert("RGBA")
    print("Successfully loaded source assets!")
except Exception as e:
    print(f"Error loading images: {e}")
    exit(1)

# --- 1. Large Biohazard Area (Top-Left 128x128) ---
bio_resized = bio_img.resize((120, 120), Image.Resampling.LANCZOS)
sheet.paste(bio_resized, (4, 4), bio_resized)

# --- 2. Status Skull Icon (Top area around x=130) ---
skull_small = skull_img.resize((32, 32), Image.Resampling.LANCZOS)
sheet.paste(skull_small, (135, 2), skull_small)

# --- 3. Zombie/Infected Row (y=130) ---
zombie_slots = [0, 64, 128, 192]
for x_offset in zombie_slots:
    zombie_resized = zombie_img.resize((32, 32), Image.Resampling.LANCZOS)
    sheet.paste(zombie_resized, (x_offset + 16, 130), zombie_resized)

# --- 4. Special Nodes (Router, Laptop, Patient Zero) ---
tech_slots = [
    (288, skull_small),
    (352, skull_small),
    (416, zombie_img.resize((32, 32), Image.Resampling.LANCZOS))
]

for x_offset, icon in tech_slots:
    sheet.paste(icon, (x_offset + 16, 130), icon)

# Save output atlas back to the active assets directory
os.makedirs(assets_dir, exist_ok=True)
output_path = os.path.join(assets_dir, "zombie_spritesheet_v1.png")
sheet.save(output_path, "PNG")
print(f"Sprite sheet successfully generated at: {output_path}")