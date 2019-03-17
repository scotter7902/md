import pefile
import os
import hashlib
import array
import math
import check

def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_entropy(data):
    if len(data) == 0:
        return 0.0
    occurences = array.array('L', [0] * 256)
    for x in data:
        occurences[x if isinstance(x, int) else ord(x)] += 1

    entropy = 0
    for x in occurences:
        if x:
            p_x = float(x) / len(data)
            entropy -= p_x * math.log(p_x, 2)

    return entropy


def get_resources(pe):
    """Extract resources :
    [entropy, size]"""
    resources = []
    if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
        try:
            for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:

                if hasattr(resource_type, 'directory'):
                    for resource_id in resource_type.directory.entries:
                        if hasattr(resource_id, 'directory'):
                            for resource_lang in resource_id.directory.entries:
                                data = pe.get_data(resource_lang.data.struct.OffsetToData,
                                                   resource_lang.data.struct.Size)
                                size = resource_lang.data.struct.Size

                                entropy = float(get_entropy(data))

                                resources.append([entropy, size])
        except Exception:
            return resources
    return resources


def get_version_info(pe):
    ret = []
    if hasattr(pe, 'VS_VERSIONINFO'):
        for x in pe.VS_VERSIONINFO:
            for a in x.__unpacked_data_elms__:
                if a!=0:
                    ret.append(a)
        if hasattr(pe, 'FileInfo'):
            for entry in pe.FileInfo:
                for x in entry:
                    for a in x.__unpacked_data_elms__:
                        if a != 0:
                            ret.append(a)

    if hasattr(pe, 'VS_FIXEDFILEINFO'):
        for x in pe.VS_FIXEDFILEINFO:
            ret.append(x.FileFlags)
            ret.append(x.FileOS)
            ret.append(x.FileType)
            ret.append(x.FileVersionLS)
            ret.append(x.ProductVersionLS)
            ret.append(x.Signature)
            ret.append(x.StrucVersion)
    return ret



def extract_infos(fpath):
    res = []
    res.append(os.path.basename(fpath))
    res.append(get_md5(fpath))
    pe = pefile.PE(fpath)
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
    entropy = list()
    for x in pe.sections:
        entropy.append(x.get_entropy())
    try:
        res.append(sum(entropy) / float(len(entropy)))
    except:
        res.append(0)
    try:
        res.append(min(entropy))
    except:
        res.append(0)
    try:
        res.append(max(entropy))
    except:
        res.append(0)
    raw_sizes = list(map(lambda x: x.SizeOfRawData, pe.sections))
    try:
        res.append(sum(raw_sizes) / float(len(raw_sizes)))
    except:
        res.append(0)
    try:
        res.append(min(raw_sizes))
    except:
        res.append(0)
    try:
        res.append(max(raw_sizes))
    except:
        res.append(0)
    virtual_sizes = list(map(lambda x: x.Misc_VirtualSize, pe.sections))
    try:
        res.append(sum(virtual_sizes) / float(len(virtual_sizes)))
    except:
        res.append(0)
    try:
        res.append(min(virtual_sizes))
    except:
        res.append(0)
    try:
        res.append(max(virtual_sizes))
    except:
        res.append(0)
    # Imports
    try:
        res.append(len(pe.DIRECTORY_ENTRY_IMPORT))
        imports = sum([x.imports for x in pe.DIRECTORY_ENTRY_IMPORT], [])
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
        try:
            res.append(sum(entropy) / float(len(entropy)))
        except:
            res.append(0)
        try:
            res.append(min(entropy))
        except:
            res.append(0)
        try:
            res.append(max(entropy))
        except:
            res.append(0)
        sizes = list(map(lambda x: x[1], resources))
        try:
            res.append(sum(sizes) / float(len(sizes)))
        except:
            res.append(0)
        try:
            res.append(min(sizes))
        except:
            res.append(0)
        try:
            res.append(max(sizes))
        except:
            res.append(0)
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
    #size imfomation version
    try:
        version_infos = get_version_info(pe)
        res.append(len(version_infos))
    except AttributeError:
        res.append(0)
    return res

if __name__ == '__main__':
    output = "data.csv"
    csv_delimiter = "|"
    columns = [
        "Name",
        "md5",
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
        "legitimate"
    ]
    print('- openning data.csv', end='...')
    try:
        ff = open(output, "w+")
        print('[done]')
    except:
        print('[error]')
        exit()
    ff.write(csv_delimiter.join(columns) + "\n")

    # run
    check.fols_()
    pro_ = 0
    sum_ = check.len_(check.fols[0])
    for fol in check.fols[1:]:
        for file in os.listdir(fol):
            print('- reading file: '+'/'.join([fol, file]), end=' ')
            pro_ = pro_+1
            try:
                res = extract_infos('/'.join([fol, file]))
                res.append(abs(check.fols.index(fol)-2))
                ff.write(csv_delimiter.join(map(lambda x:str(x), res)) + "\n")
                print('[done]'+'['+str(pro_)+'/'+str(sum_)+']')
            except:
                print('[error]'+'['+str(pro_)+'/'+str(sum_)+']')
    print("- done")
    ff.close()
