# !/usr/lib/python3
import requests
from bs4 import BeautifulSoup
baseUrl = 'https://www.tujidao.com/'
cookie = '7Dw1Tw3Bh2Mvfr=; UM_distinctid=173f0c5bc3717e-09b6cf2e7e2015-3972095d-1fa400-173f0c5bc38b44; 7Dw1Tw3Bh2Mvu%5Fleixing=3; 7Dw1Tw3Bh2Mvu%5Fpw=84f05029abccc09a; 7Dw1Tw3Bh2Mvu%5Fusername=asdf0823; 7Dw1Tw3Bh2Mvu%5Fid=229195; ASPSESSIONIDCWDQSQRQ=DHMOPECDLLEHFEBKIGHCBHKI; CNZZDATA1257039673=454938172-1597469558-%7C1597474969'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.tujidao.com',
    'Cookie': cookie
}
tags = []


def start():
    r = requests.get(baseUrl, verify=False, headers=headers)
    if(r.status_code == 200):
        soup = BeautifulSoup(r.text, 'lxml')
        tags = soup.select('div.tags > a')
        for a in tags:
            # tags.append({'name': a.text, 'url': a['href']})
            extractTag(a['href'])
            break


def extractTag(tagUrl):
    if(not(tagUrl.startswith('http') or tagUrl.startswith('https'))):
        tagUrl = baseUrl + tagUrl
        r = requests.get(tagUrl, verify=False, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        albums = soup.select('div.hezi ul li')
        authors = []
        for album in albums:
            print(album)
            # 标题
            biaoti = album.select_one('.biaoti')
            count = album.select_one('.shuliang')
            organization = album.select_one('p:nth-of-type(1) a')
            lables = album.select('p:nth-of-type(2) a')
            figure = album.select_one('p:nth-of-type(3) a')
            print(biaoti)
            print(count)
            print(organization)
            print(lables)
            print(figure)
            print({
                'title': biaoti.a.text,
                'url': biaoti.a['href'],
                'count': count.text[:-1],
                'organization': organization.text,
                'lables': '',
                'figure': figure.text,
                'figureUrl':figure['href'],
                'organizationUrl':organization['href'],
            })
        print(authors)


if __name__ == '__main__':
    start()
