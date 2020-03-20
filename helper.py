# -*- coding: utf-8 -*-
import time
import os
import sys
import pandas as pd
from subprocess import call

#  srs@2020
def IDMdown(url_list, save_dir_list,file_name_list=""):
    """
    url_list: list 待下载链接列表，长度为n
    save_dir_list: list 本地保存位置，长度为n或者1
    file_name_list: list 文件重命名，可留空
    """
    
    # 找找IDM
    IDMPath = "C:/Program Files (x86)/Internet Download Manager/"
    IDM = "IDMan.exe"
    for x in ["D","E","F","G","Z"]:
        if not os.path.isfile(os.path.join(IDMPath,IDM)):
            if x=="Z":
                while not os.path.isfile(os.path.join(IDMPath,IDM)):
                    IDMPath = input("Path of IDMan.exe:\n")
                    if IDMPath[0]=="\"" or IDMPath[0]=="\'":
                        IDMPath = IDMPath[1:]
                    if IDMPath[-1]=="\"" or IDMPath[-1]=="\'":
                        IDMPath = IDMPath[0:-1]
                    if IDMPath.split('/')[-1] == IDM:
                        IDMPath = os.path.dirname(IDMPath)
            else:
                IDMPath = x+IDMPath[1:];

    # 再次检查输入数据
    if not file_name_list:
        file_name_list = [x.split('/')[-1] for x in url_list]
    if len(save_dir_list) < len(url_list): # 按最后一项补完保存位置
        save_dir_list.extend( save_dir_list[-1]*(len(url_list)-len(save_dir_list)) )

    # 建立下载队列
    os.chdir(IDMPath)
    call(IDM) # 提前启动，否则会卡死在第一个任务
    #time.sleep(3)
    for i in range(len(url_list)):
        processbar(i,len(url_list),'Transfering...')
        call([IDM, '/d', url_list[i], '/p', save_dir_list[i], '/f', file_name_list[i], '/a'])
        if (i+1)%50 == 0:
            flag = call([IDM, '/s']) # 加速开始任务
    print('\n')
    flag = call([IDM, '/s']) # 开始任务
    if not flag:
        print('Download started!')
    return not flag



# 根据csv文件中的地址和分类名分别下载文件
def down_from_csv(file,save_dir_perfix):
    """
    file: str csv文件绝对路径地址。
        特征：
        文件有标题行。有三列。
        第一列url，留空则跳过此行
        第二列子文件夹名，留空则直接下载到保存文件夹
        第三列文件名，留空则使用url中给出的原始文件名
    save_dir_perfix: str  保存路径
    """

    # 载入CSV
    print('Loading...')
    try:
        src = pd.read_csv(file, names=['url','subfolder','filename'], encoding="utf-8", keep_default_na=False)
    except Exception as e:
        try:
            src = pd.read_csv(file, names=['url','subfolder','filename'], encoding="gb2312", keep_default_na=False)
        except Exception as e:
            print('Load file failed.Check CSV file encoding.')
            return -1
    print('>>Loaded %s '%file)
    
    # 提取和检查数据
    rows = src.values.shape[0]-1 # 标题行无用
    #defualt_folder = time.strftime("%Y%m%d%H%M%S") # 理论上应该用不到
    url_list = []
    save_dir_list = []
    file_name_list = []
    for i in range(rows):
        # url为空
        if not src.url.values[i+1]:
            continue
        else:
            url_list.append(src.url.values[i+1])

        # 子文件夹名为空
        save_dir = os.path.join(save_dir_perfix , src.subfolder.values[i+1])
        save_dir_list.append(save_dir)

        # 文件名为空
        file_name = src.filename.values[i+1]
        if not file_name:
            file_name = url_list[-1].split('/')[-1]
        # 最后链接批量标识：_last_link
        # '_last_link2' 表示文件名可变部分为最后两位，从01到last
        if file_name[0:10] == "_last_link":
            if len(file_name) > 10:
                var_len = int(file_name[10:])
            else:
                var_len = 0
            file_name = url_list[-1].split('/')[-1] # 改回默认文件名
            file_name_list.append(file_name) # 完成本行数据
            
            # file202012.jpg -> 'file2020','12','.jpg' = fix + var + ext
            perfix_len = len(url_list[-1]) - len(file_name) # 提取链接前缀
            url_perfix = url_list[-1][:perfix_len]
            ext = '.'+file_name.split('.')[-1] # 文件拓展名
            ext_len = len(ext)
            if var_len == 0:
                var_len = len(file_name) - ext_len
            fix_len = len(file_name) - var_len - ext_len
            fix = file_name[0:fix_len]# 文件固定名
            var = file_name[fix_len:-ext_len] # 文件可变名
            
            i = 1
            while i < int(var): # 生成从1开始到last-1的链接
                tmp_file_name = fix + str(i+1).zfill(len(var)) + ext # 默认补零格式
                tmp_url = url_perfix + tmp_file_name
                url_list.append(tmp_url)
                save_dir_list.append(save_dir_list[-1])
                file_name_list.append(tmp_file_name)
                i+=1
        else:
            file_name.replace(".","_") #文件名中的"."被替换
            file_name_list.append(file_name)
    
    # 传送数据到IDM并建立列表
    print('>>Total files amount: '+str(len(url_list)))
    sec = str(  int( 0.6*len(url_list) )  )
    print('>>Transfering to IDM...')
    print('>>Estimated waiting time: '+sec+" s.")
    flag = IDMdown(url_list, save_dir_list, file_name_list)
    print('>>Import success, plz quit and wait IDM.')
    return 0

# 进度条
def processbar(i,total,message = 'Processing...'):
    sys.stdout.write('\r>> '+message+' %.1f%%' % (float(i + 1) / float(total) * 100.0))
    sys.stdout.flush()

def guide():
    print("----Batch Download Files using IDM----")

    # CSV文件的位置。支持当前文件夹的文件名或任意绝对路径
    print('Columns: url  subfolder  filename')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file = ""
    while not file:
        file = input("Name of CSV file in current folder or absolute path:\n")
        if file[0]=="\"" or file[0]=="\'":
            file = file[1:]
        if file[-1]=="\"" or file[-1]=="\'":
            file = file[0:-1]
        if file[-4:] != ".csv":
            file = file + ".csv"
        file = os.path.join(file_dir,file)#如果file是绝对路径，则file_dir会被自动丢弃
        if not os.path.isfile(file):
            print("Wrong path!")
            file = ""
    print(r">>Selected data source: "+file)
    
    # 下载到本地的位置。默认当前目录
    save_dir_perfix = ""
    save_dir_perfix = input("Absolute save path:\n")
    if not save_dir_perfix:
        save_dir_perfix = file_dir;
        print("Using current directory as save folder.")

    
    if save_dir_perfix[0]=="\"" or save_dir_perfix[0]=="\'":
        save_dir_perfix = save_dir_perfix[1:]
    if save_dir_perfix[-1]=="\"" or save_dir_perfix[-1]=="\'":
        save_dir_perfix = save_dir_perfix[0:-1]
    print(">>Selected save directory: "+save_dir_perfix)
    
    # 启动下载器
    down_from_csv(file,save_dir_perfix)


if __name__ == "__main__":
    guide()
    os.system("pause")
