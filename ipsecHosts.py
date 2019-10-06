#!C:\Python\Python37-32\python

# #!/usr/bin/python3.6

import cgi
import cgitb; cgitb.enable()  # for troubleshooting 
from array import *
import re
import ipaddress
import os
import socket,struct
import binascii
import math # to round up divide results
import subprocess

#################################
# Writen By: Itay Shay
# ACS / ishay@airspan.com
#
#### Configuration Variable #####
dhcpConfTmp = 'C:/Stuff/scripts/python/airspan-guiForDhcp/dhcp.conf.tmp'
inputFile = 'C:/Stuff/scripts/python/airspan-guiForDhcp/dhcpd.conf'
outputFile = 'C:/Stuff/scripts/python/airspan-guiForDhcp/editedF.conf'
# for linux:
#dhcpConfTmp = os.path.join('/tmp/', 'dhcpd.conf.tmp')
#inputFile = os.path.join('/etc/dhcp/', 'dhcpd.conf')
#outputFile = os.path.join('/etc/dhcp/', 'editedF.conf')
#################################

print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title> IPsec Hosts </title></head>")
print ('<body style=\"background-color:#E5E8E8;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"   IPsec Hosts  "'</font></h1>')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #8ebf42; background-color: #EDBB99;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')

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

# Verify Mac format
def checkMAC(x):
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower()): return 1;
    else: return 0;

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

# open dhcpd.conf:
filename = inputFile
#f = open(filename, 'r') 
#text = f.read().strip()

# find the number of hosts, subnets and the max custom options in subnet
# remove "CUSTOM_OPTIONS" string lines from file
editf = open(dhcpConfTmp, 'w')
fi = open(filename, 'r'); numHosts = 0 ; numoptions=0 ; numSubnets = 0 ; numoptions=0 ; numOfIpSecHosts=0; numOptions=0
for l in fi:
    if l.startswith("host"): numHosts += 1
    if not re.search(r'.*.CUSTOM_OPTIONS.*\n',l):
        editf.write(l)
    if l.startswith("subnet"): numSubnets += 1
    if "if (substring" in l: numOfIpSecHosts += 1
    if l.startswith("option "): numOptions += 1
editf.close()
fi.close()

# find x/y position of an inde from 2D list
def findPosition(val):
    for i in range(len(subnetList)):
        for j in range(len(ipsecHostsMacList)):
            if val == ipsecHostsMacList[i][j] or val == ipsecHostsDescList[i][j]:
                # print ("VAL , psecHostsMacList[i][j], ipsecHostsDescList[i][j] = ", val, ipsecHostsMacList[i][j], ipsecHostsDescList[i][j])
                postn=[i,j] ;
                # print ("postn = ", postn)
                return postn ; break

hostsMacList = list(range(0,numHosts))
hostDescList = list(range(0,numHosts))
ipAddrList = list(range(0,numHosts))
dhcpClientIdentifier = list(range(0,numHosts))
hostMac = ''
netmaskList = list(range(0,numSubnets))
subnetList = list(range(0,numSubnets))
ipsecHostsMacList = list(range(0,numOfIpSecHosts))
ipsecHostsDescList = list(range(0,numOfIpSecHosts))
ipsecHostsOptionsList = list(range(0,numOfIpSecHosts))
optionsList = list(range(0,numOptions))

# 2D array for hosts/custom-options
items2, lists2 = 24, numHosts;
HostOptions = [["" for w in range(items2)] for r in range(lists2)]
items, lists = 54, numSubnets;
ipsecHostsMacList = [["" for w in range(items)] for r in range(lists)]
ipsecHostsDescList = [["" for w in range(items)] for r in range(lists)]
ipsecHostsOptionsList = [["" for w in range(items)] for r in range(lists)]
x=0 ; j=0

# db for hosts (exept ipsec hosts):
fTmp = open(dhcpConfTmp, 'r')
for i, line in enumerate(fTmp):
    if line.startswith("host"):
        # print ("Host Is =", line)
        f2 = open(dhcpConfTmp, 'r'); lines=f2.readlines()
        # hostDescList[x] = line.split(' ')[1] ; # print ("HostDescList =", hostDescList[x])
        for k in range(i+1,i+3):
            # print ("K is =", k)
            if "hardware ethernet" in lines[k]:
                hostsMacList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("hostsMacList =", hostsMacList[x])
            if "fixed-address" in lines[k]:
                ipAddrList[x] = lines[k].split(' ')[-1].strip().strip(";"); # print ("ipAddrList =", ipAddrList[x])
            if "}" in lines[k]:
                break
        x+=1; # incremented for each line with "host"
        f2.close()
fTmp.close()

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

def checkDescriptionExist(hostDescChos,indicator):
    # print ("Checking if Desc exist or not, indicator =", indicator)
    if indicator == 0 or indicator:
        hostDescrip = ipsecHostsDescList[indicator]
        # print ("hostDescrip / hostDescChos" ,hostDescrip , hostDescChos)
        if hostDescChos not in ipsecHostsDescList or hostDescrip == hostDescChos:
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


def verifySubnetNetmaskPair(subn,netm,indicator):
    if indicator == 0 or indicator:
        sub = subnetList[indicator]
        net = netmaskList[indicator]
        if sub == subn and net == netm:
            #print ("return true while sub == subn and net == netm")
            return True
        else:
            #print ("return FALSE while sub != subn or net != netm")
            return False
    else:
        f = open(filename, 'r')
        for line in f:
            if subn in line and netm in line:
                #print ("return True - both subnet and netmask are at the same line")
                return True
        f.close()
        #print ("return false while indicator is null")
        return False


op = list(range(0,12)) # tmp
def custumOptionsValidation(val):
    ok=0
    # print ("custumOptionsValidation, vali is = ", val)
    options =''
    if val:
        options = val.split('\n')
    else:
        return True
    opLen = len(options) ; # print ("opLen = ", opLen)
    for opL in options:
        if not opL:
            # print ("EMPTY line")
            opLen-=1    # print ("options = ", options)
    for option in options:
        # print ("optionOrig = " , option)
        opTmp = option.replace('\n','').replace('\r','').replace('\t','')
        if opTmp and opTmp.count("option") == 1:
            #print ("op SPLIT =" , opTmp.split(' '))
            op = opTmp.split(' ')[1]
            #print ("op = ", op)
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


form = cgi.FieldStorage()
print ('<p>' "debugging: form is: " + str(form) + '</p>'); # remove if Linux

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


# Host Search Pressed
if form.getvalue("valToSearch"):
    print ('<form method="post" action="ipsecHosts.py">')
    val2Search = form.getvalue("valToSearch")
    print ('<style>table {border-style: ridge;  border-width: 2px; '
           'border-color: #FDF2E9; background-color: #B48DF0;} th  '
           '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')
    valFound=0
    print ('<h2><font color=\"#9A7D0A\"> # Search Results For "' +val2Search+ '" : </font></h2>')
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
                            print ('</td> <td><input type = "submit" name = "hostMacChosen" value =' +str(ipsecHostsMacList[index][x])+ ' </td></tr>')
        if (val2Search in sul for sul in ipsecHostsMacList):
            #print ("ipsecHostsMacList")
            for index, item in enumerate(ipsecHostsMacList):
                for indY, dd in enumerate(item):
                    if val2Search in dd:
                        print ('<td>'+str(ipsecHostsMacList[index][indY])+'</td> <td>'+str(ipsecHostsDescList[index][indY])+'</td> <td>'+str(subnetList[index])+ ' / ' +str(netmaskList[index])+'</td>')
                        print ('</td> <td><input type = "submit" name = "hostMacChosen" value =' +str(ipsecHostsMacList[index][indY])+ ' </td></tr>')
        if (val2Search in subl for subl in ipsecHostsDescList):
            #print ("ipsecHostsDescList")
            for index, item in enumerate(ipsecHostsDescList):
                for indY, dd in enumerate(item):
                    if val2Search in str(dd):
                        print ('<td>'+str(ipsecHostsMacList[index][indY])+'</td> <td>'+str(ipsecHostsDescList[index][indY])+'</td> <td>'+str(subnetList[index])+ ' / ' +str(netmaskList[index])+'</td>')
                        print ('</td> <td><input type = "submit" name = "hostMacChosen" value =' +str(ipsecHostsMacList[index][indY])+ ' </td></tr>')
    print ("</tr></table>")
    if not valFound:
        print ('<h2><font color=\"#9A7D0A\"> ## ALERT: ## COULDN\'T FIND REQUESTED VALUE, PLEASE TRY AGAIN ## </font></h2>')
    #print ("</tr></table>")
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


'''
    print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| SUBNET |</th><th>| NETMASK |</th><th>| EDIT LINK |</th></tr><tr>")
    if any(val2Search in subl for subl in ipsecHostsDescList) or any(val2Search in subl for subl in ipsecHostsMacList) or (val2Search in subnetList): #  
        if any(val2Search in subl for subl in ipsecHostsDescList):
            ind, indY = findPosition(val2Search)
            #print ("VAL FOUND IN DESC' LIST, ind, indY = %s,%s" %(ind,indY))
        elif any(val2Search in subl for subl in ipsecHostsMacList):
            ind, indY = findPosition(val2Search)
            #print ("VAL FOUND IN MAC LIST, ind, indY = %s,%s" %(ind, indY))
        elif val2Search in subnetList:
            ind = subnetList.index(val2Search)
            indY=''
            #print ("VAL FOUND IN SUBNET LIST. ind= %s,%s" %(ind,indY))
        # print ("ind, indY = %s,%s" %(ind, indY))
        if ind and (indY == 0 or indY):
            # print ("IND AND IND-Y:")
            print ('<td>'+str(ipsecHostsMacList[ind][indY])+'</td><td>'+str(ipsecHostsDescList[ind][indY])+'</td><td>'+str(subnetList[ind])+ '</td><td>'+str(netmaskList[ind])+ '</td>')
            print ('<td><input type = "submit" name = "hostMacChosen" value =' +str(ipsecHostsMacList[ind][indY])+ ' </td></tr></tr>')
        if ind and not indY == 0 and not indY:
            print ("SEARCH BY SUBNET:")
    else:
        print ("<h2><font color=\"#9A7D0A\">## ALERT: COULDN'T FIND REQUESTED VALUE, PLEASE TRY AGAIN ##</font><h2>")
        # print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
    print ("</tr></table>")
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
'''

# Host Chosen (Edit button)
if form.getvalue("hostMacChosen"):
    print ('<form method="post" action="ipsecHosts.py">')
    hostMac = form.getvalue("hostMacChosen")
    # Validate mac format
    if checkMAC(hostMac):
        # print ("MAC is OK")
        # Check if host chosen (1) exists, for editing or.. (2) new to create new:
        #print ("ipsecHostsMacList = ", ipsecHostsMacList)
        if any(hostMac in subl for subl in ipsecHostsMacList):
            print ('<h2> # Host Mac Chosen is: ' + hostMac +  "  </h2>")
            # ind = ipsecHostsMacList.index(hostMac)
            ind, indY = findPosition(hostMac) ; #print ("ind, indY =" '%s,%s'%(ind,indY) )
            print ("<h2><font color=\"#0000FF\"> # Edit Below Values and Press \'Submit Changes\' Button</font></h2>")
            print ('<p> --- ipsec Host Description:------- <input type="text" name="ipsechostDesc" value= ' + str(ipsecHostsDescList[ind][indY]) + ' /></p>')
            print ('<p> --- SUBNET: ----------------------- <input type="text" name="subnetChos" value= ' + str(subnetList[ind]) + ' /></p>')
            print ('<p> --- NETMASK: -------------------- <input type="text" name="netmaskChos" value= ' + str(netmaskList[ind]) + ' /></p>')
            print ('<p> --- IPsec Host Mac: --------------- <input type="text" name="hostMac" value= ' + str(ipsecHostsMacList[ind][indY]) + ' /></p>')
            print ('<p> --- CUSTOM OPTIONS ---------:  </p>')
            print ('<textarea name = "textcontent" cols = "52" rows = 3">' + "".join(str(val) for val in ipsecHostsOptionsList[ind][indY]) +  '</textarea>')
            print ('<p></p>')
            print ('<input type = "submit" name = "SubmitChanges" value = "Submit Changes"/>')
            print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
            print ('<input type = "submit" style="background-color:red; width:110px; height:35px" value = "Delete Host" name = "Delete?" />')
        else:
            # New IPsec host
            print ('<form method="post" action="ipsecHosts.py">')
            print ('<h2> # Creating new ipsec Host: ' + hostMac + "</h2>")
            print ("<h2><font color=\"#0000FF\"> # Enter Below Values and Press \'Submit New Host\' Button</font></h2>")
            print ('<p> --- Host Description:------- <input type="text" name="hostDesc" value="" /></p>')
            print ('<p> --- SUBNET: ---------------- <input type="text" name="newSubnet" value="" /></p>')
            print ('<p> --- NETMASK: ---------------- <input type="text" name="newNetmask" value="" /></p>')
            print ('<p> --- Host Mac: --------------- <input type="text" name="newHostMac" value=' + hostMac + ' /></p>')
            print ('<p> --- CUSTOM OPTIONS ---------:  </p>')
            print ('<textarea name = "textcontent" cols = "52" rows = 3"></textarea>')
            print ('<p></p>')
            print ('<input type = "submit" value = "Submit New Host"/>')
            print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG MAC FORMAT, PLEASE TRY AGAIN ## </font></h2>')


# Edit Host Chosen by User
if ((form.getvalue('hostMac')) or (form.getvalue('subnetChos')) or (form.getvalue('ipsechostDesc')) or (form.getvalue('netmaskChos')) or (form.getvalue('textcontent'))
    or (form.getvalue('dhcpClientId'))) and ((form.getvalue("SubmitChanges") == "Submit Changes") or (form.getvalue("newHostMac"))):
   print ('<form method="post" action="ipsecHosts.py">')
   subnetChos = form.getvalue('subnetChos')
   netmaskChos = form.getvalue('netmaskChos')
   # ipsechostDesc = form.getvalue('ipsechostDesc')
   HostOptions = form.getvalue('textcontent').strip('\n').replace('\n', '\t\t\t')
   if form.getvalue('ipsechostDesc'):
       ipsechostDesc = form.getvalue('ipsechostDesc')
   else:
       ipsechostDesc = form.getvalue('hostDescChos')
   if form.getvalue('hostMac'):
       hostMac = form.getvalue('hostMac')
   else:
       hostMac = (form.getvalue("newHostMac"))
   hostDesc = form.getvalue('hostDesc')
   customOptions = form.getvalue('textcontent')
   if custumOptionsValidation(customOptions):
       if not form.getvalue("newHostMac") in hostsMacList and not any(form.getvalue("newHostMac") in subl for subl in ipsecHostsMacList):
           if examSpecialCharInStr(hostDesc) and examSpecialCharInStr(customOptions):
               if any(hostMac in subl for subl in ipsecHostsMacList):
                    ind, indY = findPosition(hostMac)
                    OrigHostDesc = ipsecHostsDescList[ind][indY]
               else: ind, indY ='',''
               if verifySubnetNetmaskPair(subnetChos,netmaskChos,ind):
                   if validate_ipaddress(form.getvalue('subnetChos')): 
                       # hostDescChos = form.getvalue('hostDesc')
                       newHostFormat = ("    if (substring(hardware,1,6)=", hostMac,")    ## ", ipsechostDesc, "\n    {\n    \t    ",
                                        HostOptions, "\n", "        }\n")
                       # print ("newHostFormat = ", newHostFormat , "\n" )
                       editedF = outputFile
                       editf = open(editedF, 'w')
                       f3 = open(filename, 'r')
                       # Create New Host Mac
                       # if verifySubnetNetmaskPair(subnetChos,netmaskChos,ind):
                       if not any(hostMac in subl for subl in ipsecHostsMacList):
                           # print (" Adding new host to file ")
                           firstHostFound=0
                           # strTest = "subnet " +str(subnetChos)+ " netmask " +str(netmaskChos) ; # print ("strTest = ", strTest)
                           mark = '0'
                           for i, lin in enumerate(f3):
                               if ("subnet " +str(subnetChos)+ " netmask " +str(netmaskChos)) in lin and mark == '0':
                                  mark = '1'
                                  editf.write(lin)
                               elif mark == '1':
                                   if "pool {" in lin or lin.startswith("{") or "END_CUSTOM_OPTIONS" in lin:
                                       for t, value in enumerate(newHostFormat):
                                           editf.write(str(newHostFormat[t]))
                                       mark = '0'
                                       editf.write(lin)
                                       # break
                                   else:
                                       editf.write(lin)
                               else:
                                   editf.write(lin);
                           print ('<h2><font color=\"#9A7D0A\"> ## HOST EDITED/CREATED: ## </font></h2>')
                           print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| SUBNET |</th><th>| NETMASK |</th><th>| EDIT LINK |</th></tr><tr>")
                           print ('<td>'+str(hostMac)+'</td> <td>'+str(ipsechostDesc)+'</td> <td>'+str(subnetChos)+ '<td>'+str(netmaskChos)+
                                  '</td><td><input type = "submit" name = "hostMacChosen" value =' +str(hostMac)+ ' </td></tr><tr>')
                           print ("</tr></table>")
                       elif any(hostMac in subl for subl in ipsecHostsMacList):
                           inLin='0'
                           for lin in f3:
                               if "(substring(hardware,1,6)=" + hostMac +")" not in lin and inLin != '1':
                                   editf.write(lin);
                               elif '}' in lin:
                                   inLin='0'
                               elif "(substring(hardware,1,6)=" + hostMac +")" in lin: # host-Desciption is in-line
                                  for t, value in enumerate(newHostFormat):
                                      # print ("value is =" , value)
                                      editf.write(str(newHostFormat[t]))
                                  inLin='1'
                       editf.close()
                       f3.close()
                       print ('<h2> ## Host New Values Are: </h2> ')
                       print ('<p>&#160 --- Host Description:-------- <input type="text" name="hostDescChos" value= ' + str(ipsechostDesc) + ' /></p>')
                       print ('<p>&#160 --- IP address ---------------: <input type="text" name="subnetChos" value= ' + str(subnetChos) + ' /></p>')
                       print ('<p>&#160 --- Host MAC --------------: <input type="text" name="hostMac" value= ' + str(hostMac) + ' /></p>')
                       print ('<p>&#160--- CUSTOM OPTIONS ---:  </p>')
                       print ("<textarea name = \"textcontent\" cols = \"49\" rows = \"3\" style=\"background-color:#40E0D0\">" + str(HostOptions.replace('\t', '')) +  '</textarea>')
                       print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
                       #executeCmd('copy ' + outputFile + ' ' + inputFile) # win
                       executeCmd('\cp ' + outputFile + ' ' + inputFile) # linux
                       executeCmd('service dhcpd restart')
                   elif not validate_ipaddress(form.getvalue('subnetChos')):
                       print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG IP ADDRESS FORMAT, PLEASE TRY AGAIN ## </font></h2>')
                       print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
               else:
                   print ('<h2><font color=\"#9A7D0A\"> ## ALERT: NO SUCH SUBNET AND NETMASK PAIR, PLEASE CHECK SUBNET LIST ## </font></h2>')
                   print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
           else:
               print ('<h2><font color=\"#9A7D0A\"> ## ALERT: ILLIGAL CHARACTERS [@!#$%^&*()<>?\|}{~] IN DESCRIPTION OR CUSTOM-OPTIONS, PLEASE TRY AGAIN ## </font></h2>')
               print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
       else:
           print ('<h2><font color=\"#9A7D0A\"> ## ALERT: MAC IS ALREADY EXIST, PLEASE TRY AGAIN ## </font></h2>')
           print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
   else:
       print ('<h2><font color=\"#9A7D0A\"> ## ALERT: WRONG CUSTOM OPTIONS, PLEASE TRY AGAIN (MAKE SURE TO REMOVE NEW LINES) ## </font></h2>')
       print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# New IPsec Host button pressed:
if (form.getvalue('ipsecHost?')) == 'New IPsec Host':
    print ('<form method="post" action="ipsecHosts.py">')
    print ('<h2> ## Host Mac # '' # New Values Are: </h2> ')
    print ('<p>&#160 --- Host Description:-------- <input type="text" name="hostDescChos" value="" /></p>')
    print ('<p>&#160 --- SUBNET ----------------: <input type="text" name="subnetChos" value="" /></p>')
    print ('<p>&#160 --- NETMASK -------------: <input type="text" name="netmaskChos" value="" /></p>')
    print ('<p>&#160 --- host Mac ----------------: <input type="text" name="newHostMac" value="" /></p>')
    print ('<p>&#160--- CUSTOM OPTIONS ------------:  </p>')
    print ("<textarea name = \"textcontent\" cols = \"52\" rows = \"3\" style=\"background-color:#40E0D0\">"'</textarea>')
    print ('<p><input type = "submit" name = "SubmitChanges" value = "Submit Changes"/></p>')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


# Deleting Host
if form.getvalue('Delete?') == "Delete Host":
    # print ("DELETING HOST")
    MacToDel = form.getvalue("hostMac")
    print ('<form method="post" action="ipsecHosts.py">')
    if any(MacToDel in subl for subl in ipsecHostsMacList):
        ind, indY = findPosition(MacToDel)
        MacDescToDel = ipsecHostsDescList[ind][indY]
        editedF = outputFile
        editf2 = open(editedF, 'w')
        f5 = open(filename, 'r')
        inLin='0'
        for lin in f5:
            if "substring(hardware,1,6)="+MacToDel not in lin and inLin != '1':
                # Writing line to file
                editf2.write(lin);
            elif "substring(hardware,1,6)="+MacToDel in lin or inLin == '1':
               # print ("SKIP LINE / DO NULL") ;
               inLin='1';
               if '}' in lin: inLin='0';
            else:
                print ("WHAT TO DO? NO SUCH MAC?")
        editf2.close()
        f5.close()
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
        print ('<h2><font color=\"#9A7D0A\"> ## HOST DELETED:</font></h2>')
        print ("<table><tr><th>| MAC |</th><th>| DESCIRPTION |</th><th>| SUBNET |</th><th>| NETMASK |</th><th>| OPTIONS |</th></tr><tr>")
        print ('<td>'+str(ipsecHostsMacList[ind][indY])+'</td> <td>'+str(ipsecHostsDescList[ind][indY])+'</td> <td>'+str(subnetList[ind])+'</td> <td>'+str(netmaskList[ind])+'</td>'
               '<td>' +str(ipsecHostsOptionsList[ind][indY])+ '</td> </tr><tr>')
        print ("</tr></table>")
        print ('<p></p>')
        # cmd
        #executeCmd('copy ' + outputFile + ' ' + inputFile)
        # executeCmd('\cp ' + outputFile + ' ' + inputFile) # linux
        #executeCmd('service dhcpd restart')
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## NO SUCH HOST MAC TO DELETE: ' + MacToDel + ' -  PLEASE TRY AGAIN ## </font></h2>')
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Table print
if not form.getvalue("hostMacChosen") and not form.getvalue("valToSearch") and not form.getvalue("SubmitChanges") and not form.getvalue('ipsecHost?') and not form.getvalue("Delete?"):
    print ('<form method="post" action="ipsecHosts.py">')
    print ('<p><font color=\"#0000FF\">&#160# Search IPsec Host By (MAC / DESCRIPTION): <input type="text" name="valToSearch"/></font>')
    print ('<input type="submit" value="Search Host"/><br></p>')
    print ('<p><font color=\"#0000FF\">&#160# Create New IPsec Host: </font>')
    print ('<input type="submit" value="New IPsec Host" name = "ipsecHost?" /><br></p>')
    print ("<font color=\"#FF4500\"><h2> IPsec Hosts List: </h2></font>")
    print ("<table><tr><th>| # |</th><th>| MAC |</th><th>| DESCIRPTION |</th><th>| SUBNET |</th><th>| NETMASK |</th><th>| OPTIONS |</th><th>| EDIT LINK |</th></tr><tr>")
    y=0
    for i in range(len(subnetList)):
        for j in range(len(ipsecHostsMacList)):
            if ipsecHostsMacList[i][j]:
                #print ("subnetList = " ,  subnetList[i])
                #print ("netmaskList = " , netmaskList[i])
                #print ("ipsecHostsMacList = " , ipsecHostsMacList[i][j])
                #print ("ipsecHostsDescList = " , ipsecHostsDescList[i][j])
                #print ("ipsecHostsOptionsList = " , ipsecHostsOptionsList[i][j])
                print ('<td>'+str(y)+'</td><td>'+str(ipsecHostsMacList[i][j])+'</td> <td>'+str(ipsecHostsDescList[i][j])+'</td> <td>'+str(subnetList[i])+'</td> <td>'+str(netmaskList[i])+'</td>'
               '<td>' +str(ipsecHostsOptionsList[i][j])+ '</td> <td><input type = "submit" name = "hostMacChosen" value =' +str(ipsecHostsMacList[i][j])+ ' </td></tr><tr>')
                y+=1
            #print ('%s,%s'%(i,j))
    print ("</tr></table>")

print ("</form>")
print ("</body>")
print ("</html>")



