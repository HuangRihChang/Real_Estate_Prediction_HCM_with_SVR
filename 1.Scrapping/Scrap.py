# -*- coding: utf-8 -*-
"""
Created on Sun May 07 11:39:59 2017

@author: Heo
"""
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup # To parse html text
import time


EnvironmentList = [long(398815066321257668988259), 
    long(6010592966479218379), 
    long(1785257969025739638638), 
    long(407688410680556161655654437286508202199965331047),
    long(7324944404327233889),
    long(8053861545573411769987900220416),
    long(7324944404312474478),
    long(1253544981520355813998),
    long(23337657136035692223428192288)]

EnvironmentList_weight = [0.8, 0.5, 0.8, 0.5, 0.2, 0.2, 0.8, 0.5, 0.85]

utilityList = [long(19637877408971420257),
    long(113056967532905),
    long(5611899790763210612),
    long(6396782650570236189510567929950356050636391),
    long(97015336072187352420604216977097273289372644634215),
    long(1571470410559908303490744810457179508),
    long(1466525289),
    long(6044514735612681582),
    long(1630907526034838660914466436771104)]

utilityList_weight = [0.5, 0.8, 0.3, 0.35, 0.5, 0.9, 0.35, 0.8, 0.4]

def write_file(fname, string):
    with open(fname, 'ab') as fout:
            fout.write(string)
            fout.write('\n')

def replace_file(fname, tupe):
    with open(fname, 'w') as fout:
        for i in tupe:
            fout.write(i)
            fout.write('\n')

def read_file(filename):
    tupe = []
    with open(filename, 'r') as f:
        content = f.readlines()
    for link in content:
        link = link.split('\n')[0]
        tupe.append(link)
    return tupe

def parse_html(url):
    html_content = requests.get(url).content
    return BeautifulSoup(html_content, 'html.parser')

def ASCII(s):
    x = 0
    for i in xrange(len(s)):
        x += ord(s[i])*2**(8 * (len(s) - i - 1))
    return x

def data_scrap(post_url):
    try:
        post_tree = parse_html(post_url)
    except:
        print 'Cannot read ' + post_url
        write_file("accept_error.txt", post_url)
        return None
    
    count = 0
    
    #Diện tích
    try:
        surface = post_tree.find(id='MainContent_ctlDetailBox_lblSurface').string
        if(surface != ''):
            surface = int(surface.split(' ')[0])
        else:
            count += 1
            surface = ''
    except:
        count += 1
        surface = ''
    
    #Giá
    try:
        tmp = post_tree.find(class_='price').text
        if(ASCII(unicode(tmp)) != long(86333734532808072716070260)):
            try:
                const = int(tmp.split(' ')[0].split(',')[0])*1.0 + int(tmp.split(' ')[0].split(',')[1])*0.1
            except:
                const = int(tmp.split(' ')[0])*1.0
            ty = long(29431)
            if(ASCII(unicode(tmp).split(' ')[1]) == ty):
                price = (const*1000000000)/surface
            else:
                price = (const*1000000)/surface
        else:
            print 'have no price'
            write_file("no_price.txt", post_url)
            return None
    except:
        print 'have no price'
        write_file("no_price.txt", post_url)
        return None
        
    #Tình trạng pháp lý
    try:
        Legalstt = post_tree.find(id='MainContent_ctlDetailBox_lblLegalStatus').string
        if(Legalstt != None):
            if(ASCII(unicode(Legalstt)) == long(396513421505342481524512)):
                Legal = [1,0,0] #Sổ Hồng
            else:
                if(ASCII(unicode(Legalstt)) == long(125160198754080)):
                    Legal = [0,1,0] #Sổ Đỏ
                else:
                    Legal = [0,0,1] #Có giấy phép xây dựng
        else:
            count += 1
            Legal = ''
    except:
        count += 1
        Legal = ''
        
    #Số Tầng
    if(post_tree.find(id='MainContent_ctlDetailBox_lblFloor').string != None):
        floor = int(post_tree.find(id='MainContent_ctlDetailBox_lblFloor').string)
    else:
        count += 1
        floor = ''
        
    #Số Phòng Tắm
    if(post_tree.find(id='MainContent_ctlDetailBox_lblBathRoom').string != None):
        bathRoom = int(post_tree.find(id='MainContent_ctlDetailBox_lblBathRoom').string)
    else:
        count += 1
        bathRoom = ''
        
    #Số Phòng Ngủ
    if(post_tree.find(id='MainContent_ctlDetailBox_lblBedRoom').string != None):
        bedRoom = int(post_tree.find(id='MainContent_ctlDetailBox_lblBedRoom').string)
    else:
        count += 1
        bedRoom = ''
        
    #Tiện ích
    utility = ''
    getlist = post_tree.find(id='MainContent_ctlDetailBox_lblUtility').text
    if(getlist != ''):
        getlist = getlist.split('  ')
        for i in getlist:
            utility += i + ','
        
    #Môi trường xung quanh
    environment = ''
    getlist = post_tree.find(id='MainContent_ctlDetailBox_lblEnvironment').text
    if(getlist != ''):
        getlist = getlist.split('  ')
        for i in getlist:
            environment += i + ','
        
    #Quận
    district = unicode(post_tree.find(id='MainContent_ctlDetailBox_lblDistrict').find('a').string)

    #Phường
    ward = unicode(post_tree.find(id='MainContent_ctlDetailBox_lblWard').find('a').string)
        
    #Loại hình bán (nhà phố, biệt thự, khác)
    try:
        kind = post_tree.find_all(itemprop="title")[1].string
    except:
        count += 1
        kind = ''
        
    coordinates = []
    Loc = post_tree.find(id="MainContent_ctlDetailBox_lblMapLink").find('a')['href'].split(':')[2].split(',')
    for l in Loc:
        coordinates.append(float(l))
    if(coordinates[0] == 0.0):
        count += 1
    if(count >1):
        print 'Missing ' + str(count) + ' fields, No adapt mining data request!'
        return None
    else:
        print 'Missing ' + str(count) + ' fields'
        return district, ward, coordinates, kind, Legal, surface, floor, bedRoom, bathRoom, environment, utility, price



def main(bb):
    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('kind', type=str, help='...')
    args = parser.parse_args()

    if args.kind not in ['getlink', 'scrapping']:
        raise ValueError("kind must be 'getlink' or 'scrapping'")


    if(args.kind == 'getlink'):
    #if(bb == 1):
        tree = parse_html('http://www.muabannhadat.vn/nha-ban-3513/tp-ho-chi-minh-s59?sf=dpo&so=d&p=0')
        num_posts = int(tree.find(id='MainContent_ctlList_ctlResults_lblCount').strong.string.replace(".", ""))
        num_pages = (num_posts - 1) / 10 + 1
        print 'we found', num_pages, 'pages for', num_posts, 'posts'
        rage = 0/10
        try:
            links = read_file("link.txt")
            rage = len(links)/10
        except:    
            rage = 0/10

        num = rage
        for num in range(rage, num_pages):
            url = 'http://www.muabannhadat.vn/nha-ban-3513/tp-ho-chi-minh-s59?sf=dpo&so=d&p=' + str(num)
            search_tree = parse_html(url)
            posts_set_result = search_tree.find_all(class_='resultItem')
            for post in posts_set_result:
                post_url = 'http://www.muabannhadat.vn' + post.find('a')['href']
                write_file("link.txt", post_url)
            posts_set_result = []
            print 'Page ' + str(num)
            num += 1
            time.sleep(3)
        
    
    if(args.kind == 'scrapping'):
    #if(bb == 2):
        linkstupe = read_file("link.go.txt")
        data = []
        try:
            df = pd.DataFrame.from_csv('data_muabannhadat.csv')
        except:
            df = pd.DataFrame(columns=['district','ward','coordinates','kind','Legal','surface','floor','bedRoom','bathRoom','environment','utility','price'])
            df.to_csv('data_muabannhadat.csv', encoding='utf-8')
        for link in linkstupe:    
            data_cell = data_scrap(link)
            if(data_cell != None):
                data.append(data_cell)
                df2 = pd.DataFrame(data, columns=['district','ward','coordinates','kind','Legal','surface','floor','bedRoom','bathRoom','environment','utility','price'])
                frames = [df, df2]
                df = pd.concat(frames, ignore_index=True)
                df.to_csv('data_muabannhadat.csv', encoding='utf-8')
                data = []
            linkstupe.remove(link)
            replace_file("link.go.txt", linkstupe)
            
            
if __name__ == '__main__':
    main(1)