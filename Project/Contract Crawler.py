# -*- coding: utf-8 -*-

import urllib2
import re
import time
import thread
import os

def work(name,start,end):
    page = start
    limit = end
    Pname = name
    #safeliblist = ['Crowdsale','FinalizableCrowdsale','PostDeliveryCrowdsale','RefundableCrowdsale','RefundVault','AllowanceCrowdsale','MintedCrowdsale']
    while page < limit:
        #print Pname + '->' + str(page) + '\n'
        if(page == limit - 1) :
            print Pname + '->' + 'page = ' + str(page) + '  last page starts' + '\n'
        else:
            print Pname + '->' + 'page = ' + str(page) + '\n'
        try:
            myUrl = "https://etherscan.io/contractsVerified/" + str(page)
            page += 1
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','accept-language': 'zh-CN,zh;q=0.9,en;q=0.8', 'cache-control': 'max-age=0','cookie': '__cfduid=dee5b32434e56a209c72b36827df099541524317377; ASP.NET_SessionId=b0pqo1yn5c2n3q330crw55cr; _ga=GA1.2.1239785349.1524317379; _gid=GA1.2.154284148.1524749879; __cflb=2883464440; cf_clearance=ed11fe73a1bb2f611f48ba3ee6468bd48053997f-1524796655-2700','User-Agent': user_agent}
            #user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'
            #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            #user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            #headers = {'User-Agent': user_agent}
            req = urllib2.Request(myUrl, headers=headers)
            myResponse = urllib2.urlopen(req)
            myPage = myResponse.read()
            myitem = re.findall(r'href=\'/address/(.*?)\' class=\'address-tag\'>', myPage, re.S)
            print myitem[0]

            myTxCount = re.findall(r'href=\'.*?\' class=\'address-tag\'>.*?<td>.*?<td>.*?<td>.*?<td>(.*?)</td>', myPage, re.S)
            myCP = re.findall(r'href=\'.*?\' class=\'address-tag\'>.*?<td>.*?<td>(.*?)</td>', myPage, re.S)
            #print myitem
            i = 0
            while i < len(myitem):
                try:
                    myUrl2 = "https://etherscan.io/address/" + myitem[i]
                    myTitle = myitem[i]
                    #title = myitem[i]
                    i += 1
                    #user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'
                    #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                    #user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
                    #headers = {'User-Agent': user_agent}
                    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
                    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','accept-language': 'zh-CN,zh;q=0.9,en;q=0.8', 'cache-control': 'max-age=0','cookie': '__cfduid=dee5b32434e56a209c72b36827df099541524317377; ASP.NET_SessionId=b0pqo1yn5c2n3q330crw55cr; _ga=GA1.2.1239785349.1524317379; _gid=GA1.2.154284148.1524749879; __cflb=2883464440; cf_clearance=ed11fe73a1bb2f611f48ba3ee6468bd48053997f-1524796655-2700','User-Agent': user_agent}
                    req = urllib2.Request(myUrl2, headers=headers)
                    myResponse = urllib2.urlopen(req)
                    myPage = myResponse.read()
                    myInfo = re.findall(r'<div id="dividcode">.*?<pre.*?>(.*?)</pre>', myPage, re.S)
                    myversion = re.findall(r'Compiler.*?Version.*?<td>\n(.*?)\n.*?</td>', myPage, re.S)
                    if (len(myInfo) == 0):
                        print 'spider error ' +  str(page - 1) + '-' + str(i - 1)
                    '''
                    myInfo = re.findall(r'pragma.*?solidity.*?;(.*?)</pre>', myPage, re.S)
                    if (len(myInfo) == 0):
                        myInfo = re.findall(r'<div id="dividcode">.*?<pre.*?>(.*?)</pre>', myPage, re.S)
                    if (len(myInfo) == 0):
                        myInfo = re.findall(r'<div id="dividcode">(.*?)</pre>', myPage, re.S)
                    myTitle = re.findall(r'<td>Contract Name:\s</td>\s<td>\s(.*?)\s</td>', myPage, re.S)
                    '''
                    if (myTitle):
                        title = myTitle
                        path1 = os.path.abspath('.')
                        path = path1 + '/' + title + '.txt'
                        if (os.path.exists(path)):
                            title = myTitle + ' ' + str(page - 1) + '-' + str(i - 1)
                    else:
                        #print len(myTitle)
                        title = 'page=' + str(page-1) + '  i=' + str(i-1)
                    #f = open(title + '.txt', 'w+')
                    if(len(myInfo) != 0):
                        list = myTitle.split('#')
                        #list2 = list[2].split('#')
                        title  = list[0]
                        if(len(myversion)!=0):
                            title = title + "+" + myversion[0]
                        f = open(title + '.txt', 'w+')
                        content = myInfo[0]
                        replace1 = re.sub(r'&gt;', '>', content)  # replace >
                        replace2 = re.sub(r'&lt;', '<', replace1)  # replace <
                        replace3 = re.sub(r'&quot;', '"', replace2)  # replace "
                        replace4 = re.sub(r'&amp;', '&', replace3)  # replace &
                        replace5 = re.sub(r'&nbsp;', ' ', replace4)  # replace space
                        replace6 = re.sub(r'&#39;', '\'', replace5)  # replace '
                        f.write(replace6)
                        print myitem[i - 1] + '   success   ' + Pname
                        f.close()
                    else:
                        l = open('loglogging.txt','a+')
                        errorinfo = title + ' can not get the info' + myitem[i - 1]
                        l.write(errorinfo)
                        l.write('\n')
                        print 'page=' + str(page-1) + '  i=' + str(i-1) + ' error'
                        l.close()
                    #f.write(myInfo[0])
                    #f.close()
                    #print myitem[i - 1] + '   success   ' + Pname
                except:
                    raise
                    print myitem[i - 1] + '   error   ' + Pname +'>>>' + myTitle[0] + '>>>' + myInfo[0]
        except Exception as e:
            raise
            print e
            print myUrl + '   error'
            #print myTitle + myInfo
        if(limit == page):
            print Pname + ' has finished'

try:
    thread.start_new_thread(work, ('Thread 1',1,101))
    #thread.start_new_thread(work, ('Thread 2',11,21))
    #thread.start_new_thread(work, ('Thread 3',21,31))
    #thread.start_new_thread(work, ('Thread 4',31,41))
    #thread.start_new_thread(work, ('Thread 5',41,51))
    #thread.start_new_thread(work, ('Thread 6',51,61))
    #thread.start_new_thread(work, ('Thread 7',61,71))
    #thread.start_new_thread(work, ('Thread 8',71,81))
    #thread.start_new_thread(work, ('Thread 9',81,91))
    #thread.start_new_thread(work, ('Thread 10',91,101))
except:
    print 'error thread failed'

print 'started Zzzzz'
time.sleep(100000)