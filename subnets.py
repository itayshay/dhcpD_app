#!C:\Python\Python37-32\python

# # #!/usr/bin/python3.6

import cgi
import cgitb; cgitb.enable()  # for troubleshooting, comment-out if linux server
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

print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title>DHCP v4 Subnets </title></head>")
print ('<body style=\"background-color:#E5E8E8;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"  Subnets v.4 Settings  "'</font></h1>')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #8ebf42; background-color: #99C0ED;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')


# Restart dhcpd every dhcpd.conf file cahnge ("service dhcpd restart") 
def CMD(cmd) :
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=False)
    return (p.stdin, p.stdout, p.stderr)

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

# open dhcpd.conf:
filename = inputFile
f = open(filename, 'r') 
text = f.read().strip()

# find the number of subnets and the max custom options in subnet
# remove "CUSTOM_OPTIONS" string lines from file
editf = open(dhcpConfTmp, 'w')
fi = open(filename, 'r'); numSubnets = 0 ; numoptions=0
for l in fi:
    if l.startswith("subnet"): numSubnets += 1
    if not re.search(r'.*.CUSTOM_OPTIONS.*\n',l):
        editf.write(l)
fi.close()
editf.close()

#subnetsMacList = list(range(0,numSubnets))
#subnetDescList = list(range(0,numSubnets))
netmaskList = list(range(0,numSubnets))
subnetList = list(range(0,numSubnets))
ipNetList = list(range(0,numSubnets))
entireSubnetList = list(range(0,numSubnets))

# 2D array for hosts/custom-options
items, lists = 99, numSubnets;
# SubnetOptions = [["" for w in range(items)] for r in range(lists)]
subnetContent = [["" for w in range(items)] for r in range(lists)]
x=0 ; j=0


'''
regSubnetContent2 = re.compile(r'\bsubnet(.*?){(\n.*)*?\n}')
print ("regSubnetContent2 = ", regSubnetContent2)
regSubnetContent = re.compile(r'\bsubnet(.*?){(\n.*)*?\n}')
match = (regSubnetContent.search(text).group())+'\n'
print ("match = ", match)

for q in re.findall(regSubnetContent2, text):
    print ("q =", q[0],q[1])

for regSubnetContent in text:
    print ("building entireSubnetList")
    entireSubnetList = regSubnetContent
'''

x=0 ; j=0
fTmp = open(inputFile, 'r')
for i, line in enumerate(fTmp):
    if line.startswith("subnet"):
        # print ("subnet in line = ", line)
        splitlen = len(line.split(' '))
        subnetList[x] = line.split(' ')[-(splitlen-1)]
        netmaskList[x] = line.split(' ')[-2]
        '''
        # print ("subnet Is =", line)
        f2 = open(dhcpConfTmp, 'r'); lines=f2.readlines()
        ipNetList[x] = line.strip(" {")
        regOptions = r'' + ipNetList[x] + '{.*\{\n(.*?\n)*?\}'
        print ("options = ", regOptions)
        regex_compile=re.compile(regOptions)
        # SubnetOptions[x] = (regex_compile.search(text).group(0))+'\n'        
        x+=1;
        f2.close()
        '''
        f = open(filename, 'r'); lines=f.readlines()
        for k in range(i+1,i+99):
            if lines[k].startswith("}"):
                #print ("### ending subnet }, BREAK, K IS = %s" %(k) )
                #print ("line is = ", line) ;  print ("lines is = %s / k is %s" %(lines[k], k))
                j=0; break
            else:
                #print ("X = %s  / j = %s" %(x, j) )
                subnetContent[x][j] = lines[k] ; j+=1; # print ("subnetContent = ", subnetContent[x][j])
        f.close()
        x+=1; 
fTmp.close()

#print ("subnetContent[0] = ", subnetContent[0])
#print ("subnetContent[1] = ", subnetContent[1])

form = cgi.FieldStorage()
print ('<p>' "debugging: form is: " + str(form) + '</p>'); # linux
if form.getvalue("subnetToFind"):
    print ("")

# LINK IS PRESSED:
if form.getvalue("subnetChosen"):
    print ('<form method="post" action="subnets.py">')
    subChos = form.getvalue("subnetChosen")
    ind = subnetList.index(subChos) 
    print ('<h2> # Subnet & Netmask Chosen Are: ' + subChos + " / " + netmaskList[ind] + "  </h2>")
    print ('<p> --- SUBNET:  <input type="text" name="subnet" value= ' + str(subChos) + ' />')
    print (' --- NETMASK:  <input type="text" name="netmask" value= ' + str(netmaskList[ind]) + ' /></p>')
    print ('<textarea name = "textcontent" cols = "65" rows = 26">' + "".join(str(val) for val in subnetContent[ind]) +  '</textarea>')
    print ('<p><input type = "submit" name = "SubmitChanges" value = "Submit Changes"/></p>')
    print ('<input type = "submit" style="background-color:red; width:110px; height:35px" value = "Delete Subnet" name = "Delete?" />')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Submit changes Pressed
if (form.getvalue("SubmitChanges") == "Submit Changes"):
    print ('<form method="post" action="subnets.py">')
    newVals = form.getvalue('textcontent')
    subnet = form.getvalue("subnet")
    netmask = form.getvalue("netmask")
    # ind = subnetList.index(subChos)
    if newVals:
        editedF = outputFile
        editf = open(editedF, 'w')
        f = open(filename, 'r')
        subFound=0
        countinue=1
        for lin in f:
           if lin.startswith("subnet " +subnet+ " netmask " +netmask ) and subFound==0:
              subFound=1
              editf.write(lin)
              #editf.write("subnet " +subnet+ " netmask " +netmask +" {\n" ) ;
              for val in newVals:
                  editf.write(str(val.strip('\r')))
              #editf.write(lin) # writing subnet line to file
              editf.write("}\n")
              countinue=0
           elif lin.startswith("}"):
               countinue=1
           elif countinue == 1:
               # Writing other lines to file
               editf.write(lin);
        f.close()

# Submit New Subnet Pressed
if (form.getvalue("SubmitNewSubnet") == "Submit New Subnet"):
    print ('<form method="post" action="subnets.py">')
    newVals = form.getvalue('textcontent')
    subnet = form.getvalue("subnet")
    netmask = form.getvalue("netmask")
    # ind = subnetList.index(subChos)
    if newVals:
        editedF = outputFile
        editf = open(editedF, 'w')
        f = open(filename, 'r')
        firstSubFound=0
        for lin in f:
           if lin.startswith("subnet ") and firstSubFound==0:
              firstSubFound=1
              editf.write("subnet " +subnet+ " netmask " +netmask+ " {\n" )
              for val in newVals:
                  editf.write(str(val.strip('\r')))
              #editf.write(lin) # writing subnet line to file
              editf.write("\n}\n")
           else:
               # Writing other lines to file
               editf.write(lin);
        f.close()
        print ('<h2> # New Subnet & Netmask Are: ' + subnet + " / " + netmask + "  </h2>")
        print ('<p> --- SUBNET:  <input type="text" name="subnet" value= ' + str(subnet) + ' />')
        print (' --- NETMASK:  <input type="text" name="netmask" value= ' + str(netmask) + ' /></p>')
        print ('<textarea name = "textcontent" cols = "65" rows = 26">' + "".join(str(val.strip('\n')) for val in newVals) +  '</textarea>')
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Add New Subnet Pressed:
if (form.getvalue("newHost?") == "Add New Subnet"):
    print ('<form method="post" action="subnets.py">')
    print ('<h2> # Complete Below Values To Add new Subnet:  </h2>')
    print ('<p> --- SUBNET:  <input type="text" name="subnet" value= '' >')
    print (' --- NETMASK:  <input type="text" name="netmask" value= '' ></p>')
    print ('<textarea name = "textcontent" cols = "65" rows = 26">''</textarea>')
    print ('<p><input type = "submit" name = "SubmitNewSubnet" value = "Submit New Subnet"/></p>')
    print ('<input type = "submit" style="background-color:red; width:110px; height:35px" value = "Delete Subnet" name = "Delete?" />')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Delete Button Pressed:
if (form.getvalue("Delete?") == "Delete Subnet"):
    print ('<form method="post" action="subnets.py">')
    subnetToDel = form.getvalue("subnet")
    netmask = form.getvalue("netmask")
    if subnetToDel in subnetList:
        ind = subnetList.index(subnetToDel)
        editedF = outputFile
        editf = open(editedF, 'w')
        f = open(filename, 'r')
        inLin='0'
        subnetLine = str("subnet " + subnetToDel + " netmask " + netmask)
        for lin in f:
            if subnetLine in lin or inLin == '1':
               inLin='1';
               if lin.startswith("}"):
                   inLin='0';
            else:
                # Writing line to file
                editf.write(lin);
        editf.close()
        f.close()
        print ('<h2> # Subnet & Netmask Deleted: ' + subnetToDel + " / " + netmaskList[ind] + "  </h2>")
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
        #executeCmd('copy ' + outputFile + ' ' + inputFile)
        # executeCmd('\cp ' + outputFile + ' ' + inputFile) # linux
    else:
        print ('<h2><font color=\"#9A7D0A\"> ## NO SUCH SUBNET TO DELETE: ' + subnetToDel + ' -  PLEASE TRY AGAIN ## </font></h2>')
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')


# Printing Table:
if not form.getvalue("subnetChosen") and not form.getvalue("Delete?") and not (form.getvalue("newHost?") == "Add New Subnet") and not (form.getvalue("SubmitNewSubnet")):
    print ('<form method="post" action="subnets.py">')
    print ("<h2># Subnet List: </h2>")
    print ("<table><tr><th>| # |</th><th>| SUBNET |</th><th>| NETMASK |</th><th>| EDIT LINK |</th></tr><tr>")
    for i in range(len(subnetList)):
        print ('<td>'+str(i)+'</td><td>'+str(subnetList[i])+'</td> <td>'+str(netmaskList[i])+'<td><input type = "submit" name = "subnetChosen" value = ' +str(subnetList[i])+ ' </td>'
               '</tr><tr>')
    print ("</tr></table>")
    print ("<p></p>")
    print ('<input type="submit" value="Add New Subnet" name = "newHost?" /><br></p>')
print ("</form>")
print ("</body>")
print ("</html>")


