import os
from AudioUtils import AudioUtils
import tensorflow as tf
import numpy as np
import json
from sklearn.neighbors import KernelDensity
import configparser 

class AnomalyDetector:
    def __init__(self, config):

        BASE_PATH = os.getcwd()

        # # Read config
        # config_file = os.path.join(BASE_PATH, "anomaly_detector_config.json")
        # with open(config_file, "r") as f:
        #     self.config = json.load(f)

        # self.config = self.load_config('cfg/config.properties')
        # ae_config_path = self.config.get('AUTOENCODER_CONF', 'path')
        # with open(ae_config_path, "r") as f:
        #     self.ae_config = json.load(f)

        self.config = config 
        ae_config_path = self.config.get('AUTOENCODER_CONF', 'path')
        with open(ae_config_path, "r") as f:
            self.ae_config = json.load(f)

    def update_test_data_dir(self, test_data_dir):
        self.test_data_dir = test_data_dir
        pass

    def import_test_data(self, file_name_list, test_data_path):
        ab_x, ab_x_names = [], []
        for file_name in file_name_list:
            file_path = os.path.join(test_data_path, file_name)
            audio = AudioUtils()
            spectrogram, _ = audio.preprocess(file_path, "")
            ab_x.append(spectrogram)
            ab_x_names.append(file_name)

        ab_x = np.array(ab_x)
        ab_x_names = np.array(ab_x_names)
        return ab_x, ab_x_names 


    def inference_classifier(self):
        # BASE_PATH = os.getcwd()
        # MODEL_PATH = os.path.join(BASE_PATH, "model")
        # self.classifier_path = os.path.join(MODEL_PATH, "classifier", "1")
        self.classifier_path = self.config.get('MODEL_PATH', 'classifier')

        # Load model
        self.classifier = tf.keras.models.load_model(self.classifier_path)

        # Process data
        ab_x, ab_x_names = self.import_test_data(os.listdir(self.test_data_dir), self.test_data_dir)
        
        # Prediction
        ambient, door, vocal, noclass = [], [], [], []
        for i, data in enumerate(ab_x):
            predictions = self.classifier([data])
            pred_class = np.argmax(predictions[0])

            # print("class:", pred_class, predictions[0][pred_class], predictions[0])

            if (predictions[0][pred_class] < 0.8):
                pred_class = -1

            if pred_class == 0: ambient.append(ab_x_names[i]) 
            elif pred_class == 1: vocal.append(ab_x_names[i])
            elif pred_class == 2: door.append(ab_x_names[i])
            else: noclass.append(ab_x_names[i])

        # Output results to json file
        out_dict = {
            "ambient": ambient,
            "vocal": vocal,
            "door": door,
            "no class": noclass
        }
        out_file = self.config.get('RESULT_PATH', 'classifier')
        with open(out_file, "w") as f:
            json.dump(out_dict, f, indent=4)


    def inference_detector(self, target_class):
        # BASE_PATH = os.getcwd()
        # MODEL_PATH = os.path.join(BASE_PATH, "model")

        self.density_threshold = self.ae_config[target_class]["density_threshold"]
        self.reconstruction_error_threshold = self.ae_config[target_class]["reconstruction_error_threshold"]
        self.out_vector_shape = self.ae_config[target_class]["out_vector_shape"]
        self.encoded_images_vector = self.ae_config[target_class]["encoded_images_vector"]
        self.kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(self.encoded_images_vector)

        # self.detector_path = os.path.join(MODEL_PATH, "anomalydetector", target_class, "1")
        self.detector_path = self.config.get('MODEL_PATH', target_class)

        # Load model
        self.detector = tf.keras.models.load_model(self.detector_path)
        self.detector.summary()

        # Get prediction results
        with open(self.config.get('RESULT_PATH', 'classifier'), "r") as f:
            preds = json.load(f)

        test_data_files = preds[target_class]

        # Process data
        ab_x, ab_x_names = self.import_test_data(test_data_files, self.test_data_dir)
        
        # check anomaly
        normal_list, abnormal_list = [], []
        for i, data in enumerate(ab_x):
            if self.check_anomaly(data, self.density_threshold, 
                        self.reconstruction_error_threshold, self.kde, self.out_vector_shape, 
                        self.detector):
                abnormal_list.append(ab_x_names[i])
            else: normal_list.append(ab_x_names[i])
        
        # Output results to json file
        out_dict = {
            "abnormal": abnormal_list,
            "normal": normal_list,
        }
        out_file = self.config.get('RESULT_PATH', target_class)
        with open(out_file, "w") as f:
            json.dump(out_dict, f, indent=4)

        print(f'[AnomalyDetector.inference_detector] class {target_class}: inference process finished!')


    def check_anomaly(self, img, density_threshold, reconstruction_error_threshold,
                  kde, out_vector_shape, model):
    
        density_threshold = density_threshold
        reconstruction_error_threshold = reconstruction_error_threshold

        img = img[np.newaxis, :,:,:]
        encoded_image = model.encoder([[img]]).numpy()

        encoded_image = [np.reshape(e_img, (out_vector_shape)) for e_img in encoded_image]

        density = kde.score_samples(encoded_image)[0] # get a density score for the new image
        reconstruction = model(img)
        reconstruction_error = model.evaluate(reconstruction,img, batch_size = 1)[0]
        
        if density < density_threshold: #or reconstruction_error > reconstruction_error_threshold:
            # print(file_name, "The audio is an anomaly")
            return True
            
        else:
            # print(file_name, "The audio is NOT an anomaly")
            return False

    

       

if __name__ == "__main__":

    config = configparser.ConfigParser()
    try:
        config.read('cfg/config.properties')
    except:
        print("Error loading properties file, check the correct directory")

    detector = AnomalyDetector(config)
    detector.update_test_data_dir(config.get("RECORDING", 'chunk_path'))
    detector.inference_classifier()
    detector.inference_detector("ambient")
    detector.inference_detector("vocal")
    detector.inference_detector("door")