#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

# define varriable in dictionary
data_folders = {
    'data' : 'data',
    'raw_data' : 'raw_data'
}
data_folders.update({
    'legitimate' : '/'.join([data_folders['data'], 'legitimate']),
    'malicious' : '/'.join([data_folders['data'], 'malicious']),
    'raw_legitimate' : '/'.join([data_folders['raw_data'], 'legitimate']),
    'raw_malicious' : '/'.join([data_folders['raw_data'], 'malicious']),
})

def length_dir(dir_path):
    count = 0
    for file in os.listdir(dir_path):
        file_path = '/'.join([dir_path, file])
        if os.path.isdir(file_path):
            count=count+length_dir(file_path)
        elif os.path.isfile(file_path):
            count=count+1
    return count

# run
print('number of data files...')
for folder in data_folders:
    print('    '+data_folders[folder]+': ...', end='')
    print(length_dir(data_folders[folder]))


# In[ ]:




