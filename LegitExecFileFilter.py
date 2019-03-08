#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import shutil
import zipfile

# varriable folder name
exec_file_filter_folder="legit_exec_file_filter"
raw_data_path=exec_file_filter_folder+"/raw_data"
data_path="data/legitimate"
zip_path=exec_file_filter_folder+"/zip"
unzip_path=exec_file_filter_folder+"/unzip"

# check is created folder function
def CheckFolder():
    if os.path.isdir(exec_file_filter_folder)==0:
        os.mkdir(exec_file_filter_folder)
    if os.path.isdir(raw_data_path)==0:
        os.mkdir(raw_data_path)
    if os.path.isdir(zip_path)==0:
        os.mkdir(zip_path)
    if os.path.isdir(unzip_path)==0:
        os.mkdir(unzip_path)
    print("Checked folder")
    return

# filter file in folder
def FileFilter(dir):
    for file in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, file)): # check is folder
            FileFilter(os.path.join(dir, file))
        if file.endswith(".zip") or file.endswith(".cab") or file.endswith(".ZIP") or file.endswith(".CAB"): # check is zip file
            shutil.copyfile(os.path.join(dir, file), os.path.join(zip_path, file)) # copy file to zip_result folder
            print(os.path.join(dir, file))
        elif file.endswith(".dll") or file.endswith(".exe") or file.endswith(".DLL") or file.endswith(".EXE"): # check is exec file
            shutil.copyfile(os.path.join(dir, file), os.path.join(data_path, file)) # copy exec file to result folder
            print(os.path.join(dir, file))

# unzip file in folder
def ExtractFile(dir):
    for file in os.listdir(dir):
        try:
            ufile = zipfile.ZipFile(os.path.join(dir, file), 'r') # open file
            ufile.extractall(unzip_path) # unzip file
            print(os.path.join(dir, file)) # print file name
            ufile.close() # close file
        except:
            print("file error...")

# run
CheckFolder()
print("Fitlering data..................")
FileFilter(raw_data_path)
print("Extracting zip to unzip folder..")
ExtractFile(zip_path)
print("Filtering unzip folder..........")
FileFilter(unzip_path)
# remove zip and unzip folder
print("Remove zip folder")
shutil.rmtree(zip_path)
print("Remove unzip folder")
shutil.rmtree(unzip_path)
print("Done!")


# In[ ]:




