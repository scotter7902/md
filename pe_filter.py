#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import library
import os # system call
import shutil # copy file
import zipfile # unzip file
import hashlib # get md5 of string
import pefile # open PE file

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
iteration = -1
count = 0
# check if created folder function
def check_data_folders():
    print('checking data folders...')
    for folder in data_folders:
        if not os.path.isdir(data_folders[folder]):
            print('creating path: '+data_folders[folder]+'...', end='')
            try:
                os.mkdir(data_folders[folder])
                print('done.')
            except:
                print('error.')
                exit()
    print('check data folders done.')
# unzip function
def unzip_file(file_path, file_path_md5):
    try:
        file = zipfile.ZipFile(file_path, 'r') # open zip file
    except:
        return 0, 'cannot open zip file: '
    unzip_path = '/'.join([os.path.dirname(file_path), file_path_md5]) # get the unzip path
    print('unzipping file: '+unzip_path+'...', end='')
    try:
        file.extractall(unzip_path) # unzip file
    except:
        return 0, 'error.'
    file.close() # close file
    return 1, unzip_path

# filter file in folder
def pe_filter(dir_path):
    global count
    global iteration
    print('filtering PE files in folder: '+dir_path+'...')
    if os.path.isdir(dir_path): # check if folder
        for file in os.listdir(dir_path): # loop each file in dir_path
            if iteration > 0 and count >= iteration:
                return
            file_path = '/'.join([dir_path, file]) # get file path
            file_path_md5 = hashlib.md5(file_path.encode('utf-8')).hexdigest() # get the md5 hash of file_path
            print('checking file: '+file_path+'...', end='')
            if os.path.isdir(file_path): # check if folder
                print('is folder.')
                pe_filter(file_path) # if file_path is folder then using pe_filter for file_path
            elif zipfile.is_zipfile(file_path): # check if zip file
                print('is zip file.')
                print('unzipping file: '+file_path+'...', end='')
                unzip_file_result, unzip_file_log = unzip_file(file_path, file_path_md5) # if file_path is zip file the using unzip_file for file_path
                if unzip_file_result == 1: # if unzip file successfully
                    print("unzipped.")
                    pe_filter(unzip_file_log) # filter folder just unzipped
                    shutil.rmtree(unzip_file_log, ignore_errors=True) # remove folder just unzipped
                    print("removed folder: "+unzip_file_log)
            else:
                try:
                    file_pe = pefile.PE(file_path) # try to open file
                    print('is PE file.', end='')
                except: # if not pe file
                    print('orther format.', end='')
                    print('deleting file...', end='')
                    try:
                        os.remove(file_path) # remove file after be checked
                        print('done.')
                    except:
                        print('error.')
                    continue
                if dir_path.find(data_folders['legitimate'])>=0: # check if file is in raw_data/legitimate folder
                    print('copying file to '+data_folders['legitimate']+'...', end='')
                    try:
                        shutil.copyfile(file_path, '/'.join([data_folders['legitimate'], file_path_md5])) # copy file to raw_data/legitimate folder and rename it to file_path_md5
                        print('done.', end='')
                        count = count+1
                    except:
                        print('error.', end='')
                elif dir_path.find(data_folders['malicious'])>=0: # check if file is in raw_data/malicious folder
                    print('copying file to '+data_folders['malicious']+'...', end='')
                    try:
                        shutil.copyfile(file_path, '/'.join([data_folders['malicious'], file_path_md5])) # copy file to raw_data/malicious folder and rename it to file_path_md5
                        print('done.', end='')
                        count = count+1
                    except:
                        print('error.', end='')
                file_pe.close() # close PE file
                print('deleting file...', end='')
                try:
                    os.remove(file_path) # remove file after be checked
                    print('done.')
                except:
                    print('error.')
# run
check_data_folders() # check data folders
pe_filter(data_folders['raw_data']) # filter PE files in raw_data folder
print("done!")