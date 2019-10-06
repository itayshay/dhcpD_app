#!C:\Python\Python37-32\python

# # #!/usr/bin/python3.6

import cgi
import cgitb; cgitb.enable()  # for troubleshooting 
from array import *
import re
import ipaddress
import binascii
import os
import subprocess
import math # to round up divide results

#################################
# Writen By: Itay Shay
# ACS / ishay@airspan.com
#
#### Configuration Variable #####
#dhcpConfTmp = 'C:/Stuff/scripts/python/airspan-guiForDhcp/dhcp.conf.tmp'
dhcpConfTmp = os.path.join('C:/Stuff/scripts/python/airspan-guiForDhcp/', 'dhcp.conf.tmp')
#inputFile = 'C:/Stuff/scripts/python/airspan-guiForDhcp/dhcpd.conf'
inputFile = os.path.join('C:/Stuff/scripts/python/airspan-guiForDhcp/', 'dhcpd.conf')
#outputFile = 'C:/Stuff/scripts/python/airspan-guiForDhcp/editedF.conf'
outputFile = os.path.join('C:/Stuff/scripts/python/airspan-guiForDhcp/', 'editedF.conf')
# for linux:
#dhcpConfTmp = os.path.join('/tmp/', 'dhcpd.conf.tmp')
#inputFile = os.path.join('/etc/dhcp/', 'dhcpd.conf')
#outputFile = os.path.join('/etc/dhcp/', 'editedF.conf')
#################################

def validate_ipaddress(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError as errorCode:
        #uncomment below if you want to display the exception message.
        #print(errorCode)
        #comment below if above is uncommented.
        pass
        return False

# IPv6 format validation:
def val_ipv6(ipv6):
    try:
        addr = ipaddress.IPv6Address(ipv6)
    except ipaddress.AddressValueError:
        print(ipv6, 'is not a valid IPv6 address')
        return False
    else:
        if addr.is_multicast:
            print(ipv6, 'is an IPv6 multicast address')
            return False
        if addr.is_private:
            print(ipv6, 'is an IPv6 private address')
            return True
        if addr.is_global:
            print(ipv6, 'is an IPv6 global address')
            return True
        if addr.is_link_local:
            print(ipv6, 'is an IPv6 link-local address')
            return True
        if addr.is_site_local:
            print(ipv6, 'is an IPv6 site-local address')
            return True
        if addr.is_reserved:
            print(ipv6, 'is an IPv6 reserved address')
            return True
        if addr.is_loopback:
            print(ipv6, 'is an IPv6 loopback address')
            return True
        if addr.ipv4_mapped:
            print(ipv6, 'is an IPv6 mapped IPv4 address')
            return True
        if addr.sixtofour:
            print(ipv6, 'is an IPv6 RFC 3056 address')
            return True
        if addr.teredo:
            print(ipv6, 'is an IPv6 RFC 4380 address')
            return True

# Verify Mac format
def checkMAC(x):
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower()): return 1;
    else: return 0;

# copy editedDhcpd.conf file to replace /etc/dhcpd.conf
def replaceDhcpdFile(cmd):
    #print ("CMD = ", cmd)
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=False)
    return (p.stdin, p.stdout, p.stderr)

# Restart dhcpd every dhcpd.conf file change ("service dhcpd restart") 
def restartDhcpd(cmd):
    #print ("CMD = ", cmd)
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=False)
    return (p.stdin, p.stdout, p.stderr)

# open dhcpd.conf:
filename = inputFile
f = open(filename, 'r') 

# find the number of hosts and the max custom options in host
# remove "CUSTOM_OPTIONS" string lines from file
editf = open(dhcpConfTmp, 'w')
fi = open(filename, 'r'); numHosts = 0 ; numoptions=0 ; numSubnets = 0 ; numOfIpSecHosts=0;
for l in fi:
    if l.startswith("host"): numHosts += 1
    if not re.search(r'.*.CUSTOM_OPTIONS.*\n',l):
        editf.write(l)
    if l.startswith("subnet"): numSubnets += 1
    if "if (substring" in l: numOfIpSecHosts += 1
fi.close()
editf.close()

hostsMacList = list(range(0,numHosts))
hostDescList = list(range(0,numHosts))
ipAddrList = list(range(0,numHosts))
dhcpClientIdentifier = list(range(0,numHosts))
hostTypeList = list(range(0,numHosts))
hostMac = ''
netmaskList = list(range(0,numSubnets))
subnetList = list(range(0,numSubnets))
ipsecHostsMacList = list(range(0,numOfIpSecHosts))
ipsecHostsDescList = list(range(0,numOfIpSecHosts))
ipsecHostsOptionsList = list(range(0,numOfIpSecHosts))
hostTypeList2 = list(range(0,numOfIpSecHosts))


# 2D array for hosts/custom-options
items, lists = 24, numHosts;
HostOptions = [["" for w in range(items)] for r in range(lists)]
x=0 ; j=0
items2, lists2 = 54, numSubnets;
ipsecHostsMacList = [["" for w in range(items2)] for r in range(lists2)]
ipsecHostsDescList = [["" for w in range(items2)] for r in range(lists2)]
ipsecHostsOptionsList = [["" for w in range(items2)] for r in range(lists2)]

regDhcpClietId = re.compile(r'[0-9]{15}$') # IMSI
regDhcpClietId2 = re.compile(r'([0-9][0-9]:){11}[0-9][0-9]') # mac converted to hex

def ascii2HexConverter(mac2Convert):
    #ch = "00:a0:0a:2d:6f:fe"
    ascii2hex = (str(binascii.hexlify(mac2Convert.encode()))).strip("b").strip("'")
    t = iter(ascii2hex)
    macConverted = ":".join(str(a+b) for a,b in zip(ascii2hex[::2], ascii2hex[1::2]))
    print ("ascii2hex, macConverted = ",ascii2hex ,  macConverted)
    return macConverted

fTmp = open(dhcpConfTmp, 'r')

for i, line in enumerate(fTmp):
    if line.startswith("host"):
        # print ("Host Is =", line)
        f2 = open(dhcpConfTmp, 'r'); lines=f2.readlines()
        hostDescList[x] = line.split(' ')[1] ; # print ("HostDescList =", hostDescList[x])
        hostTypeList[x] = 'eNB / Other' ;# other hosts
        for k in range(i+1,i+11):
            # print ("K is =", k)
            if "hardware ethernet" in lines[k]:
                hostsMacList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("hostsMacList =", hostsMacList[x])
            if "fixed-address" in lines[k]:
                ipAddrList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("ipAddrList =", ipAddrList[x])
            if "dhcp-client-identifier" in lines[k]:
                dhcpClientIdentifier[x] = lines[k].split(' ')[-1].strip().strip(";").strip("\"").replace("\\000",''); # print ("dhcp-client-identifier[x] =" , dhcpClientIdentifier[x])
                if regDhcpClietId.match(str(dhcpClientIdentifier[x])):
                    hostTypeList[x] = "Relay" ;# relay host
                elif regDhcpClietId2.match(str(dhcpClientIdentifier[x])):
                    hostTypeList[x] = "eNB of Relay" ;# enb (of relay) host
            if "fixed-address" in lines[k]:
                # linForOptions=f2.readlines()
                for q in range(k+1,k+24):
                    if "}" in lines[q]: j=0; break;
                    HostOptions[x][j] = str(lines[q].strip('\t')) ;
                    j+=1 ;
            if "}" in lines[k]:
                break
        x+=1; # incremented for each line with "host"
        f2.close()
fTmp.close()

def sortFunc(sBy):
    newList = []
    tmpList = []
    if sBy == " MAC ":
        for i in range(len(subnetList)):
            for j in range(len(ipsecHostsMacList)):
                if ipsecHostsMacList[i][j]:
                    tmpList.append(ipsecHostsMacList[i][j])
        for val in hostsMacList:
            tmpList.append(val)
        for e in sorted(tmpList):
            newList.append(e) ;
        # print ("newList = ", newList)
        return newList
    if sBy == " DESCIRPTION ":
        for e in sorted(hostDescList):
            newList.append(e) ;
        return newList
    #print ("newList = ", newList)


x=0 ; j=0
fTmp = open(filename, 'r')
for i, line in enumerate(fTmp):
    if line.startswith("subnet"):
        f = open(filename, 'r'); lines=f.readlines()
        # print ("subnet in line = ", line)
        splitlen = len(line.split(' ')) ; # print ("splitlen = ", splitlen)
        subnetList[x] = line.split(' ')[-(splitlen-1)]
        netmaskList[x] = line.split(' ')[-2]
        # print ("subnetList / netmaskList = ", subnetList[x], netmaskList[x])
        for k in range(i+1,i+70):
            if lines[k].startswith("}"): break
            if lines[k].startswith("    if (substring"):
                for q in range(k,k+4):
                    if "}" in lines[q]: j=0; break
                    if lines[q].startswith("    if (substring"):
                        ipsecHostsMacList[x][j] = lines[q].split('=')[-1].split(")")[0]; #print ("ipsecHostsMacList =", ipsecHostsMacList[x][j])
                        ipsecHostsDescList[x][j] = lines[q].split(' ')[-1].strip('\n'); #print ("ipsecHostsDescList =", ipsecHostsDescList[x][j])
                        hostTypeList2[x] = "IPsec Host"
                    if "option" in lines[q]:
                        ipsecHostsOptionsList[x][j] = str(lines[q].strip(' ').strip('\n')); #print ("ipsecHostsOptionsList = ", ipsecHostsOptionsList[x][j])
                        j+=1; break
                if lines[k].startswith("}"):
                    # print ("### end subnet }, BREAK");
                    break
        x+=1; f.close()
fTmp.close()

# print ("dhcp-client-identifier =" , dhcpClientIdentifier)

# find x/y position of an inde from 2D list
def findPosition(val):
    for i in range(len(subnetList)):
        for j in range(len(ipsecHostsMacList)):
            if val in (ipsecHostsMacList[i][j] or ipsecHostsDescList[i][j] or subnetList[i]):
                postn=[i,j] ;
                print ("postn = ", postn)
                return postn ; break

# find position in 1D list (for sorting)
def findPos2(val, list):
    for i in range(len(list)):
        if val in list[i]:
            postn2=i ;
            #print ("pos is %s , for val %s " %(postn2,val) )
            return postn2 ; break

# Duplicate IP validation
def checkIpExistance(ipChos,indicator):
    if indicator == 0 or indicator:
        ip = ipAddrList[indicator]
        # print ("ip and ipChos = ", ip , ipChos)
        if ipChos not in ipAddrList or ip == ipChos:
            return True
        else:
            return False
    else: return True

def checkDescriptipnExist(hostDescChos,indicator):
    # print ("Checking if Desc exist or not, indicator =", indicator)
    if indicator == 0 or indicator:
        hostDescrip = hostDescList[indicator]
        # print ("hostDescrip / hostDescChos" ,hostDescrip , hostDescChos)
        if hostDescChos not in hostDescList or hostDescrip == hostDescChos:
            #print ("RETURN TRUE 1")
            return True
        else:
            #print ("RETURN FALSE")
            return False
    elif hostDescChos not in hostDescList:
        #print ("RETURN TRUE 2")
        return True
    else:
        #print ("RETURN FALSE 2")
        return False

# examine special characters in description or custom_options
def examSpecialCharInStr(string): 
    if string:
        stringReg = re.compile('[@!#$%^&*()<>?\|}{~]')      
        if(stringReg.search(string) == None):
            #print("String is accepted")
            return True
        else: 
            #print("String is not accepted.", string)
            return False
    else: return True

# examine imsi format
def imsiFormatValid(imsi):
    if imsi:
        imsiReg = re.compile('[0-9]{15}$')      
        if imsiReg.match(imsi):
            #print("correct imsi format")
            return True
        else: 
            #print("wrong imsi format")
            return False
    else:
        #print("no imsi, return true.")
        return True

# Duplicate imsi validation
def duplicateImsi(imsiChos,indicator):
    if indicator == 0 or indicator:
        imsi = dhcpClientIdentifier[indicator]
        # print ("imsi and imsiChos = ", imsi , imsiChos)
        if imsiChos not in dhcpClientIdentifier or imsi == imsiChos:
            #print ("imsi not in list OR imsi not the same as previus")
            return True
        else:
            #print ("imsi in list OR imsi is the same as previus")
            return False
    else:
        # print ("no indicator, new host")
        return True    

print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title>DHCPv4 Hosts</title></head>")
print ('<body style=\"background-color:#E8F6F3;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"      All Hosts List "'</font></h1>')
# print (' <style><img src="img.jpg" alt="somthing about pic" width="100" height="100"></style> ')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #FDF2E9; background-color: #85C1E9;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')

form = cgi.FieldStorage()
# print ('<p>' "debugging: form is: " + str(form) + '</p>'); # linux

ind, indY = '', '';

# check if val2search is in one of the relevant lists
def searchListFunc(val2Check, List2Check):
    valExist=0
    for v in List2Check:
        if val2Check in str(v):
            # print ("VAL %s FOUND IN LIST" %(val2Check))
            valExist=1
            return True
    if valExist:
        return True
    else:
        return False    

def printRowFound(ind):
    print ('<td>'+str(hostsMacList[ind])+'</td> <td>'+str(hostDescList[ind])+'</td><td>'+str(ipAddrList[ind])+ '</td>')
    if str(hostTypeList[ind]) == "eNB / Other":
        print ('<td><a href="otherHosts.py" target="home">eNB / Other </a></td></tr>')
    if str(hostTypeList[ind]) == "Relay":
        print ('<td><a href="relayHosts.py" target="home">Relay Host </a></td></tr>')
    if str(hostTypeList[ind]) == "eNB of Relay":
        print ('<td><a href="enbOfRelayHosts.py" target="home">eNB (of Relay) Host </a></td></tr>');

# Host Chosen for Search
if form.getvalue("valToSearch"):
    print ('<form method="post" action="hosts.py">')
    val2Search = form.getvalue("valToSearch")
    # indexList = list(range(0,40)) ; x=0
    # table border style
    print ('<style>table {border-style: ridge;  border-width: 2px; '
           'border-color: #FDF2E9; background-color: #B48DF0;} th  '
           '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')
    valFound=0
    print ('<h2><font color=\"#9A7D0A\"> # Search Results For "' +val2Search+ '" : </font></h2>')
    if searchListFunc(val2Search, hostDescList) or searchListFunc(val2Search, hostsMacList) or searchListFunc(val2Search, ipAddrList):
        print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS (or Subnet/Netmask) |</th><th>| Host Type |</th></tr><tr>")
        valFound=1
        if searchListFunc(val2Search, hostDescList):
            for index, item in enumerate(hostDescList):
                if val2Search in item:
                    printRowFound(index)
        elif searchListFunc(val2Search, hostsMacList):
            for index, item in enumerate(hostsMacList):
                if val2Search in item:
                    printRowFound(index)
        elif searchListFunc(val2Search, ipAddrList):
            for index, item in enumerate(ipAddrList):
                if val2Search in str(item):
                    printRowFound(index)
        # print ("</tr></table>")
    if (val2Search in subl for subl in ipsecHostsMacList) or (val2Search in subl for subl in ipsecHostsDescList) or searchListFunc(val2Search, subnetList):
        if not valFound: print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS (or Subnet/Netmask) |</th><th>| Host Type |</th></tr><tr>")
        valFound=1 ; indX=0; indY=0
        if searchListFunc(val2Search, subnetList):
            # print ("subnetList")
            for index, item in enumerate(subnetList):
                if val2Search in item:
                    for x, q in enumerate(ipsecHostsMacList):
                        if str(ipsecHostsMacList[index][x]):
                            print ('<td>'+str(ipsecHostsMacList[index][x])+'</td> <td>'+str(ipsecHostsDescList[index][x])+'</td> <td>'+str(subnetList[index])+ ' / ' +str(netmaskList[index])+'</td>')
                            print ('<td><a href="ipsecHosts.py" target="home">IPsec Host </a></td></tr>')
        if (val2Search in sul for sul in ipsecHostsMacList):
            #print ("ipsecHostsMacList")
            for index, item in enumerate(ipsecHostsMacList):
                for indY, dd in enumerate(item):
                    if val2Search in dd:
                        print ('<td>'+str(ipsecHostsMacList[index][indY])+'</td> <td>'+str(ipsecHostsDescList[index][indY])+'</td> <td>'+str(subnetList[index])+ ' / ' +str(netmaskList[index])+'</td>')
                        print ('<td><a href="ipsecHosts.py" target="home">IPsec Host </a></td></tr>')
        if (val2Search in subl for subl in ipsecHostsDescList):
            #print ("ipsecHostsDescList")
            for index, item in enumerate(ipsecHostsDescList):
                for indY, dd in enumerate(item):
                    if val2Search in str(dd):
                        print ('<td>'+str(ipsecHostsMacList[index][indY])+'</td> <td>'+str(ipsecHostsDescList[index][indY])+'</td> <td>'+str(subnetList[index])+ ' / ' +str(netmaskList[index])+'</td>')
                        print ('<td><a href="ipsecHosts.py" target="home">IPsec Host </a></td></tr>')
    print ("</tr></table>")
    if not valFound:
        print ('<h2><font color=\"#9A7D0A\"> ## ALERT: ## COULDN\'T FIND REQUESTED VALUE, PLEASE TRY AGAIN ## </font></h2>')
    #print ("</tr></table>")
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


# Printing Table
if not form.getvalue("valToSearch") and not form.getvalue("SubmitChanges"):
    print ('<form method="post" action="hosts.py">')
    #print ('<p> ## =========================================================================== ## </p>')
    print ('<font color=\"#0000FF\">&#160# Search Host by: ( MAC / IP / DESCRIPTION / SUBNET ) <input type="text" name="valToSearch"/></font>')
    print ('<input type="submit" value="Search Host "/><br>')
    print ('<p></p>') ; print ('<p></p>') ; y=0
    divider = 22
    divL = int((len(hostsMacList)+len(ipsecHostsMacList))/divider ) ; # print  ("divL = ", divL)
    divH = math.ceil(( (len(hostsMacList)+len(ipsecHostsMacList))/divider )) ; # print ("divH rounded up = ", divH)
    for i in range(1, divL+1):
        RL1 = 0+(int(i-1)*divider) ; RH1 = 0+(int(i)*divider)
        print ('<input type = "submit" name = "tableRange" value ='"Range"+str(RL1)+'-'+str(RH1)+'>')
        if i == (divL):
            RL1 = (int(i)*divider) ; RH1 = ((int(i+1)*divider)-((int(i+1)*divider)-(len(hostsMacList)+len(ipsecHostsMacList)))-3)
            print ('<input type = "submit" name = "tableRange" value ='"lRange"+str(RL1)+'-'+str(RH1)+'>')
            #print ("i, RL1 , RH1 =", i, RL1, RH1)
    print ("<table><tr><th>| # |</th><th> <input type = \"submit\" name = \"listToSortBy\" value =\" MAC \""
           "</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS (or Subnet/Netmask) |</th><th>| Host Type |</th></tr><tr>")
    if form.getvalue("tableRange"):
        RL = form.getvalue("tableRange").split("-")[0].strip("l").strip("Range")
        RH = form.getvalue("tableRange").split("-")[-1]
        RLt, RHt = 0, 0
        #print ("RL, RH, RLt , RHt = ", RL, RH, RLt, RHt);
        # print ("tableRange, RL, RH = ", form.getvalue("tableRange"), RL, RH)
        if "l" in str(form.getvalue("tableRange")):
            RLt = 0 ; RHt = (len(ipsecHostsMacList)-2)
            RH=int(RH)-int(RHt)
            #print ("RL, RH, RL2 , RH2 = ", RL, RH, RLt, RHt)
        for y in range(int(RL), int(RH)+1):
            print ('<td>' +str(y)+ '</td><td>'+str(hostsMacList[y])+'</td> <td>'+str(hostDescList[y])+'</td><td>'+str(ipAddrList[y])+ '</td>')
            if str(hostTypeList[y]) == "eNB / Other":
                print ('<td><a href="otherHosts.py" target="home">eNB / Other </a></td></tr>') 
            if str(hostTypeList[y]) == "Relay":
                print ('<td><a href="relayHosts.py" target="home">Relay Host </a></td></tr>')
            if str(hostTypeList[y]) == "eNB of Relay":
                print ('<td><a href="enbOfRelayHosts.py" target="home">eNB (of Relay) Host </a></td></tr>');
        for i in range(len(subnetList)):
            for j in range(int(RHt)):
                if ipsecHostsMacList[i][j]:
                    # print ("ipsecHostsMacList[i][j] = %s, i = %s, j = %s" %(i,j,ipsecHostsMacList[i][j]))
                    print ('<td>' +str(y+1+j)+ '</td><td>'+str(ipsecHostsMacList[i][j])+'</td> <td>'+str(ipsecHostsDescList[i][j])+'</td> <td>'+str(subnetList[i])+ ' / ' +str(netmaskList[i])+'</td>')
                    if str(hostTypeList2[i]) == "IPsec Host":
                        print ('<td><a href="ipsecHosts.py" target="home">IPsec Host </a></td></tr>')
    else: # no range, print entire table
        # print ("<font color=\"#FF4500\"><h2> All Hosts List: </h2></font>")
        listToSortBy = form.getvalue("listToSortBy") ; # print ("listToSortBy = %s " %(listToSortBy))
        sortList=''
        posList = ''
        if listToSortBy == " MAC ":
            sortList = sortFunc(listToSortBy)
            posList = hostsMacList
            #pos = findPos2(valFromList,hoststList) ; print ("pos is %s , for valFromList %s " %(pos,valFromList))
            # print (sortList)
        elif listToSortBy == " DESCIRPTION  ":
            sortList = sortFunc(listToSortBy)
            posList = hostDescList
            #pos = findPos2(valFromList,hoststList) ; print ("pos is %s , for valFromList %s " %(pos,valFromList))
            # print (sortList)
        else:
            sortList=hostsMacList
        for y, valFromList in enumerate(sortList):
            pos = findPos2(valFromList,posList) ; # print ("pos is %s , for valFromList %s " %(pos,valFromList))
            if pos: y=pos
            print ('<td>' +str(y)+ '</td><td>'+str(hostsMacList[y])+'</td> <td>'+str(hostDescList[y])+'</td><td>'+str(ipAddrList[y])+ '</td>')
            if str(hostTypeList[y]) == "eNB / Other":
                print ('<td><a href="otherHosts.py" target="home">eNB / Other </a></td></tr>') 
            if str(hostTypeList[y]) == "Relay":
                print ('<td><a href="relayHosts.py" target="home">Relay Host </a></td></tr>')
            if str(hostTypeList[y]) == "eNB of Relay":
                print ('<td><a href="enbOfRelayHosts.py" target="home">eNB (of Relay) Host </a></td></tr>')
        for i in range(len(subnetList)):
            for j in range(len(ipsecHostsMacList)):
                if ipsecHostsMacList[i][j]:
                    print ('<td>' +str(y+1+j)+ '</td><td>'+str(ipsecHostsMacList[i][j])+'</td> <td>'+str(ipsecHostsDescList[i][j])+'</td> <td>'+str(subnetList[i])+ ' / ' +str(netmaskList[i])+'</td>')
                    if str(hostTypeList2[i]) == "IPsec Host":
                        print ('<td><a href="ipsecHosts.py" target="home">IPsec Host </a></td></tr>')
    print ("</tr></table>") 
print ("</form>")
print ("</body>")
print ("</html>")

