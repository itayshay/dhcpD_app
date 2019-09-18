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
# ### Configuration Variable #####
dhcpdConfFile = 'C:\\Stuff\\scripts\\python\\airspan-guiForDhcp\\dhcpd.conf'
ReadableLocationFile = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\dhcpd.conf'
ifconfigFile = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\ifconfig.out'
sysconfigDhcpdFile = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\dhcpd'
outputFile = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\dhcpd.out'
outputFile2 = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\editedF.conf'
genConfOptionListSatusF = 'C:\\Stuff\\Tools\\Apache-Win64\\Apache24\\htdocs\\GenConfOpListStatus.db'
# Linux:
# inputFile = os.path.join('/etc/sysconfig/', 'dhcpd')
# outputFile = os.path.join('/tmp', 'sysconfigDhcpd.out')
# dhcpdConfFile = os.path.join('/etc/dhcp/', 'dhcpd.conf')
#ifconfigFile = os.path.join('/tmp/', 'ifconfig.out')
#sysconfigDhcpdFile = os.path.join('/etc/sysconfig/', 'dhcpd')
# genConfOptionListSatusF = os.path.join('/var/www/', 'GenConfOpListStatus.db')
#################################

def execCommand(cmd):
    # print ("Executing Command = ", cmd)
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=False)
    return (p.stdin, p.stdout, p.stderr)

filename = dhcpdConfFile
fi = open(filename, 'r'); numOptions = 0 ; numMainOptions=0 #numMainOptions=0
for l in fi:
    if l.startswith("option "):
        numOptions += 1
        numMainOptions+=1
    #if l.startswith("option space"): numMainOptions += 1
fi.close()

x=0
# 2D:
items, lists = 34, numMainOptions;
subOpLineList = [["" for w in range(items)] for r in range(lists)]
subOpValList = [["" for w in range(items)] for r in range(lists)]
subOpCodeList = [["" for w in range(items)] for r in range(lists)]
mainOpList = []

# 2D:
x=0; j=0
fil = open(dhcpdConfFile, 'r')
for line in fil:
    if line.startswith("option "):
        if line.startswith("host"): break
        if "space" in line:
            mainOpList.append(line.split(' ')[2].replace(';',''))
            j+=1; x=0
        elif "code" in line:
            subOpLineList[x][j] = line ;  # print ("subOpLineList[x][j] =", subOpLineList[x][j])
            subOpValList[x][j] = (line.split(' ')[1]).split('.')[-1] ;  # print ("subOpValList[x][j] =", subOpValList[x][j])
        # optionsVal[x] = line.strip("option ");  # print ("optionsVal[x] =", optionsVal[x])
            subOpCodeList[x][j] = line.split("code ", 1)[1].split("= ")[0].strip(" ") ; # print ("subOpCodeList[x][j] =", subOpCodeList[x][j])
            x+=1
            # print (" ### X is %s / j IS %s " %(x,j))
fil.close()

# print ("### subOpLineList[1][j] are: ", subOpLineList[1][2])


print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title>DHCP GUI</title></head>")
print ('<body style=\"background-color:#E8F6F3;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"      Global Settings     "'</font></h1>')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #FDF2E9; background-color: #EDED99;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')

form = cgi.FieldStorage()
print ('<p>' "debugging: form is: " + str(form) + '</p>'); # linux

# execCommand('\ifconfig > /tmp/ifconfig.out') # linux

x=0
regexNic = re.compile(r'(.*?)\: ')
nicNum=3
nic = list(range(0,3))
filename2 = ifconfigFile
fi = open(filename2, 'r');
for line in fi:
    if x == nicNum: break
    if regexNic.match(str(line)):
        # print ("line to examine NIC is = %s" %(line))
        nic[x] = line.split(" ")[0].strip(":") ; # print ("nic[%s] = %s, " %(x, nic[x]))
        x+=1
fi.close()
# print ("nics =", nic)

# Editing "/etc/sysconfig/dhcpd" as below example
# DHCPDARGS=eth0
filename3 = sysconfigDhcpdFile
fi = open(filename3, 'r');
#text = fi.read().strip()
#print ("text =", text.replace(r'DHCPDARGS=.*.?', 'DHCPDARGS=it'))
if form.getvalue("interfacenum?"):
    print ('<form method="post" action="globalSettings.py">')
    nicName = nic[int(form.getvalue("interfacenum?"))]
    # print ("nicName =", nicName)
    editedF = outputFile
    editf = open(editedF, 'w')
    for line in fi:
        if "DHCPDARGS=" in line:
            print ("CURRENT SETTINGS: DHCPDARGS, = ", line)
            editf.write(str('DHCPDARGS='+nicName+"\n"))
        else:
            editf.write(str(line))
        #print ("line is = %s" %(line))
    fi.close()
    editf.close()
    # execCommand('\cp ' + outputFile + ' ' + inputFile) # linux
    # execCommand('service dhcpd restart')
    print ('<h2><font color=\"#9A7D0A\">  &#160&#160 # NOTICE: NIC Listener Changed to: ' +str(nicName)+ '  </font></h2>')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

if not form.getvalue("optionChosen") and not form.getvalue("Delete?") and not form.getvalue("SubmitChanges") and not form.getvalue("viewContent?") and not form.getvalue("interfacenum?"):
    # print ("<p> # </p>")
    print ("<h2><li><a > Select Interface/NIC Listener  </a></li></h2>")
    print ("<ul><li><a >")
    for y, nic in enumerate(nic):
        print ('<form method="post" action="globalSettings.py">')
        print ('<input type = "radio" name = "interfacenum?" value = '+str(y)+' />'+ str(nic) )
    print ('<input type = "submit" value = "Submit" />')
    print ("</form>")
    print ("</a></li></ul>")


# View File Content Pressed:
if not form.getvalue("optionChosen") and not form.getvalue("Delete?") and not form.getvalue("SubmitChanges") and not form.getvalue("interfacenum?"):
    # print ("<p>" ' ' "</p>")
    print ('<form method="post" action="globalSettings.py">')
    print ('<h2><li><a > View dhcpd.conf content, Press:</a> <input type="submit" value="View File Contant" name = "viewContent?" /> </li></h2>')
    fil = open(dhcpdConfFile, 'r')
    if form.getvalue("viewContent?") == "View File Contant":
        print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
        for line in fil:
            print (line + '<p></p>')
    fil.close()


def sortFunc(sBy,mainOp):
    if mainOp == "PNP": j=0
    if mainOp == "PNP1": j=1
    if mainOp == "PNP2": j=2
    newList = []
    tmpList = []
    if sBy == " Sub-Option ":
        for i in range(len(subOpValList[j])):
            if subOpValList[i][j+1]:
                tmpList.append(subOpValList[i][j+1])
        #print ("TEMP LIST = %s " %(tmpList) + '\n')
        for e in sorted(tmpList, key=lambda s: s.lower()):
            newList.append(e) ;
        #print ("LIST BEFORE SORT = %s " %(subOpValList) + '\n')
        # print ("returning new sub-option sorted list = %s " %newList )
        return newList
    elif sBy == " Option Code ":
        for e in sorted(optionsCode):
            newList.append(e) ;
        return newList
    else:
        return False    
    #print ("newList = ", newList)



# find position in 1D list (for sorting)
def findPos(val, lis, j):
    for i in range(len(lis)):
        if val in lis[i][j+1]:
            postn=i ;
            # print (" # pos is %s , for val %s " %(postn,val) )
            return postn ; break

# Add option
if form.getvalue("addOption?"):
    print ('<form method="post" action="globalSettings.py">')
    print ("Add Option Chosen")
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')
    
# Edit option Pressed
if form.getvalue("optionChosen"):
    print ('<form method="post" action="globalSettings.py">')
    f = open(genConfOptionListSatusF, 'r'); mainOption = f.read() ; f.close()
    subOpToEdit = form.getvalue("optionChosen")
    if mainOption == "PNP": j=0
    if mainOption == "PNP1": j=1
    if mainOption == "PNP2": j=2
    x = findPos(subOpToEdit,subOpValList,j)
    print ('<h2> # Main and Sub Options Are: <input type="text" name="mainOption" value= ' + str(mainOption) + ' />' " / "
           '<input type="text" name="subOpToEdit" value= ' + str(subOpToEdit) + ' /></h2>')
    print ('<textarea name = "textcontent" cols = "70" rows = 2">' + str(subOpLineList[x][j+1]) +  '</textarea>')
    print ('<p><input type = "submit" name = "SubmitChanges" value = "Submit Changes"/></p>')
    print ('<input type = "submit" style="background-color:red; width:110px; height:35px" value = "Delete Option" name = "Delete?" />')
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Submit Changes Pressed
if form.getvalue("SubmitChanges"):
    print ('<form method="post" action="globalSettings.py">')
    newSubOpVals = form.getvalue("textcontent")
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# Delete Option Pressed:
if (form.getvalue("Delete?") == "Delete Option"):
    print ('<form method="post" action="globalSettings.py">')
    mainOption = form.getvalue("mainOption")
    subOpToDel = form.getvalue("subOpToEdit")
    lineToDel = form.getvalue("textcontent")
    editedF = outputFile2
    editf = open(editedF, 'w')
    f = open(filename, 'r')
    for l in f:
        if str(lineToDel).strip('\r\n') in l:
            # print("main and sub are in line = %s" %l)
            print ('<h2><font color=\"#9A7D0A\"> # Sub Option Deleted From Main Option </font></h2>')
        else:
            editf.write(str(l))
    f.close()
    editf.close()
    print ('<p><input type = "submit" value = " << Back" name = "Back?" /></p>')

# print Tabel:
if not form.getvalue("viewContent?") and not form.getvalue("optionChosen") and not form.getvalue("Delete?") and not form.getvalue("SubmitChanges") and not form.getvalue("interfacenum?"):
    mainOption = form.getvalue("mainOption?")
    print ('<form method="post" action="globalSettings.py">')
    print ("<h2><li><a > DHCP-D General Options Table: </a></li></h2>")
    # selecting main option
    print ("<ul><li><a > Select Main Option:  ")
    for y, nic in enumerate(mainOpList):
        print ('<form method="post" action="globalSettings.py">')
        print ('<input type = "radio" name = "mainOption?" value = '+str(mainOpList[y])+' />'+ str(mainOpList[y]) )
    print ('<input type = "submit" value = "Submit" />')
    print ("</form>")
    print ("</a></li></ul>")
    # 
    print ("<ul><li><a > Add Option:  ")
    print ('<input type= \"submit\" value= \"Add Option\" name = \"addOption?\" />')
    print ("</form>")
    print ("</a></li></ul>")
    # Table print
    # if not form.getvalue("hostMacChosen") and not form.getvalue("valToSearch") and not form.getvalue("SubmitChanges") and not form.getvalue("Delete?") and not form.getvalue('newHost?'):
    print ('<form method="post" action="globalSettings.py">')
    print ("<table><tr><th>| # |</th> <th>| Option |</th> <th> <input type = \"submit\" style=\"background-color:black;color:white\" name = \"listToSortBy\" value =\" Sub-Option \""
           "</th><th>| Option Line |</th><th>| EDIT |</th></tr><tr>")
    #sort by column:
    listToSortBy = form.getvalue("listToSortBy") ; # print ("listToSortBy = %s " %(listToSortBy))
    if mainOption:
        # print ("setting new val from op list db")
        f = open(genConfOptionListSatusF, 'w')
        f.write(mainOption)
        f.close()
    else:
        f = open(genConfOptionListSatusF, 'r')
        mainOption = f.read()
        # print ("reading option list from file, val is: %s " %mainOption )
        f.close()
    sortList=''
    posList = ''
    if listToSortBy == " Sub-Option ":
        sortList = sortFunc(listToSortBy,mainOption)
        posList = subOpValList
        #x = findPos(val,posList) ; # print (" # Z IS: ", z)
    elif listToSortBy == " Option Code  ":
        sortList = sortFunc(listToSortBy)
    #else:
    #    sortList=subOpValList # optionsList
    z=0
    if mainOption and not sortList:
        if mainOption == "PNP": j=0
        if mainOption == "PNP1": j=1
        if mainOption == "PNP2": j=2
        for i in range(len(subOpValList)):
            if subOpValList[i][j+1]:
                print ('<td>' +str(z)+ '</td><td>' +str(mainOption)+ '</td><td>' +str(subOpValList[i][j+1])+ '</td><td>' + str(subOpLineList[i][j+1]) + '</td>'
                       '<td><input type = "submit" name = "optionChosen" value =' +str(subOpValList[i][j+1])+ ' </td></tr><tr>')
                z+=1
    elif mainOption and sortList:
        # print ("mainOption and sortList")
        if mainOption == "PNP": j=0
        if mainOption == "PNP1": j=1
        if mainOption == "PNP2": j=2
        z=0
        for val in sortList:
            x = findPos(val,posList, j)
            print ('<td>' +str(z)+ '</td><td>' +str(mainOption)+ '</td><td>' +str(subOpValList[x][j+1])+ '</td><td>' + str(subOpLineList[x][j+1]) + '</td>'
                   '<td><input type = "submit" name = "optionChosen" value =' +str(subOpValList[x][j+1])+ ' </td></tr><tr>')
            z+=1
    else: # default table
        for j in range(len(mainOpList)):
            for i in range(len(subOpValList[j])):
                if subOpValList[i][j+1]:
                    print ('<td>' +str(z)+ '</td><td>' +str(mainOpList[j])+ '</td><td>' +str(subOpValList[i][j+1])+ '</td><td>' + str(subOpLineList[i][j+1]) + '</td>'
                           '<td><input type = "submit" name = "optionChosen" value =' +str(subOpValList[x][j+1])+ ' </td></tr><tr>')
                    z+=1
    print ("</tr></table>")
print ("</body>")
print ("</html>")


