import os # system call
import shutil # copy file
import zipfile # unzip file
import hashlib # get md5 of string
import pefile # open PE file
import check # counting files in folder tree

# parameter:
#   dir: directory path (root)
#   type: 1 -> legitimate, 2 -> malicious
#   boolroot: 1 -> root directory, 0 -> is not root directory
#   pro_: n_th processing file
#   sum_: number of all files in the root folder
def filter(dir, type, boolroot=1, pro_=0, sum_=0):
    if boolroot == 1:
        pro_ = 0
        sum_ = check.len_(dir)

    print('checking folder: '+dir)
    if os.path.isdir(dir):
        for file in os.listdir(str(dir)):
            pfile = '/'.join([dir, file])
            pfilemd5 = hashlib.md5(pfile.encode('utf-8')).hexdigest()
            print('- checking file: '+pfile, end=' ')
            if os.path.isdir(pfile):
                print('[folder]')
                pro_ = filter(pfile, type, 0, pro_, sum_)
            else:
                pro_ = pro_+1
                try:
                    ofile = pefile.PE(pfile)
                    print('[pe]'+'['+str(pro_)+'/'+str(sum_)+']')
                except:
                    print('[orther format]'+str(pro_)+'/'+str(sum_)+']')
                    continue
                print('-> copy file to '+check.fols[type], end=' ')
                try:
                    shutil.copyfile(pfile, '/'.join([check.fols[type], pfilemd5]))
                    print('[done]')
                except:
                    print('[error]')
                ofile.close()
    if boolroot == 0:
        return pro_
    if boolroot == 1:
        print('- done')