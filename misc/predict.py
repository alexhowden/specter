import os
from ultralytics import YOLO

model = YOLO("models/yolo11_state.pt")
image_folder = "state_model/val/images"

for img_name in os.listdir(image_folder):
    img_path = os.path.join(image_folder, img_name)
    model.predict(source=img_path, save=True, line_width=3)
