#!C:\Python\Python37-32\python

# # #!/usr/bin/python3.6

import cgi
# import cgitb; cgitb.enable()  # for troubleshooting, comment-out if linux server
from array import *
import re
import ipaddress
import binascii
import os
import subprocess

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
# Or: Restart dhcpd every dhcpd.conf file change ("service dhcpd restart") 
def executeCmd(cmd):
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
fi = open(filename, 'r'); numHosts = 0 ; numoptions=0 ; numSubnets = 0 ; numOfIpSecHosts=0; numOptions=0
for l in fi:
    if l.startswith("host"): numHosts += 1
    if not re.search(r'.*.CUSTOM_OPTIONS.*\n',l):
        editf.write(l)
    if l.startswith("subnet"): numSubnets += 1
    if "if (substring" in l: numOfIpSecHosts += 1
    if l.startswith("option "): numOptions += 1
fi.close()
editf.close()

hostsMacList = list(range(0,numHosts))
hostDescList = list(range(0,numHosts))
ipAddrList = list(range(0,numHosts))
dhcpClientIdentifier = list(range(0,numHosts))
hostMac = ''
hostTypeList = list(range(0,numHosts))
netmaskList = list(range(0,numSubnets))
subnetList = list(range(0,numSubnets))
ipsecHostsMacList = list(range(0,numOfIpSecHosts))
ipsecHostsDescList = list(range(0,numOfIpSecHosts))
ipsecHostsOptionsList = list(range(0,numOfIpSecHosts))
hostTypeList2 = list(range(0,numOfIpSecHosts))
optionsList = list(range(0,numOptions))

# 2D array for hosts/custom-options
items, lists = 24, numHosts;
HostOptions = [["" for w in range(items)] for r in range(lists)]
x=0 ; j=0
items2, lists2 = 54, numSubnets;
ipsecHostsMacList = [["" for w in range(items2)] for r in range(lists2)]
ipsecHostsDescList = [["" for w in range(items2)] for r in range(lists2)]
ipsecHostsOptionsList = [["" for w in range(items2)] for r in range(lists2)]

regDhcpClietId = re.compile(r'[0-9]{15}$')
regDhcpClietId2 = re.compile(r'([0-9][0-9]:){11}[0-9][0-9]')

def ascii2HexConverter(mac2Convert):
    #ch = "00:a0:0a:2d:6f:fe"
    ascii2hex = (str(binascii.hexlify(mac2Convert.encode()))).strip("b").strip("'")
    t = iter(ascii2hex)
    macConverted = ":".join(str(a+b) for a,b in zip(ascii2hex[::2], ascii2hex[1::2]))
    # print ("ascii2hex, macConverted = ",ascii2hex ,  macConverted)
    return macConverted

fTmp = open(dhcpConfTmp, 'r')

for i, line in enumerate(fTmp):
    if line.startswith("host"):
        # print ("Host Is =", line)
        f2 = open(dhcpConfTmp, 'r'); lines=f2.readlines()
        hostDescList[x] = line.split(' ')[1] ; # print ("HostDescList =", hostDescList[x])
        hostTypeList[x] = '3' ;# other hosts
        for k in range(i+1,i+11):
            # print ("K is =", k)
            if "hardware ethernet" in lines[k]:
                hostsMacList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("hostsMacList =", hostsMacList[x])
            if "fixed-address" in lines[k]:
                ipAddrList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("ipAddrList =", ipAddrList[x])
            if "dhcp-client-identifier" in lines[k]:
                dhcpClientIdentifier[x] = lines[k].split(' ')[-1].strip().strip(";").strip("\"").replace("\\000",''); # print ("dhcp-client-identifier[x] =" , dhcpClientIdentifier[x])
                if regDhcpClietId.match(str(dhcpClientIdentifier[x])):
                    hostTypeList[x] = "1" ;# relay host
                elif regDhcpClietId2.match(str(dhcpClientIdentifier[x])):
                    hostTypeList[x] = "2" ;# enb (of relay) host
            if "fixed-address" in lines[k]:
                # linForOptions=f2.readlines()
                for q in range(k+1,k+24):
                    if "}" in lines[q]: j=0; break;
                    HostOptions[x][j] = str(lines[q].strip('\t')) ;
                    # print ("lines[q] = ", lines[q].strip('\t'), '\t' )
                    # currentOption = HostOptions[x][j]
                    # print ("HostOptions[x][j] x, j  = " ,j ,x , currentOption)
                    j+=1 ;
            if "}" in lines[k]:
                break
        x+=1; # incremented for each line with "host"
        f2.close()
fTmp.close()

#print ("hostTypeList =" , hostTypeList)

# db for ipsec Hosts:
x=0 ; j=0
fTmp = open(filename, 'r')
for i, line in enumerate(fTmp):
    if line.startswith("subnet"):
        f = open(filename, 'r'); lines=f.readlines()
        # print ("subnet in line = ", line)
        splitlen = len(line.split(' '))
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

x=0
fil = open(filename, 'r')
for line in fil:
    if line.startswith("option "):
        if line.startswith("host"): break
        if "space" in line:
            optionsList[x] = line.split(' ')[2].replace(';','');  # print ("optionsList[x] =", optionsList[x])
        else:
            optionsList[x] = line.split(' ')[1];  # print ("optionsList[x] =", optionsList[x])
        x+=1;
fil.close()

# Duplicate IP validation
def checkIpExistance(ipChos,indicator):
    #print ("ipChos,indicator = ", ipChos, indicator)
    if indicator == 0 or indicator:
        ip = ipAddrList[indicator]
        #print ("ip and ipChos = ", ip , ipChos)
        if ipChos not in ipAddrList or ip == ipChos:
            #print ("return TRUE1")
            return True
        else:
            return False
    elif ipChos not in ipAddrList:
        #print ("return TRUE2 - NO IND, IP not in ipList")
        return True
    else:
        #print ("return FALSE")
        return False

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

op = list(range(0,22)) # tmp
def custumOptionsValidation(val):
    ok=0
    # print ("custumOptionsValidation, vali is = ", val)
    options =''
    if val:
        options = val.split('\n')
    else:
        return True
    opLen = len(options) ; print ("opLen = ", opLen)
    for opL in options:
        if not opL:
            # print ("EMPTY line")
            opLen-=1
    for option in options:
        opTmp = option.replace('\n','').replace('\r','').replace('\t','')
        if opTmp and opTmp.count("option") == 1:
            op = opTmp.split(' ')[5]
            # print ("op = ", op)
            for valFromList in optionsList:
                if op in valFromList:
                    # print (" ## OP %s is in valFromList %s " %(op,valFromList))
                    ok+=1
    if ok == opLen:
        #print (" All options are ok ")
        return True
    else:
        #print (" Some options are wrong")
        return False


print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title>DHCPv4 Hosts</title></head>")
print ('<body style=\"background-color:#E8F6F3;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"      Relay Hosts     "'</font></h1>')
# print (' <style><img src="img.jpg" alt="somthing about pic" width="100" height="100"></style> ')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #FDF2E9; background-color: #EDBB99;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')

form = cgi.FieldStorage()
# print ('<p>' "debugging: form is: " + str(form) + '</p>');

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
    print ('<td><input type = "submit" name = "hostMacChosen" value =' +str(hostsMacList[ind])+ ' </td></tr>')

# Host Search Pressed
if form.getvalue("valToSearch"):
    print ('<form method="post" action="relayHosts.py">')
    val2Search = form.getvalue("valToSearch")
    print ('<style>table {border-style: ridge;  border-width: 2px; '
           'border-color: #FDF2E9; background-color: #B48DF0;} th  '
           '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')
    print ('<h2><font color=\"#9A7D0A\"> # Search Results For "' +val2Search+ '" : </font></h2>')
    if searchListFunc(val2Search, hostDescList) or searchListFunc(val2Search, hostsMacList) or searchListFunc(val2Search, ipAddrList):
        print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS |</th><th>| EDIT LINK |</th></tr><tr>")
        if searchListFunc(val2Search, hostDescList):
            for index, item in enumerate(hostDescList):
                if val2Search in item:
                    if int(hostTypeList[index]) == 1: printRowFound(index)
        elif searchListFunc(val2Search, hostsMacList):
            for index, item in enumerate(hostsMacList):
                if val2Search in item:
                    if int(hostTypeList[index]) == 1: printRowFound(index)
        elif searchListFunc(val2Search, ipAddrList):
            for index, item in enumerate(ipAddrList):
                if val2Search in str(item):
                    if int(hostTypeList[index]) == 1: printRowFound(index)
        print ("</tr></table>")
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## ALERT: ## COULDN\'T FIND REQUESTED VALUE, PLEASE TRY AGAIN ## </font></h2>')
    # print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Edit Link pressed:
if form.getvalue("hostMacChosen"):
    print ('<form method="post" action="relayHosts.py">')
    hostMac = form.getvalue("hostMacChosen")
    # Validate mac format
    if checkMAC(hostMac):
        # print ("MAC is OK")
        # Check if host chosen (1) exists, for editing or.. (2) new to create new:
        if hostMac in hostsMacList:
            print ('<h2> # Host Mac Chosen is: ' + hostMac +  "  </h2>")
            ind = hostsMacList.index(hostMac) ; # print ("hostMac index is =" , ind);
            print ("<h2><font color=\"#0000FF\"> # Edit Below Values and Press \'Submit Changes\' Button</font></h2>")
            print ('<p> --- Host Description:------- <input type="text" name="hostDesc" value= ' + str(hostDescList[ind]) + ' /></p>')
            print ('<p> --- IP address: -------------- <input type="text" name="ipAddr" value= ' + str(ipAddrList[ind]) + ' /></p>')
            print ('<p> --- Host Mac: --------------- <input type="text" name="hostMac" value= ' + str(hostsMacList[ind]) + ' /></p>')
            if regDhcpClietId.search(str(dhcpClientIdentifier[ind])):
                print ('<p> --- DHCP Client Identifier:<input type="text" name="dhcpClientId" value= '+str(dhcpClientIdentifier[ind])+' ''</p>')
            print ('<p> --- CUSTOM OPTIONS --:  </p>')
            print ('<textarea name = "textcontent" cols = "60" rows = 12">' + "".join(str(val) for val in HostOptions[ind]) +  '</textarea>')
            print ('<p><input type = "submit" name = "SubmitChanges" value = "Submit Changes"/></p>')
            print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
            print ('<input type = "submit" style="background-color:red; width:110px; height:35px" value = "Delete Host" name = "Delete?" />')
        else:
            # New host
            print ('<form method="post" action="relayHosts.py">')
            print ('<h2> # Creating new Host: ' + hostMac + "</h2>")
            print ("<h2><font color=\"#0000FF\"> # Enter Below Values and Press \'Submit New Host\' Button</font></h2>")
            print ('<p> --- Host Description:------- <input type="text" name="hostDesc" value="" /></p>')
            print ('<p> --- IP address: -------------- <input type="text" name="ipAddr" value="" /></p>')
            print ('<p> --- Host Mac: --------------- <input type="text" name="newHostMac" value=' + hostMac + ' /></p>')
            print (' --- DHCP Client Identifier:<input type="text" name="newDhcpClientId" value="" ')
            print ('<p> --- CUSTOM OPTIONS --:  </p>')
            print ('<textarea name = "textcontent" cols = "60" rows = 10"></textarea>')
            print ('<p></p>')
            print ('<input type = "submit" value = "Submit New Host"/>')
            print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG MAC FORMAT, PLEASE TRY AGAIN ## </font></h2>')
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Edit Host Chosen by User
if ((form.getvalue('hostMac')) or (form.getvalue('ipAddr')) or (form.getvalue('hostDesc')) or (form.getvalue('textcontent'))
    or (form.getvalue('dhcpClientId'))) and ((form.getvalue("SubmitChanges") == "Submit Changes") or (form.getvalue("newHostMac"))):
   print ('<form method="post" action="relayHosts.py">')
   ipAddrChos = form.getvalue('ipAddr')
   if form.getvalue('hostMac'):
       hostMac = form.getvalue('hostMac')
   else:
       hostMac = (form.getvalue("newHostMac"))
   hostDesc = form.getvalue('hostDesc')
   customOptions = form.getvalue('textcontent')
   if custumOptionsValidation(customOptions):
       if not form.getvalue("newHostMac") in hostsMacList and not any(form.getvalue("newHostMac") in subl for subl in ipsecHostsMacList):    
           if examSpecialCharInStr(hostDesc) and examSpecialCharInStr(customOptions):
               if hostMac in hostsMacList:
                   ind = hostsMacList.index(hostMac)
                   OrigHostDesc = hostDescList[ind]
               else: ind = ''
               if checkIpExistance(ipAddrChos,ind) and checkDescriptipnExist(hostDesc,ind):
                   if validate_ipaddress(form.getvalue('ipAddr')): 
                       hostDescChos = form.getvalue('hostDesc')
                       dhcpClientIden = form.getvalue('dhcpClientId')
                       if imsiFormatValid(dhcpClientIden) and duplicateImsi(dhcpClientIden,ind):
                           # print ("IMSI IS OK")
                           if regDhcpClietId.search(str(dhcpClientIden)):
                               dhcpClientIdFormat = "option dhcp-client-identifier \"\\000" + dhcpClientIden + "\";\n\t"
                           else: dhcpClientIdFormat = ''
                           #print ("@@@ eNBOfRelay chosen, converting mac @@@")
                           dhcpClientIdFormat = "option dhcp-client-identifier " + ascii2HexConverter(hostMac) + ";\n\t"
                           #print ("dhcpClientIdFormat = ", dhcpClientIdFormat)
                           if form.getvalue('textcontent'): HostOptions = form.getvalue('textcontent').replace('\r', '')
                           else: HostOptions = form.getvalue('textcontent')
                           # print line for testing
                           newHostFormat = ("\nhost ", hostDescChos, " {", '\n\t',
                                            dhcpClientIdFormat,
                                            "hardware ethernet ", hostMac,";\n\t",
                                            "fixed-address ", ipAddrChos, ";\n\t",
                                            "### BEGIN_CUSTOM_OPTIONS ###\n",
                                            HostOptions, "\n\t", "### END_CUSTOM_OPTIONS ###\n", "}\n")
                           # print ("newHostFormat = ", newHostFormat , "\n" )
                           editedF = outputFile
                           editf = open(editedF, 'w')
                           f3 = open(filename, 'r')
                           # Create New Host
                           if hostMac not in hostsMacList:
                               # print (" Adding new host to file ")
                               firstHostFound=0
                               for lin in f3:
                                   if lin.startswith("host") and firstHostFound==0:
                                      firstHostFound=1
                                      for t, value in enumerate(newHostFormat):
                                          editf.write(str(newHostFormat[t]))
                                      editf.write(lin) # writing host line to file
                                   else:
                                       # Writing line to file
                                       editf.write(lin);
                               #print ('<h2><font color=\"#9A7D0A\"> ## HOST CREATED: ## </font></h2>')
                               #print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS |</th><th>| IMSI |</th><th>| EDIT LINK |</th></tr><tr>")
                               #print ('<td>'+str(hostMac)+'</td> <td>'+str(hostDescChos)+'</td> <td>'+str(ipAddrChos)+
                               #       '</td><td><input type = "submit" name = "hostMacChosen" value =' +str(hostMac)+ ' </td></tr><tr>')
                               #print ("</tr></table>")
                           elif OrigHostDesc:
                               inLin='0'
                               for lin in f3:
                                   if OrigHostDesc not in lin and inLin != '1':
                                       # Writing line to file
                                       editf.write(lin);
                                   elif '}' in lin:
                                       inLin='0'
                                   elif OrigHostDesc in lin: # host-Desciption is in-line
                                      for t, value in enumerate(newHostFormat):
                                          # print ("value is =" , value)
                                          editf.write(str(newHostFormat[t]))
                                      inLin='1'
                           editf.close()
                           f3.close()
                           print ('<h2><font color=\"#9A7D0A\"> ## HOST EDITED/CREATED: ## </font></h2>')
                           print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS |</th><th>| IMSI |</th><th>| EDIT LINK |</th></tr><tr>")
                           print ('<td>'+str(hostMac)+'</td> <td>'+str(hostDescChos)+'</td> <td>'+str(ipAddrChos)+
                                  '</td><td>'+str(dhcpClientIden)+'</td><td><input type = "submit" name = "hostMacChosen" value =' +str(hostMac)+ ' </td></tr><tr>')
                           print ("</tr></table>")
                           #cpCommand = 'cp ' + outputFile + ' ' + inputFile ; print ("cpCommand = ", cpCommand)
                           #executeCmd('copy ' + outputFile + ' ' + inputFile)
                           # executeCmd('\cp ' + outputFile + ' ' + inputFile) # linux
                           #executeCmd('service dhcpd restart')
                           '''
                           print ('<h2> ## Host # ' + str(hostMac) + ' # New Values Are: </h2> ')
                           print ('<p>&#160 --- Host Description:-------- <input type="text" name="ipAddr" value= ' + str(hostDescChos) + ' /></p>')
                           print ('<p>&#160 --- IP address ---------------: <input type="text" name="ipAddr" value= ' + str(ipAddrChos) + ' /></p>')
                           print ('<p>&#160 --- host Mac ----------------: <input type="text" name="hostMac" value= ' + str(hostMac) + ' /></p>')
                           # if regDhcpClietId.search(str(dhcpClientIdentifier[ind])):
                           print ('&#160 --- DHCP Client Identifier:<input type="text" name="dhcpClientId" value= ' + str(dhcpClientIden) +' ''</p>')
                           print ('<p>&#160--- CUSTOM OPTIONS:  -----:  </p>')
                           print ("<textarea name = \"textcontent\" cols = \"80\" rows = \"8\" style=\"background-color:#40E0D0\">" + str(HostOptions) +  '</textarea>')
                           #cpCommand = 'cp ' + outputFile + ' ' + inputFile ; print ("cpCommand = ", cpCommand)
                           replaceDhcpdFile('copy ' + outputFile + ' ' + inputFile)
                           #restartDhcpd('service dhcpd restart')
                           print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
                           '''
                       else:
                           print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG IMSI FORMAT OR IMSI ALREADY EXIST, PLEASE TRY AGAIN ## </font></h2>')
                           print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
                   elif not validate_ipaddress(form.getvalue('ipAddr')):
                       print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG IP ADDRESS FORMAT, PLEASE TRY AGAIN ## </font></h2>')
                       print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
               else:
                   print ('<h2><font color=\"#9A7D0A\"> ## ALERT: IP (OR DESCRIPTION) IS ALREADY EXIST, PLEASE TRY AGAIN ## </font></h2>')
           else:
               print ('<h2><font color=\"#9A7D0A\"> ## ALERT: ILLIGAL CHARACTERS [@!#$%^&*()<>?\|}{~] IN DESCRIPTION OR CUSTOM-OPTIONS, PLEASE TRY AGAIN ## </font></h2>')
               print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
       else:
           print ('<h2><font color=\"#9A7D0A\"> ## ALERT: MAC IS ALREADY EXIST, PLEASE TRY AGAIN ## </font></h2>')
           print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
   else:
       print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG CUSTOM OPTIONS, PLEASE TRY AGAIN (MAKE SURE TO REMOVE NEW LINES) ## </font></h2>')
       print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


# New Host button pressed:
if (form.getvalue('newHost?')) == 'New Host':
    print ('<form method="post" action="relayHosts.py">')
    print ('<h2> ## Host Mac # '' # New Values Are: </h2> ')
    print ('<p>&#160 --- Host Description:-------- <input type="text" name="hostDesc" value="" /></p>')
    print ('<p>&#160 --- IP ADDRESS -----------: <input type="text" name="ipAddr" value="" /></p>')
    print ('<p>&#160 --- Host Mac ----------------: <input type="text" name="newHostMac" value="" /></p>')
    print ('<p>&#160 --- DHCP Client Identifier: <input type="text" name="dhcpClientId" value="" /></p>')
    print ('<p>&#160--- CUSTOM OPTIONS ------------:  </p>')
    print ("<textarea name = \"textcontent\" cols = \"60\" rows = \"8\" style=\"background-color:#40E0D0\">"'</textarea>')
    print ('<p><input type = "submit" name = "SubmitChanges" value = "Submit Changes"/></p>')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


# Deleting Host
if (form.getvalue("Delete?") == "Delete Host"):
    print ('<form method="post" action="relayHosts.py">')
    # print ("DELETING HOST")
    MacToDel = form.getvalue("hostMac")
    if MacToDel in hostsMacList:
        ind = hostsMacList.index(MacToDel)
        MacDescToDel = hostDescList[ind]
        editedF = outputFile
        editf2 = open(editedF, 'w')
        f5 = open(filename, 'r')
        inLin='0'
        for lin in f5:
            if MacDescToDel not in lin and inLin != '1':
                # Writing line to file
                editf2.write(lin);
            elif MacDescToDel in lin or inLin == '1':
               # print ("SKIP LINE / DO NULL") ;
               inLin='1';
               if '}' in lin: inLin='0';
            else:
                print ("WHAT TO DO? NO SUCH MAC?")
        editf2.close()
        f5.close()
        # print ('<h2><font color=\"#9A7D0A\"> ## HOST DELETED: '+ MacToDel + ' <<--->> ' + MacDescToDel +  ' ## </font></h2>')
        print ('<h2><font color=\"#9A7D0A\"> ## HOST DELETED:</font></h2>')
        print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS |</th></tr><tr>")
        print ('<td>'+str(hostsMacList[ind])+'</td> <td>'+str(hostDescList[ind])+'</td> <td>'+str(ipAddrList[ind])+ '</td></tr><tr>')
        print ("</tr></table>")
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
        # CMD("service dhcpd restart")
        #executeCmd('copy ' + outputFile + ' ' + inputFile)
        # executeCmd('\cp ' + outputFile + ' ' + inputFile) # linux
        #executeCmd('service dhcpd restart')
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## NO SUCH MAC TO DELETE: ' + MacToDel + ' -  PLEASE TRY AGAIN ## </font></h2>')


# Sorintg:
#print("ipAddrList =", int(str(ipAddrList).encode()).sort())
#stringIpList = ''.join(str(ipAddrList)) # converting list into string
#sortedIpAddrList = "".join.sorted(stringIpList)
#print ("ipAddrList = %s" %ipAddrList )
#print ("sortedIpAddrList = %s" %sortedIpAddrList )

# Table print
if not form.getvalue("hostMacChosen") and not form.getvalue("valToSearch") and not form.getvalue("SubmitChanges") and not form.getvalue("Delete?") and not form.getvalue('newHost?'):
    print ('<form method="post" action="relayHosts.py">')
    #print ('<p> ## =========================================================================== ## </p>')
    '''
    print('<button onclick='"w3.sortHTML('#id01', 'li')"'>Sort</button>'
          '<ul id="id01"><li>Oslo</li><li>Stockholm</li><li>Helsinki</li><li>Berlin</li><li>Rome</li><li>Madrid</li></ul>')
    '''
    print ('<font color=\"#0000FF\">&#160# Search Host By ( IMSI / MAC / IP / DESCRIPTION ): <input type="text" name="valToSearch"/></font>')
    print ('<input type="submit" value="Search Host"/><br>')
    print ('<p></p>') ; print ('<p></p>') ; y=0
    print ('<p><font color=\"#0000FF\">&#160# To create New Host Enter: </font>')
    print ('<input type="submit" value="New Host" name = "newHost?" /><br></p>')
    print ("<font color=\"#FF4500\"><h2> Relay Hosts List: </h2></font>")
    print ("<table><tr><th>| # |</th><th>| MAC |</th><th>| DESCIRPTION |</th><th>| IP-ADDRESS |</th><th>| IMSI |</th><th>| EDIT LINK |</th></tr><tr>")
    z=0
    for y, Mac in enumerate(hostsMacList):
        if hostTypeList[y] == "1":
            print ('<td>'+str(z)+'</td><td>'+str(hostsMacList[y])+'</td> <td>'+str(hostDescList[y])+'</td> <td>'+str(ipAddrList[y])+ '</td><td>'+str(dhcpClientIdentifier[y])+
                   '</td><td><input type = "submit" name = "hostMacChosen" value =' +str(hostsMacList[y])+ ' </td></tr><tr>')
            z+=1
    print ("</tr></table>")
print ("</form>")
print ("</body>")
print ("</html>")

