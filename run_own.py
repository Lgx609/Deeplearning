import cv2
import torch
import os

# 1. 加载模型
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=False)
model.eval()
model = model.cuda() if torch.cuda.is_available() else model.cpu()

# 2. 打开视频
video_path = 'input.mp4'
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError("无法打开视频文件")

# 3. 逐帧处理
frame_id = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(rgb, size=640)
    detections = results.xyxy[0].cpu().numpy()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        label = f'{results.names[int(cls)]} {conf:.2f}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    out_path = os.path.join(output_dir, f'frame_{frame_id:06d}.jpg')
    cv2.imwrite(out_path, frame)
    frame_id += 1

cap.release()
print(f"处理完成，共保存 {frame_id} 张图片到 {output_dir}")