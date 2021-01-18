# !/usr/lib/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import re
import logging
import os
import shutil
import json
import threading
import concurrent.futures
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='example.log',level=logging.DEBUG)

baseUrl = 'https://www.tujidao.com'
cookie = '7Dw1Tw3Bh2Mvfr=; UM_distinctid=173f0c5bc3717e-09b6cf2e7e2015-3972095d-1fa400-173f0c5bc38b44; 7Dw1Tw3Bh2Mvu%5Fleixing=3; 7Dw1Tw3Bh2Mvu%5Fpw=84f05029abccc09a; 7Dw1Tw3Bh2Mvu%5Fusername=asdf0823; 7Dw1Tw3Bh2Mvu%5Fid=229195; ASPSESSIONIDCWDQSQRQ=DHMOPECDLLEHFEBKIGHCBHKI; CNZZDATA1257039673=454938172-1597469558-%7C1597474969'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.tujidao.com',
    'Cookie': cookie
}

imageHeaders = {
'Host': 'lns.hywly.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate, br',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'If-Modified-Since': 'Tue, 19 May 2020 07:36:33 GMT',
'If-None-Match': "5ec38c81-9d03e",
'Cache-Control': 'max-age=0',
'TE': 'Trailers',
}
tags = []
albums = []
imagesDir = "./images"

def start():
    r = requests.get(baseUrl, verify=False, headers=headers)
    if(r.status_code == 200):
        soup = BeautifulSoup(r.text, 'lxml')
        tagsSoup = soup.select('div.tags > a')
        for a in tagsSoup:
            r = re.search(r'/(?P<type>\w)/\?id=(?P<id>\d+)',a['href'])
            tag = {'name': a.text, 'url': a['href'],'tagId':r['id'],'type':r['type']}
            tags.append(tag)
        # tags保存到文件    
        with open('tags.json','w',encoding='utf-8') as f:
                f.write(json.dumps(tags,ensure_ascii=False))
        for tag in tags:
            try:
                extractTag(tag)
            except Exception as e:
                logging.error(e)    
                logging.info('step over this error and continue')
                continue

def extractTag(tag):
    '''
    提取标签
    '''
    logging.info('==============extractTag=============')
    tagUrl = tag['url']
    logging.info("extractTag:%s",tagUrl)
    logging.info('tagName:%s',tag['name'])
    # 标签文件夹
    tagDir = '{imagesDir}/{tagName}-{type}-{id}'.format(imagesDir=imagesDir, tagName=tag['name'],type=tag['type'],id=tag['tagId']) 
    logging.info('tagDir:%s',tagDir)
    if not os.path.exists(tagDir):
        os.makedirs(tagDir)
    if(not(tagUrl.startswith('http') or tagUrl.startswith('https'))):
        tagUrl = baseUrl + tagUrl
    logging.info('tagUrl:%s',tagUrl)
    # 获取tag
    r = requests.get(tagUrl, verify=False, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    albums4Tag = soup.select('div.hezi ul li')
    logging.info("albums4Tag size:%s",len(albums4Tag))
    with concurrent.futures.ThreadPoolExecutor(len(albums4Tag)) as executor:
        for album in albums4Tag:
            executor.submit(extractAlbum,album,tagDir)
    logging.info('extractTag %s completed',tag)

def extractAlbum(album,tagDir):
    '''提取相册
    
    album: 相册名
    tagDir: 标签对应的目录
    '''
    logging.info('>>>>>>>>>>thread-%s extractAlbum>>>>>>>>>',threading.current_thread.__name__)
    try:
        # 标题
        biaoti = album.select_one('.biaoti')
        # 一个album中图片的数量
        count = album.select_one('.shuliang')
        # 机构
        organization = album.select_one('p:nth-of-type(1) a')
        # 标签
        lables = album.select('p:nth-of-type(2) a')
        # 任务
        figure = album.select_one('p:nth-of-type(3) a')
        ### 提取数据
        title = biaoti.a.text
        url = biaoti.a['href']
        #id
        r = re.search(r'id=(?P<id>\d+)',url)
        albumId = r.groupdict()['id']
        count = int(count.text[:-1])
        organizationUrl = organization['href']
        organization = organization.text
        lables = [{'label':label.text,'url':label['href']} for label in lables]
        if not figure:
            figureUrl = ''
            figure = 'unkonwn'
        else:    
            figureUrl = figure['href'],
            figure = figure.text
        logging.info('===========album=============')
        logging.info('title:%s',title)
        logging.info('url:%s',url)
        logging.info('count:%s',count)
        logging.info('figure:%s',figure)
        albumInfo = {
            'id':albumId,
            'title': title,
            'url': url,
            'count': count,
            'organization': organization,
            'organizationUrl':organizationUrl,
            'lables': lables,
            'figure': figure,
            'figureUrl':figureUrl,
        }
        albums.append(albumInfo)
        albumName  = '{title}-{figure}-{count}'.format(title=title,figure=figure,count=count)
        dir = '{tagDir}/{albumName}'.format(albumName=albumName,tagDir=tagDir)
        newAlbumDir = '{tagDir}/{albumName}-{albumId}'.format(albumName=albumName,tagDir=tagDir,albumId=albumId)
        originDir = '{}/{albumName}'.format(imagesDir,albumName=albumName)
        logging.info('dir:%s',dir)
        logging.info('originDir:%s',originDir)
        if(os.path.exists(originDir)):
            logging.info('origin dir is exist!')
            dirFileCount = getFilesCountOfDir(originDir)
            logging.info('origin dir file count:%s',dirFileCount)
            if(dirFileCount >= count):
                # 文件夹拷贝到tag目录中
                # 先将dest中的文件夹删除
                shutil.rmtree(dir,ignore_errors=True)
                shutil.move(originDir,dir)
                logging.info('move file from origin dir to new dir')
                return
        if(os.path.exists(dir)):
            logging.info('dir is not exist.try to make dir %s',dir)
            os.rename(dir,newAlbumDir)
        if not os.path.exists(newAlbumDir):
            os.mkdir(newAlbumDir)
            logging.warning('***dir:%s is exist.***',dir)
        dir = newAlbumDir    
        dirFileCount = getFilesCountOfDir(dir)
        if(dirFileCount >= count):
            return
    except Exception as error:
        logging.error(error)
        return
    # 下载图片
    # 图片地址，https://lns.hywly.com/a/1/34927/4.jpg
    # https://lns.hywly.com/a/1/34927/4.jpg
    for i in range(int(count)):
        r = re.search(r'id=(?P<id>\d+)',url)
        id = r.groupdict()['id']
        imageUrl = 'https://lns.hywly.com/a/1/{id}/{i}.jpg'.format(id = id, i = i)
        try:
            downloadImage(imageUrl,'{title}-{figure}-{count}.jpg'.format(figure=figure,title=title,count=i),dir)
        except Exception as e:
            logging.error(e)   
            continue       
def downloadImage(url,filename,dir):
    '''下载图片.
    从url下载图片到指定目录dir中，并保存图片名称为filename
    
    url: 图片地址 

    filename: 图片保存文件名 

    dir: 下载图片到某个目录 
    '''
    logging.info('>>>downloadImage:{url}'.format(url=url))
    filename = os.path.join(dir,filename)
    if(os.path.exists(filename)):
        logging.info("!!!image>>>%s is exist.",filename)
        return
    res = requests.get(url,headers=imageHeaders,verify=False)
    with open(filename,'wb',encoding='utf-8') as f:
        f.write(res.content)

def getFilesCountOfDir(dir,level = 1):
    '''获取目录中文件数量
    
    dir: 目录
    level: 目录层级
    '''
    logging.info('=============getFilesCountOfDir==========')
    logging.info('dir:%s;level:%s',dir,level)
    if not (os.path.isdir(dir)):
        logging.warning('dir:%s is not a directory!',dir)
        return 0
    count = 0
    for d in os.listdir(dir):
        # TODO: 判断isfile需要把路径加上，否则d只是文件名，isfile会为false
        if(os.path.isfile(os.path.join(dir,d))):
            count += 1
    return count        

if __name__ == '__main__':
    try:
        start()
    except Exception as e:
        logging.error(e,stack_info=True)