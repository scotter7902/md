import os
import sys
import data
import numpy as np
import pandas as pd
from tkinter import filedialog, Tk
from tensorflow.keras.models import load_model

# input command: scan_folder_path, [model_path]
if __name__ == '__main__':
    # create Tk object
    root = Tk()
    root.withdraw()
    # choose deep learning model
    model_path = filedialog.askopenfilename(initialdir = "", title="choose deep learning model (cancel to choose default model)")
    if len(model_path) == 0:
        model = load_model("data.model")
    else:
        model = load_model(model_path)
    # choose folder for scanning
    folder_scan = filedialog.askdirectory(initialdir = "C:\\", title="choose folder for scanning")
    if len(folder_scan) == 0:
        print("you haven't choosen folder for scanning, the program will stop")
        exit()
    # extract data from the folder have choosen
    print("scanning foler: ", folder_scan)
    data_scan = np.array(data.create_data(folder_scan))
    m = data_scan[1:].shape[0]
    n = data_scan[1:].shape[1]
    # convert list to dataframe
    data_scan = pd.DataFrame(np.array(data_scan[1:]).reshape(m,n), columns = data_scan[0])
    # get dataset X
    X_scan_data = np.asarray(data_scan.drop(['FilePath', 'legitimate'], axis=1).values)
    X_scan_file_name = np.asarray(data_scan['FilePath'].values)
    # run deep learning classification to predict y
    y_scan = np.array(model.predict(X_scan_data))
    # print malicious data
    mali_results = [X_scan_file_name[i] for i in range(m) if y_scan[i, 0] == 1]
    for keyy in mali_results:
        print('-> malicious file path:', keyy)
    print('malicious files is detected:', str(len(mali_results))+'/'+str(m), 'pe file(s)')