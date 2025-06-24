from ultralytics import YOLO

model = YOLO("models/YOLO11m-seg.pt")

model.train(
    data="models/dataset_attack.yaml", 
    imgsz=640, 
    batch=8, 
    epochs=100, 
    workers=1, 
    device="cpu"
    )
