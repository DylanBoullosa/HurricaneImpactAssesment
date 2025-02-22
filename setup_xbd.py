import torch
import os
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms
from tqdm import tqdm

# Define paths
MODEL_PATH = "xview2_model.pth"
INPUT_FOLDER = "path_to_images/"
OUTPUT_FOLDER = "results/"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load the pre-trained xBD model
print("📥 Loading model...")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file '{MODEL_PATH}' not found!")

model = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# Damage classification labels
DAMAGE_LABELS = {0: "No Damage", 1: "Minor", 2: "Moderate", 3: "Severe", 4: "Destroyed"}

# Function to predict damage
def predict_damage(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)
        prediction = torch.argmax(output, dim=1).item()

    return DAMAGE_LABELS.get(prediction, "Unknown")

# Function to label and save images
def label_image(image_path, label, output_name):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Set font size
    font_size = max(20, image.size[0] // 15)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Position for the text
    text_position = (10, 10)
    text_color = "red" if label in ["Severe", "Destroyed"] else "blue"

    # Add label to image
    draw.text(text_position, f"Damage: {label}", fill=text_color, font=font)

    # Save labeled image
    labeled_path = os.path.join(OUTPUT_FOLDER, output_name)
    image.save(labeled_path)
    print(f"📸 Labeled image saved: {labeled_path}")

# Process Before/After image pairs
print("🔍 Running predictions on Before/After image pairs...")

image_pairs = [
    ("house1_before.jpg", "house1_after.jpg"),
    ("house2_before.jpg", "house2_after.jpg"),
    ("house3_before.jpg", "house3_after.jpg"),
]

for before, after in tqdm(image_pairs, desc="Processing Image Pairs"):
    before_path = os.path.join(INPUT_FOLDER, before)
    after_path = os.path.join(INPUT_FOLDER, after)

    if os.path.exists(before_path) and os.path.exists(after_path):
        before_label = predict_damage(before_path)
        after_label = predict_damage(after_path)

        print(f"🏠 {before} → Damage: {before_label}")
        print(f"🏠 {after} → Damage: {after_label}")

        # Save labeled images
        label_image(before_path, before_label, f"labeled_{before}")
        label_image(after_path, after_label, f"labeled_{after}")

        # Save results as text
        result_text = f"{before}: {before_label}\n{after}: {after_label}\n"
        result_file = os.path.join(OUTPUT_FOLDER, f"{before}_vs_{after}_results.txt")
        with open(result_file, "w") as f:
            f.write(result_text)
        print(f"📄 Results saved: {result_file}")

    else:
        print(f"⚠️ Missing files: {before} or {after}, skipping pair.")

print("🎉 All predictions completed!")