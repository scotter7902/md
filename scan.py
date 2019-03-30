import os
import sys
import training
import datetime
import numpy as np
import pandas as pd
from keras.models import load_model

# input command: scan_folder_path, [model_path]
if __name__ == '__main__':
    output_csv_path = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    folder_scan = sys.argv[1]
    folder_scan_items = len(training.get_file_list(folder_scan))
    print('scaning: '+folder_scan+' '+str(folder_scan_items)+' file(s)')
    training.create_data(folder_scan, 2, output_csv_path)

    # load model
    model = load_model(str(sys.argv[2]))
    data_scan = pd.read_csv(output_csv_path, sep=',')
    X_scan_data = np.asarray(data_scan.drop(['FilePath', 'legitimate'], axis=1).values)
    X_scan_file_name = np.asarray(data_scan['FilePath'].values)
    y_scan = np.round(model.predict(X_scan_data))
    results = {X_scan_file_name[i]: y_scan[i] for i in range(len(y_scan)) if y_scan[i] == 0}
    for keyy in results:
        print('-> malicious file path:', keyy)
    print('malicious files is detected:', str(len(results))+'/'+str(folder_scan_items))
    os.remove(output_csv_path)