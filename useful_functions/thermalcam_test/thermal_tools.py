import os
import cv2
from pathlib import Path

def gray_to_heatmap(img_dir, save_dir):
    gray = cv2.imread(img_dir, cv2.IMREAD_GRAYSCALE)
    cv2.normalize(gray, gray, 0, 255, cv2.NORM_MINMAX)
    heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
    # filepath = filepath.replace("gray", "rainbow")
    cv2.imwrite(save_dir, heatmap)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # return filepath

if __name__ == '__main__':

    # filepath = '/home/yf/dev/w0405_agent/useful_functions/thermalcam_test/data/2023_12_21_16_46_37_6.0_1000.4639282226562_307.5269775390625.jpg'
    # gray_to_heatmap(filepath)

    # Iterate over file in directory
    data_dir = './data'
    data_path = Path(data_dir)

    # save_path = data_path.parent
    # print(save_path)

    for file_path in data_path.rglob("*"):
        
        if(file_path.suffix == '.jpg'):
    
            directory, filename = os.path.split(str(file_path))
            new_directory = os.path.join(directory.replace('training data - rev01', 'training data - rev01 - processed'))
            new_path = os.path.join(new_directory, filename)

            save_path = Path(new_path)
            gray_to_heatmap(str(file_path), str(save_path))
        

