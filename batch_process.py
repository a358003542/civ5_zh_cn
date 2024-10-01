import os
import logging
import shutil
import sys

import opencc
from lxml import etree


logger = logging.getLogger('batch_opencc')
logging.basicConfig(level=logging.DEBUG)

converter = opencc.OpenCC('hk2s.json')


def get_script_folder():
    # path of main .py or .exe when converted with pyinstaller
    if getattr(sys, 'frozen', False):
        script_path = os.path.dirname(sys.executable)
    else:
        script_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return script_path

def get_data_folder():
    # path of your data in same folder of main .py or added using --add-data
    if getattr(sys, 'frozen', False):
        data_folder_path = sys._MEIPASS
    else:
        data_folder_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return data_folder_path


current_workpath = get_script_folder()
steam_app_path = current_workpath
temp_data_folder = get_data_folder()

if getattr(sys, 'frozen', False):
    steam_app_path = current_workpath
else:
    # 脚本测试模式
    steam_app_path = "D:\\Program Files (x86)\\Steam\\steamapps\\common\\Sid Meier's Civilization V"

file_list = []

with open(os.path.join(temp_data_folder, 'file.txt')) as f:
    for line in f:
        text = line.strip()
        if text:
            file_list.append(text)


def check_file_content(file_path):
    content = ''
    with open(file_path, encoding='utf8') as f:
        content = f.read()

        logging.debug(f'原始的内容是：\n {content[:500]}')

    return content


def replace_text(lst):
    for e in lst:
        e.text = converter.convert(e.text)


for testfile in file_list:
    testfile_path = os.path.join(steam_app_path, testfile)

    logging.debug(f'working on {testfile_path}')

    content = check_file_content(testfile_path)

    doc = etree.XML(content)

    text_e = doc.xpath('//Language_ZH_Hant_HK//Text')

    replace_text(text_e)

    new_doc = etree.tostring(doc, pretty_print=True, encoding='utf8').decode()

    logging.debug(f'转换后的内容是：\n {new_doc[:500]}')

    # 备份工作
    dst_folder, dst_filename = os.path.split(testfile)
    dst_file = os.path.join(
        current_workpath, 'Language_ZH_Hant_HK_Backup', testfile)
    dst_folder2, dst_filename = os.path.split(dst_file)

    os.makedirs(dst_folder2, exist_ok=True)

    src_file = testfile_path

    if os.path.exists(dst_file):
        pass
    else:
        shutil.copyfile(src_file, dst_file)

    logger.debug(f'文件已备份到： {dst_file} ')

    # 实际修改文件
    with open(testfile_path, mode='w', encoding='utf8') as f:
        f.write(new_doc)

    logger.debug(f'目标文件实际修改完成： {testfile_path}')


# 移入优化的Chinese.xml
src_chinese = os.path.join(temp_data_folder, 'Chinese.xml')
dst_chinese = os.path.join(steam_app_path, 'Assets', 'Gameplay', 'XML','NewText', 'Chinese.xml')
shutil.copyfile(src_file, dst_file)
logger.debug(f'优化后的Chinese.xml已移入目的地: {dst_chinese}')
