import torch
import os
import json
import cv2

class WaterDetector:
    def __init__(self, repo, model_path, model_condifence):
        # repo = os.path.join(os.getcwd(), "yolov5")
        self.model = torch.hub.load(repo, "custom", path=model_path, source="local")
        self.model.conf = model_condifence

    def predict(self, image):
        try:
            results = self.model(image)
            return json.loads(results.pandas().xyxy[0].to_json(orient="records"))
        except:
            return None
    
    def get_image(self, image):
        results = self.model(image)
        return cv2.cvtColor(results.render()[0], cv2.COLOR_BGR2RGB)
    
    def save_image(self,save_dir, image):
        cv2.imwrite(save_dir, image)

if __name__ == "__main__":
    repo = 'yolov5'
    model_path = "weights/best.pt"
    model_confidence = 0.7
    detector = WaterDetector(repo, model_path, model_confidence)
    img = "/home/nw/Documents/GitHub/w0405_agent/src/../data/water-leakage/thermal-image/20231127/268/2023_11_27_14_35_03_5.0_1306.916015625_274.3580322265625.jpg"
    data = detector.predict(img)

    print(type(data))

    if(len(data) == 0): print('haha')
    
    for water in data:
        print(water)
    
    cv2.imshow("bus", detector.get_image(img))
    cv2.waitKey(0)