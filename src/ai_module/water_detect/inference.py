import torch
import os
import json
import cv2
from pathlib import Path

class WaterDetector:
    def __init__(self, repo, model_path, model_condifence):
        # repo = os.path.join(os.getcwd(), "yolov5")
        self.model = torch.hub.load(repo, "custom", path=model_path, source="local")
        self.model.conf = float(model_condifence)

    def predict(self, image):
        try:
            # print('<debug> try predict...')
            results = self.model(image)
            # print('<debug> try predict2...')
            return json.loads(results.pandas().xyxy[0].to_json(orient="records"))
        except Exception as e:
            print(e)
            return None
    
    def get_image(self, image):
        results = self.model(image)
        return cv2.cvtColor(results.render()[0], cv2.COLOR_BGR2RGB)
    
    def save_image(self,save_dir, image):
        cv2.imwrite(save_dir, image)

if __name__ == "__main__":
    repo = '/home/yf/dev/w0405_agent/src/ai_module/water_detect/yolov5'
    model_path = "/home/yf/dev/w0405_agent/src/ai_module/water_detect/weights/best.pt"
    model_confidence = 0.7
    detector = WaterDetector(repo, model_path, model_confidence)
    img = "/home/yf/dev/w0405_agent/src/ai_module/water_detect/test_data/2024_01_31_16_04_38_6.0_1363.7398681640625_297.32073974609375.jpg"
    img_path = Path(img)
    data = detector.predict(img)

    print(type(data))

    if(len(data) == 0): print('haha')
    
    for water in data:
        print(water)

    result_img = detector.get_image(img)
    
    cv2.imshow("water-leakage-detect-result", result_img)
    detector.save_image(f'{img_path.stem}.jpg',result_img)
    cv2.waitKey(0)