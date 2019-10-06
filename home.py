#!C:\Python\Python37-32\python

# # #!/usr/bin/python3.6

import cgi
# import cgitb; cgitb.enable()  # for troubleshooting, comment-out if linux server
import re


#################################
# Writen By: Itay Shay
# ACS / ishay@airspan.com
#
#################################

print ("Content-type: text/html\r\n\r\n")
print ("<html>")
print ("<head><title>DHCPv4 Hosts</title></head>")
print ('<body style=\"background-color:#E8F6F3;\">')
print ('<h1>&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160'
       '&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#160&#64'
      ' <font color=\"#FF4500\">'"      Home Page     "'</font></h1>')

# table border style
print ('<style>table {border-style: ridge;  border-width: 2px; '
       'border-color: #FDF2E9; background-color: #EDBB99;} th  '
       '{border:2px solid #095484;} td {border:2px groove #1c87c9;} </style>')

print ('<h2><li><a >  Welcome to: Airspan ACS DHCP MANAGER  (Ver-1.2) </a></li></h2>')
print ('<p>#</p>')

print ('<h2><li><a > Tool Purpose:</a></li></h2>')
print ('<h3><ul><li><a > To answer users requirements for: </a></li></ul></h3>')
print ('<h4><ul><ul><li><a >Straightforward settings, managing and maintaining dhcp server (automatic dhcpd.conf file editing) </a></li></ul></ul></h4>')
print ('<h4><ul><ul><li><a >To avoid user mistakes and shortening settings time.</a></li></ul></ul></h4>')
print ('<p>#</p>')

print ('<h2><li><a >  Tool Description:   </a></li></h2>')
print ('<h3><ul><li><a > The tool validates user input such as illegal custom options, illegal characters, duplicate MACs / IPs / IMSI etc.   </a></li></ul></h3>')
print ('<h3><ul><li><a > Automatic IMSI and/or MAC conversion  </a></li></ul></h3>')
print ('<h3><ul><li><a > Search Options By: IMSI/ MAC / IP / Host Description  </a></li></ul></h3>')
print ('<h3><ul><li><a > Hosts and Subnets Tables presentation, Table sorting, etc.  </a></li></ul></h3>')
print ('<h3><ul><li><a > Each user change force "dhcpd.conf" automatic file change dhcpd pid restart </a></li></ul></h3>')
print ('<h3><ul><li><a > Global settings to define NIC for listening and ability to export latest "dhcpd.conf" file </a></li></ul></h3>')
print ('<p>#</p>')
print ('<h2><li><a >  Developed by: Airspan ACS Department (Itay Shay).</a></li></h2>')

print ('</body>')


