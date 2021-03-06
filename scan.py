import os
import sys
import cnn
import data
import glob
import pickle
import numpy as np
import pandas as pd
from tkinter import filedialog, Tk
from tensorflow.keras.models import load_model

# input command: 0: scan folder, 1: scan file
if __name__ == '__main__':
    # create Tk object
    root = Tk()
    root.withdraw()
    model = load_model("trained/model.h5") # load model with highest accuracy
    if int(sys.argv[1]) == 0: # if scan folder
        scan_path = filedialog.askdirectory(initialdir = "C:\\", title="choose folder for scanning")
    elif int(sys.argv[1]) == 1: # if scan file
        scan_path = filedialog.askopenfilename(initialdir = "C:\\", title="choose file for scanning")
    if len(scan_path) == 0:
        print("you haven't choosen path for scanning, the program will stop")
        exit()
    print()
    # extract data from the folder have choosen
    print("scanning: ", scan_path)
    data_scan, columns = data.create_data(scan_path)
    data_scan = np.array(data_scan)
    if data_scan.shape[0] == 0: # check if no PE be found
        print("not found PE file. the program will stop")
        exit()
    m, n = data_scan.shape # get shape length of data_scan
    data_scan = pd.DataFrame(data_scan, columns=columns) # convert list to dataframe
    X_scan_file_name = np.array(data_scan['FilePath'].values) # get scanning files name
    X_scan_data, __ = cnn.load_and_scale_data_from_csv(data_scan)
    y_scan = np.array(model.predict(X_scan_data)) # run deep learning classification to predict y
    print()
    # print malicious data
    mali_results = [X_scan_file_name[i] for i in range(m) if y_scan[i, 0] == max(y_scan[i])]
    for keyy in mali_results:
        print('-> malicious file path:', keyy)
    print()
    print('malicious files is detected:', str(len(mali_results))+'/'+str(m), 'pe file(s)')