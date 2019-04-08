import os
import tqdm
import numpy as np
import pandas as pd
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.metrics import binary_accuracy
from tensorflow.keras.layers import Dense, Conv1D, Flatten, MaxPooling1D, Dropout, Activation

# dnn input: csv_file_path, training_epochs, output_model_path
def cnn(csv_file_path, training_epochs, output_model_path):
    # read data file
    data = pd.read_csv('data.csv', sep=',')
    # dataset
    X = np.array(data.drop(['FilePath', 'legitimate'], axis=1).values)
    y = np.array(data['legitimate'].values)
    y = np.array([np.absolute(y-1), y]).T
    n = X.shape[1]
    for i in range(X.shape[1]):
        temp = X[:, i]
        X[:, i] = (temp-min(temp))/(max(temp)-min(temp))
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # model
    model = Sequential()
    model.add(Conv1D(64,3, padding='same', input_shape=(X.shape[1:]), activation='relu'))
    model.add(Activation('relu'))
    model.add(Conv1D(32, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.25))
    model.add(Conv1D(64, 3, padding='same'))
    model.add(Activation('relu'))
    model.add(Conv1D(64, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('sigmoid'))
    model.add(Dense(512))
    model.add(Activation('sigmoid'))
    model.add(Dense(512))
    model.add(Activation('sigmoid'))
    model.add(Dense(2))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['binary_accuracy'])
    # run/train model
    model.fit(X, y, epochs=training_epochs, batch_size=32)
    #save model
    if os.path.isfile(output_model_path):
        os.remove(output_model_path)
    try:
        model.save(output_model_path)
        print('saved model to path: ', output_model_path)
    except:
        print('error when saving model to path: ', output_model_path)

