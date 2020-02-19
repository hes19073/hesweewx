##https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnings_gemeinde_mvp.html
##https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnings_gemeinde.html#Gemeinde%20Klein%20Rogahn

#import requests
#from bs4 import BeautifulSoup

#set $getpage = requests.get('https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnings_gemeinde.html#Gemeinde%20Klein%20Rogahn')

#set $getpage_soup = BeautifulSoup($getpage.text, 'html.parser')

#set $all_id_para1 = $getpage_soup.findAll('h2', {'id':'Gemeinde Klein Rogahn'})

##for $para in $all_id_para1:
##set    print (para)
##  $para
##end for
##set $test_warn = $all_id_para1.prettify()
$all_id_para1
