import os
import sys
import tqdm
import glob
import math
import array
import pefile
import pandas as pd

# create data input: raw_data_path, [data_type, [output_csv_file_path]]
def get_entropy(data):
    if len(data) == 0:
        return 0.0
    occurences = array.array('L', [0]*256)
    for x in data:
        occurences[x if isinstance(x, int) else ord(x)] += 1
    entropy = 0
    for x in occurences:
        if x:
            p_x = float(x)/len(data)
            entropy -= p_x*math.log(p_x, 2)
    return entropy
def get_resources(pe):
    resources = []
    if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
        try:
            for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                if hasattr(resource_type, 'directory'):
                    for resource_id in resource_type.directory.entries:
                        if hasattr(resource_id, 'directory'):
                            for resource_lang in resource_id.directory.entries:
                                data = pe.get_data(resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size)
                                size = resource_lang.data.struct.Size
                                entropy = get_entropy(data)
                                resources.append([entropy, size])
        except Exception as e:
            return resources
    return resources
def get_version_info(pe):
    res = {}
    for fileinfo in pe.FileInfo[0]:
        if fileinfo.Key == b'StringFileInfo':
            for st in fileinfo.StringTable:
                for entry in st.entries.items():
                    res[entry[0]] = entry[1]
        if fileinfo.Key == b'VarFileInfo':
            for var in fileinfo.Var:
                res[list(var.entry.items())[0][0]] = list(var.entry.items())[0][1]
    if hasattr(pe, 'VS_FIXEDFILEINFO'):
        res['flags'] = pe.VS_FIXEDFILEINFO[0].FileFlags
        res['os'] = pe.VS_FIXEDFILEINFO[0].FileOS
        res['type'] = pe.VS_FIXEDFILEINFO[0].FileType
        res['file_version'] = pe.VS_FIXEDFILEINFO[0].FileVersionLS
        res['product_version'] = pe.VS_FIXEDFILEINFO[0].ProductVersionLS
        res['signature'] = pe.VS_FIXEDFILEINFO[0].Signature
        res['struct_version'] = pe.VS_FIXEDFILEINFO[0].StrucVersion
    return res
def extract_infos(fpath):
    res = []
    pe = pefile.PE(fpath)
    res.append(str(fpath))
    res.append(pe.FILE_HEADER.Machine)
    res.append(pe.FILE_HEADER.SizeOfOptionalHeader)
    res.append(pe.FILE_HEADER.Characteristics)
    res.append(pe.OPTIONAL_HEADER.MajorLinkerVersion)
    res.append(pe.OPTIONAL_HEADER.MinorLinkerVersion)
    res.append(pe.OPTIONAL_HEADER.SizeOfCode)
    res.append(pe.OPTIONAL_HEADER.SizeOfInitializedData)
    res.append(pe.OPTIONAL_HEADER.SizeOfUninitializedData)
    res.append(pe.OPTIONAL_HEADER.AddressOfEntryPoint)
    res.append(pe.OPTIONAL_HEADER.BaseOfCode)
    try:
        res.append(pe.OPTIONAL_HEADER.BaseOfData)
    except AttributeError:
        res.append(0)
    res.append(pe.OPTIONAL_HEADER.ImageBase)
    res.append(pe.OPTIONAL_HEADER.SectionAlignment)
    res.append(pe.OPTIONAL_HEADER.FileAlignment)
    res.append(pe.OPTIONAL_HEADER.MajorOperatingSystemVersion)
    res.append(pe.OPTIONAL_HEADER.MinorOperatingSystemVersion)
    res.append(pe.OPTIONAL_HEADER.MajorImageVersion)
    res.append(pe.OPTIONAL_HEADER.MinorImageVersion)
    res.append(pe.OPTIONAL_HEADER.MajorSubsystemVersion)
    res.append(pe.OPTIONAL_HEADER.MinorSubsystemVersion)
    res.append(pe.OPTIONAL_HEADER.SizeOfImage)
    res.append(pe.OPTIONAL_HEADER.SizeOfHeaders)
    res.append(pe.OPTIONAL_HEADER.CheckSum)
    res.append(pe.OPTIONAL_HEADER.Subsystem)
    res.append(pe.OPTIONAL_HEADER.DllCharacteristics)
    res.append(pe.OPTIONAL_HEADER.SizeOfStackReserve)
    res.append(pe.OPTIONAL_HEADER.SizeOfStackCommit)
    res.append(pe.OPTIONAL_HEADER.SizeOfHeapReserve)
    res.append(pe.OPTIONAL_HEADER.SizeOfHeapCommit)
    res.append(pe.OPTIONAL_HEADER.LoaderFlags)
    res.append(pe.OPTIONAL_HEADER.NumberOfRvaAndSizes)
    res.append(len(pe.sections))
    entropy=list(map(lambda x:x.get_entropy(), pe.sections))
    res.append(sum(entropy)/float(len(entropy)))
    res.append(min(entropy))
    res.append(max(entropy))
    raw_sizes=list(map(lambda x:x.SizeOfRawData, pe.sections))
    res.append(sum(raw_sizes)/float(len(raw_sizes)))
    res.append(min(raw_sizes))
    res.append(max(raw_sizes))
    virtual_sizes=list(map(lambda x:x.Misc_VirtualSize, pe.sections))
    res.append(sum(virtual_sizes)/float(len(virtual_sizes)))
    res.append(min(virtual_sizes))
    res.append(max(virtual_sizes))
    # Imports
    try:
        res.append(len(pe.DIRECTORY_ENTRY_IMPORT))
        imports=sum([x.imports for x in pe.DIRECTORY_ENTRY_IMPORT], [])
        res.append(len(imports))
        res.append(len(list(filter(lambda x: x.name is None, imports))))
    except AttributeError:
        res.append(0)
        res.append(0)
        res.append(0)
    # Exports
    try:
        res.append(len(pe.DIRECTORY_ENTRY_EXPORT.symbols))
    except AttributeError:
        # No export
        res.append(0)
    # Resources
    resources = get_resources(pe)
    res.append(len(resources))
    if len(resources) > 0:
        entropy = list(map(lambda x: x[0], resources))
        res.append(sum(entropy) / float(len(entropy)))
        res.append(min(entropy))
        res.append(max(entropy))
        sizes = list(map(lambda x: x[1], resources))
        res.append(sum(sizes) / float(len(sizes)))
        res.append(min(sizes))
        res.append(max(sizes))
    else:
        res.append(0)
        res.append(0)
        res.append(0)
        res.append(0)
        res.append(0)
        res.append(0)
    # Load configuration size
    try:
        res.append(pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.Size)
    except AttributeError:
        res.append(0)
    # Version configuration size
    try:
        version_infos = get_version_info(pe)
        res.append(len(version_infos.keys()))
    except AttributeError:
        res.append(0)
    pe.close()
    return res
def get_file_list(dir):
    if os.path.isdir(dir):
        return list(set(glob.glob(dir+'/**', recursive=True)) - set(glob.glob(dir+'/**/', recursive=True)))
    else:
        return list([dir])

columns = [
    "FilePath",
    "Machine",
    "SizeOfOptionalHeader",
    "Characteristics",
    "MajorLinkerVersion",
    "MinorLinkerVersion",
    "SizeOfCode",
    "SizeOfInitializedData",
    "SizeOfUninitializedData",
    "AddressOfEntryPoint",
    "BaseOfCode",
    "BaseOfData",
    "ImageBase",
    "SectionAlignment",
    "FileAlignment",
    "MajorOperatingSystemVersion",
    "MinorOperatingSystemVersion",
    "MajorImageVersion",
    "MinorImageVersion",
    "MajorSubsystemVersion",
    "MinorSubsystemVersion",
    "SizeOfImage",
    "SizeOfHeaders",
    "CheckSum",
    "Subsystem",
    "DllCharacteristics",
    "SizeOfStackReserve",
    "SizeOfStackCommit",
    "SizeOfHeapReserve",
    "SizeOfHeapCommit",
    "LoaderFlags",
    "NumberOfRvaAndSizes",
    "SectionsNb",
    "SectionsMeanEntropy",
    "SectionsMinEntropy",
    "SectionsMaxEntropy",
    "SectionsMeanRawsize",
    "SectionsMinRawsize",
    "SectionMaxRawsize",
    "SectionsMeanVirtualsize",
    "SectionsMinVirtualsize",
    "SectionMaxVirtualsize",
    "ImportsNbDLL",
    "ImportsNb",
    "ImportsNbOrdinal",
    "ExportNb",
    "ResourcesNb",
    "ResourcesMeanEntropy",
    "ResourcesMinEntropy",
    "ResourcesMaxEntropy",
    "ResourcesMeanSize",
    "ResourcesMinSize",
    "ResourcesMaxSize",
    "LoadConfigurationSize",
    "VersionInformationSize",
    "legitimate"
]

# input_data: string or list
def append_data_to_csv(input_data, target_csv_file_path):
    csv_delimiter = ","
    global columns
    if not os.path.isfile(target_csv_file_path):
        ff = open(target_csv_file_path, "w+")
        ff.write(csv_delimiter.join(columns) + "\n")
    else:
        ff = open(target_csv_file_path, "a")
    # default type of input_data is list 2D
    if type(input_data) == str: # if input_data is csv file path then read data of csv file path
        input_data = pd.read_csv(str(input_data)).values
    with tqdm.tqdm(total=len(input_data)) as pbar:
        for file in input_data:
            ff.write(csv_delimiter.join(map(lambda x:str(x), file)) + "\n")
            pbar.update(1)
    print("done")
    ff.close()
    return columns
def create_data(raw_data_path, data_type=2, output_csv_file_path=None):
    output = []
    global columns
    file_list = get_file_list(str(raw_data_path))
    with tqdm.tqdm(total=len(file_list)) as pbar:
        for file in file_list:
            try:
                res = extract_infos(file)
                res.append(int(data_type))
                output.append(res)
                pbar.set_description('- extracting file: ...'+file[-30:]+'[done]')
            except:
                pbar.set_description('- extracting file: ...'+file[-30:]+'[error]')
            pbar.update(1)
    if output_csv_file_path == None:
        print("done")
        return output, columns
    else:
        print("write data to csv:", str(output_csv_file_path))
        append_data_to_csv(output, str(output_csv_file_path))