# IDM-Batch-Download-Helper

## 1.简介
爬取网页后经常产生大量资源链接，如何快捷地将它们分别下载到指定的文件夹？urllib和requests库的确可以做到，但它们经常会遇到下载速度缓慢甚至卡死、操作复杂易错等问题。

**IDM批量下载助手**可以帮你快速实现批量下载。同时支持为每个文件指定子文件夹和重命名。

## 2.使用方法
安装Python环境和IDM软件后，启动helper.py，输入CSV格式的资源链接文件并选择一个保存位置，即可开始下载。

### 2.1 CSV资源链接文件 - 格式
本工具使用csv文件作为下载地址等参数的保存格式，称为CSV资源链接文件。其中资源参数的基本单位为“行”。在使用本工具进行批量下载前，应将资源链接按照指定格式整理为CSV资源链接文件。

CSV资源链接文件有三列。第一行为标题行，后续每行为一条资源链接。

第一列资源链接（url），留空则跳过此行。

第二列子文件夹名（subfolder），指定子文件夹名会在保存目录下建立子文件夹，将本行资源下载到子文件夹内，留空则直接下载到保存文件夹。这一参数在批量下载专辑、相册等内容时特别有用。

第三列文件名（filename），为本行资源重命名。留空则使用url中给出的原始文件名。拓展名继承url中给出的原始拓展名。

| url                           | subfolder    | filename |
|-|-|-|
| http://site.com/file1.pdf     | myFiles      | recipe   |
| http://site2.com/scenery.jpg  | myPictures   |          |
| http://site.com/fb38te1.mp3   |              | Firework |

使用“_last_link”关键字开头的文件名将触发*单链接多文件模式*。

test.csv给出了具体示例。

### 2.2 CSV资源链接文件 - 使用

可以在helper.py启动前，将CSV资源链接文件拖动到helper.py上，一次性完成启动和读取文件两个操作。

当helper.py和CSV资源链接文件在同一目录下时，可直接输入CSV资源链接文件名。也可以直接指定CSV资源链接文件的绝对路径。

当helper.py和CSV资源链接文件不在同一目录下时，应指定CSV资源链接文件的绝对路径。

### 2.3 保存位置
在命令行提示输入保存位置时，指定一个文件夹的绝对路径作为保存位置。

如果输入空的保存位置，将使用helper.py所在目录作为保存位置。

### 2.4 进阶 - 单链接多文件模式
使用“_last_link”关键字开头的文件名将触发*单链接多文件模式*，将本行的url拓展为多个链接，添加到下载队列。此时该参数不再表示文件名。

此模式将url解析为 *前缀(perfix)+文件名(filename)* 格式，将其中的 *文件名* 解析为 *固定部分（fix)+可变部分(var)+拓展名(ext)* 格式。其中可变部分var为数字，其长度由“_last_link”关键字后紧跟的正整数决定。*单链接多文件模式*将这串数字替换为不超过var数值的正整数序列，并全部添加到下载队列。

**例：**

若资源链接文件中有如下内容：

|url|subfolder|filename|
|:-|:-|:-|
| http://example.com/zzpic23693.jpg |  | \_last_link1 |

文件名：zzpic23693.jpg

文件名解析："zzpic2369" + "3" + ".jpg"

实际创建的下载链接：

http://pics.sc.chinaz.com/files/pic/pic9/202003/zzpic23693.jpg

http://pics.sc.chinaz.com/files/pic/pic9/202003/zzpic23692.jpg

http://pics.sc.chinaz.com/files/pic/pic9/202003/zzpic23691.jpg

## 3.示例
提供了test.csv作为输入示例。




-----
[你说的这个IDM，它到哪下载啊？](https://www.52pojie.cn/thread-1013874-1-1.html)
