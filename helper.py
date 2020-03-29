# -*- coding: utf-8 -*-
import time
import os
import sys
import csv
import json
from subprocess import Popen
from locale import getdefaultlocale

# 记录本机IDM文件位置
def config(data = "", config_status = True):
    # 返回的是路径，不含文件名
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    IDM = "IDMan.exe"
    if not data:

        if os.path.isfile("config.json") and config_status: # 有config就试试读取
            try:
                with open("config.json", "r", encoding='utf-8') as f:
                    return json.loads(f.read())
            except Exception:
                return "" # config文件可能是损坏的
        
        else: # 没config也没data，只好自己找咯
            IDMPath = "C:/Program Files (x86)/Internet Download Manager/"
            IDMPath = "C:/Program/" # for debug
            for x in ["D","E","F","G","Z"]:
                if not os.path.isfile(os.path.join(IDMPath,IDM)):
                    IDMPath = x+IDMPath[1:]
                    continue
                return config(IDMPath)
            if x=="Z": # 找又找不到，只好问用户咯
                while not os.path.isfile(os.path.join(IDMPath,IDM)):
                    print(">> Check your IDM path")
                    IDMPath = input(">> Path of your IDM software:\n")
                    IDMPath = IDMPath.strip("\'\"")
                    if IDMPath.split('/')[-1] == IDM:
                        IDMPath = os.path.dirname(IDMPath)
                return config(IDMPath)

    else: # 有data就覆写进去
        data = data.strip("\'\"")
        if data.split('/')[-1] == IDM:
            data = os.path.dirname(data)
        with open("config.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(data))
        return data



# 建立IDM下载队列并开始下载
def IDMdown(url_list, save_dir_list, file_name_list=""):
    # url_list: list 待下载链接列表，长度为n
    # save_dir_list: list 本地保存位置，长度为n或者1
    # file_name_list: list 文件重命名，可留空

    IDMPath = config() # 路径，不含文件名
    IDM = "IDMan.exe"

    # 再次检查输入数据
    if not file_name_list:
        file_name_list = [x.split('/')[-1] for x in url_list]
    if len(save_dir_list) < len(url_list): # 按最后一项补完保存位置
        save_dir_list.extend( save_dir_list[-1]*(len(url_list)-len(save_dir_list)) )

    # 提前启动IDM，否则会卡死在第一个任务
    try:
        os.chdir(IDMPath)
        Popen(IDM)
    except Exception:
        IDMPath = config("",False)
        os.chdir(IDMPath)
        Popen(IDM) # 这种情况下还失败就异常退出算了
    time.sleep(4) # 等待IDM启动

    # 显示任务信息摘要
    print('>> Total file(s) amount: '+str(len(url_list)))
    sec = str(  int( 0.6*len(url_list) )  )
    print('>> Estimated waiting time: '+sec+" s.")
    print('>> Building IDM task list...')

    # 传输建立下载列表
    for i in range(len(url_list)):
        processbar(i,len(url_list),'Building...')
        Popen([IDM, '/d', url_list[i], '/p', save_dir_list[i], '/f', file_name_list[i], '/a'])
        if (i+1)%50 == 0:
            try:
                Popen([IDM, '/s']) # 加速开始任务
            except Exception:
                print('Warning: Accelerating starting IDM task list fialed')
    print('\n')

    # 开始任务
    try:
        Popen([IDM, '/s'])
    except Exception:
        print('Error: Start IDM task list fialed!')
        return -1
    print('Download started!')
    return 1


# 检查指定名称进程存活数量
def get_process_count(imagename):
    p = os.popen('tasklist /FI "IMAGENAME eq %s"' % imagename)
    return p.read().count(imagename)


# 根据csv文件中的地址和分类名分别下载文件
def down_from_csv(file,save_dir_perfix):
    """
    file: str csv文件绝对路径地址。
        Links source file format :
        -----------------------------------------------------------
        | url                           | subfolder    | filename |
        -----------------------------------------------------------
        | http://site.com/file1.pdf     | myFiles      | recipe   |
        -----------------------------------------------------------
        | http://site2.com/scenery.jpg  | myPictures   |          |
        -----------------------------------------------------------
        | http://site.com/fb38te1.mp3   |              | Firework |
        -----------------------------------------------------------
    save_dir_perfix: str  保存路径
    """

    # 载入CSV
    print('Loading...')
    try:
        f = open(file, encoding='utf-8')
        src = [ x for x in csv.reader(f) ]
    except Exception:
        try:
            f = open(file, encoding='gbk')
            src = [ x for x in csv.reader(f) ]
        except Exception as e:
            print('Load file failed.Check CSV file encoding.', e)
            return -1
    f.close()
    print('>>Loaded %s '%file)
    
    # 提取和检查数据
    rows = len(src)-1 # 标题行无用
    #defualt_folder = time.strftime("%Y%m%d%H%M%S") # 理论上应该用不到
    url_list = []
    save_dir_list = []
    file_name_list = []
    for i in range(rows):
        # url为空
        if not src[i+1][0]:
            continue
        else:
            url_list.append(src[i+1][0])

        # 子文件夹名为空
        save_dir = os.path.join(save_dir_perfix , src[i+1][1])
        save_dir_list.append(save_dir)

        file_name = src[i+1][2] 
        file_name = file_name.replace("/","_") # 不允许正斜杠文件名
        # 如果含有反斜杠"\"，则会以\前为名继续创建子文件夹，以\后为文件名（it's feature.
        # 文件名为空
        file_name = src[i+1][2]
        if not file_name:
            file_name = url_list[-1].split('/')[-1]
            file_name_list.append(file_name)
        # 最后链接批量标识：_last_link
        # '_last_link2' 表示文件名可变部分为最后两位，从01到last
        elif file_name[0:10] == "_last_link":
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
            
            j = 1
            while j < int(var): # 生成从1开始到last-1的链接
                tmp_file_name = fix + str(j).zfill(len(var)) + ext # 默认补零格式
                tmp_url = url_perfix + tmp_file_name
                url_list.append(tmp_url)
                save_dir_list.append(save_dir_list[-1])
                file_name_list.append(tmp_file_name)
                j+=1
        else:
            file_name = file_name +'.'+ url_list[-1].split('.')[-1] # 添加拓展名，否则前缀中含有下圆点时显示不全
            file_name_list.append(file_name)

    # 使用IDM下载
    flag = IDMdown(url_list, save_dir_list, file_name_list)
    if flag == 1:
        print('>>Import success, plz quit and wait IDM.')
        return 1
    else:
        return flag

# 进度条
def processbar(i,total,message = 'Processing...'):
    sys.stdout.write('\r>> '+message+' %.1f%%' % (float(i + 1) / float(total) * 100.0))
    sys.stdout.flush()

def guide():
    print("\n----Batch Download Files using IDM----\n")

    # CSV文件的位置。支持当前文件夹的文件名或任意绝对路径
    print('Columns: url  subfolder  filename')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file = ""

    # check drag file first
    if len(sys.argv) >= 2:
        check_file = sys.argv[1] # absolute path
        if check_file.endswith(".csv"):
            file = check_file

    ## check file in same dir  ###这里的逻辑不好，同一目录下可能有多个csv，自动选择第一个可能智障
    #if file == "":
    #    current_files = os.listdir('.')
    #    for current_file in current_files:
    #        if current_file.endswith(".csv"):
    #            file = os.path.abspath(current_file)
    #            break

    while not file:
        file = input("Name of CSV file in current folder or absolute path:\n")
        file = file.strip("\'\"")
        if not file.endswith(".csv"):
            file = file + ".csv"
        file = os.path.join(file_dir,file)#如果file是绝对路径，则file_dir会被自动丢弃
        if not os.path.isfile(file):
            print("Wrong path!")
            file = ""
    print(r">>Selected data source: " + file)
    
    # 下载到本地的位置。默认当前目录
    save_dir_perfix = ""
    save_dir_perfix = input("Absolute save path:\n")
    if not save_dir_perfix:
        save_dir_perfix = file_dir
        print("Using current directory as save folder.")

    
    save_dir_perfix = save_dir_perfix.strip("\'\"")
    print(">>Selected save directory: " + save_dir_perfix)
    
    # 启动下载器
    down_from_csv(file, save_dir_perfix)

# 汉化工具（测试中
def _(str):
    lc = getdefaultlocale()[1]
    if lc=='zh_CN':
        return EN2CN(str)
    else:
        return str

# 汉化工具（测试中
def EN2CN(str):
    EN_CN = {
        '':'',
        '':'',
        }
    return EN2CN[str]


if __name__ == "__main__":
    guide()
    os.system("pause")
