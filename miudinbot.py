#!/usr/bin/python
# -*- coding: koi8-r -*-
# $Id: miudinbot.py,v 0.1 2010/01/17 12:30:42 normanr Exp $
import sys
import xmpp
import urllib,urllib2

miudinurl = "http://miud.in/api-create.php"
miudinstat = "http://miud.in/api-stats.php"
commands={}
i18n={'ru':{},'en':{}}
########################### user handlers start ##################################

i18n['en']['AJUDA']="Eu sou um botim para o miud.in, te ajudo a encurtar as url.\nComandim Disponiveis: %s"
def ajudaHandler(user,command,args,mess):
    lst=commands.keys()
    lst.sort()
    return "AJUDA",', '.join(lst)

i18n['en']['EMPTY']="%s"

i18n['en']['SOBRE']='Jabber bot para o http://miud.in. O encurtador de urls mais simpatico. \n Mantido por: %s'
def sobreHandler(user,command,args,mess):
    return "SOBRE", 'Licio Fernando liciofernando@gmail.com \n http://wiki.github.com/licio/miudinbot/'

i18n['en']['URL']='url curtinha: %s'
def urlHandler(user,command,args,mess):    
    parameters = {'url' : args}
    data = urllib.urlencode(parameters)
    request = urllib2.Request(miudinurl, data)
    response = urllib2.urlopen(request)
    page = response.read()
    return "URL",'%s'%page

i18n['en']['STAT']='url de destino: %s'
def statHandler(user,command,args,mess):
    key = args.split('/',3)[3]
    parameters = {'key' : key}
    data = urllib.urlencode(parameters)
    request = urllib2.Request(miudinstat, data)
    response = urllib2.urlopen(request)
    page = response.read()
    return "STAT", "%s \n  Cliques na pagina: %s" %(page.split(" ",3)[1], page.split(" ",3)[2])

i18n['en']['TWIT']='Enviado para o twitter: %s'
def twitHandler(user,command,args,mess):
    url,user,passwd,msg=args.split(" ",3)
    message = msg + " " + url
    data = urllib.urlencode({"status" : message})
    response = urllib.urlopen("http://%s:%s@twitter.com/statuses/update.xml" %(user,passwd), data)
    return "TWIT", "%s %s" %(msg,url)
    
i18n['en']['COMPE']='%s'
def compeHandler(user,command,args,mess):
    pass


########################### user handlers stop ###################################
############################ bot logic start #####################################
i18n['en']["UNKNOWN COMMAND"]='Comandin desconhecido "%s". Tente "ajuda"'
i18n['en']["UNKNOWN USER"]="I do not know you. Register first."

def presenceCB(conn, mess):
	
	#added by Licio for handler presence
	utype=mess.getType()
	if not utype:
		utype = 'availabe'
		print utype
	if utype == 'subscribe':
    		conn.send(xmpp.Presence(to=mess.getFrom(), typ='subscribed'))
    		print utype


def messageCB(conn,mess):

    text=mess.getBody()
    if not text:
    	text = "compe"
    user=mess.getFrom()
    user.lang='en'      # dup
    if text.find(' ')+1: command,args=text.split(' ',1)
    else: command,args=text,''
    cmd=command.lower()

    if commands.has_key(cmd): reply=commands[cmd](user,command,args,mess)
    else: reply=("UNKNOWN COMMAND",cmd)

    if type(reply)==type(()):
        key,args=reply
        if i18n[user.lang].has_key(key): pat=i18n[user.lang][key]
        elif i18n['en'].has_key(key): pat=i18n['en'][key]
        else: pat="%s"
        if type(pat)==type(''): reply=pat%args
        else: reply=pat(**args)
    else:
        try: reply=i18n[user.lang][reply]
        except KeyError:
            try: reply=i18n['en'][reply]
            except KeyError: pass
    if reply: conn.send(xmpp.Message(mess.getFrom(),reply))

for i in globals().keys():
    if i[-7:]=='Handler' and i[:-7].lower()==i[:-7]: commands[i[:-7]]=globals()[i]

############################# bot logic stop #####################################

def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt: return 0
    return 1

def GoOn(conn):
    while StepOn(conn): pass

if len(sys.argv)<3:
    print "Usage: bot.py username@server.net password"
else:
    jid=xmpp.JID(sys.argv[1])
    user,server,password=jid.getNode(),jid.getDomain(),sys.argv[2]

    conn=xmpp.Client(server)#,debug=[])
    conres=conn.connect()
    if not conres:
        print "Unable to connect to server %s!"%server
        sys.exit(1)
    if conres<>'tls':
        print "Warning: unable to estabilish secure connection - TLS failed!"
    authres=conn.auth(user,password)
    if not authres:
        print "Unable to authorize on %s - check login/password."%server
        sys.exit(1)
    if authres<>'sasl':
        print "Warning: unable to perform SASL auth os %s. Old authentication method used!"%server
    conn.RegisterHandler('message',messageCB)
    conn.RegisterHandler('presence',presenceCB)
    conn.sendInitPresence()
    print "Bot started."
    GoOn(conn)
