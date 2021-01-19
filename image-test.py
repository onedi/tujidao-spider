import requests
import os
imageBaseUrl ='https://tjg.hywly.com'
imageHeaders = {
'Host': 'tjg.hywly.com',
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

def downloadImage(url,filename,dir):
    '''下载图片.
    从url下载图片到指定目录dir中，并保存图片名称为filename
    
    url: 图片地址 

    filename: 图片保存文件名 

    dir: 下载图片到某个目录 
    '''
    filename = os.path.join(dir,filename)
    if(os.path.exists(filename)):
        return
    res = requests.get(url,headers=imageHeaders,verify=False)
    print(res)
    with open(filename,'wb') as f:
        f.write(res.content)

if __name__ == '__main__':
    downloadImage('https://lns.hywly.com/a/1/33779/40.jpg','test.jpg','./')