import os
import pickle
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Conv1D, Flatten, MaxPooling1D, Dropout, Activation

# input_dataframe: str of csv file path or dataframe
def load_and_scale_data_from_csv(input_dataframe):
    data = input_dataframe # default value is dataframe
    if type(input_dataframe) == str: # if input is csv file path then read data of csv file path
        data = pd.read_csv(input_dataframe) # read data file
    # dataset
    X = np.array(data.drop(['FilePath', 'legitimate'], axis=1).values, dtype=np.float32)
    y = np.array(data['legitimate'].values, dtype=np.float32) # np.float32 to use numpy.absolute
    y = np.array([np.absolute(y-1), y], dtype=np.int32).T # convert Y from vector to matrix
    m, n = X.shape
    # scale and export max/min data
    max_min_data_path = "max_min_data.lis"
    open(max_min_data_path, "ab").close() # create max/min data file if not exist
    with open(max_min_data_path, "rb") as max_min_import:
        max_min_data = [] # create first max/min data. 0: max, 1: min
        if os.fstat(max_min_import.fileno()).st_size>0: # if size of max/min file>0 then load it
            max_min_data = pickle.load(max_min_import)
        max_min_import.close()
    check_diff = 0
    for i in range(n):
        max_Xi = float(max(X[:, i]))
        min_Xi = float(min(X[:, i]))
        if len(max_min_data)==i:
            max_min_data.append([max_Xi, min_Xi])
            check_diff=1
        if max_Xi>max_min_data[i][0]: #update max data for max/min data
            max_min_data[i][0] = max_Xi
            check_diff=1
        else:
            max_Xi = max_min_data[i][0]
        if min_Xi<max_min_data[i][1]: #update min data for max/min data
            max_min_data[i][1] = min_Xi
            check_diff=1
        else:
            min_Xi = max_min_data[i][1]
        if max_Xi != min_Xi:
            X[:, i] = (X[:, i]-min_Xi)/(max_Xi-min_Xi) # scale data
        else:
            X[:, i] = 0
    if check_diff==1: # check if max/min is change then update it
        with open(max_min_data_path, "wb") as max_min_export:
            pickle.dump(max_min_data, max_min_export)
            max_min_export.close()
    X = X.reshape(m, n, 1)
    return X, y
# malware_csv_file_path: str of csv file path or dataframe
# malware/benign: 70/30
# batch_size: 512
def cnn(malware_csv_file_path, training_epochs, old_model=None):
    if not os.path.isdir("trained"):
        os.mkdir("trained")
    batch_size = 512 # setting batch size for model
    benign_csv_file_path = "dataset/legit.csv"
    X_malware, y_malware = load_and_scale_data_from_csv(malware_csv_file_path) # return X, y : numpy.array
    X_benign, y_benign = load_and_scale_data_from_csv(benign_csv_file_path) # return X, y : numpy.array
    m_malware = X_malware.shape[0]
    m_benign = X_benign.shape[0]
    if m_malware < int(batch_size*(7/10)):
        return "number of malware sample must more than "+str(int(batch_size*(7/10)))
    if float(m_malware/m_benign)<(7/3):
        frequency_m_benign_target = float(m_malware*(3/7)/m_benign)
        __, X_benign, ___, y_benign = train_test_split(X_benign, y_benign, test_size=frequency_m_benign_target, random_state=1)
    elif float(m_malware/m_benign)>(7/3):
        m_benign_target = int(m_malware*(3/7))
        divv = int(m_benign_target/m_benign)
        modd = m_benign_target%m_benign
        X_benign = np.array(list(X_benign)*divv, dtype=np.float32)
        y_benign = np.array(list(y_benign)*divv, dtype=np.int32)
        X_benign = np.array(np.concatenate((X_benign, X_benign[:modd]), axis=0), dtype=np.float32)
        y_benign = np.array(np.concatenate((y_benign, y_benign[:modd]), axis=0), dtype=np.int32)
    X = np.array(np.concatenate((X_malware, X_benign), axis=0), dtype=np.float32)
    y = np.array(np.concatenate((y_malware, y_benign), axis=0), dtype=np.int32)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.1, random_state=1)
    # model
    model = Sequential()
    model.add(Conv1D(64, 3, padding='same', input_shape=(X.shape[1:]), activation='relu'))
    model.add(Conv1D(64, 3, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.25))
    model.add(Conv1D(32, 3, padding='same', activation='relu'))
    model.add(Conv1D(32, 3, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(512, activation='sigmoid', kernel_initializer='normal'))
    model.add(Dense(512, activation='sigmoid', kernel_initializer='normal'))
    model.add(Dense(512, activation='sigmoid', kernel_initializer='normal'))
    model.add(Dropout(0.25))
    model.add(Dense(  2, activation='sigmoid', kernel_initializer='normal'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])
    # run/train model
    if old_model != None:
        model = load_model(old_model)
    modell = model.fit(X_train, y_train, epochs=int(training_epochs), validation_data=(X_test, y_test), shuffle=True, batch_size=batch_size, verbose=1)
    model.save("trained/model.h5")
    with open("model_history.lis", "ab") as model_history:
        pickle.dump(modell.history, model_history)
    return modell