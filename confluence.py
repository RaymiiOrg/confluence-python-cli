#!/usr/bin/env python
# Copyright (C) 2013  Remy van Elst

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, xmlrpclib, argparse

class ConfluenceSpace(object):
    def __init__(self, token, server):
        self.server = server
        self.token = token

    def get_all_spaces(self):
        self.spaces = self.server.confluence2.getSpaces(self.token)
        return self.spaces

    def get_space_by_key(self,space_key):
        self.space_key = space_key
        self.space = self.server.confluence2.getSpace(self.token,self.space_key)
        return self.space

    def create_space(self,space_key,space_name):
        self.space_key = space_key
        self.space_name = space_name
        self.space_to_create = {"key":self.space_key,"name":self.space_name}
        self.server.confluence2.addSpace(self.token,self.space_to_create)
        return self.get_space_by_key(space_key)

    def remove_space(self,space_key):
        self.space_key = space_key
        self.server.confluence2.removeSpace(self.token,self.space_key)

class ConfluenceGroup(object):
    def __init__(self,token,server,groupname):
        self.server = server
        self.token = token
        self.groupname = groupname

    def get_all_groups(self):
        return self.server.confluence2.getGroups(self.token)

    def add_group(self):
        self.server.confluence2.addGroup(self.token,self.groupname)

    def remove_group(self):
        self.server.confluence2.removeGroup(self.token,self.groupname,"confluence-users")


class ConfluenceUser(object):
    def __init__(self,token,server,username):
        self.server = server
        self.token = token
        self.username = username

    def create_user(self,full_name,email,password):
        self.password = password
        self.email = email
        self.full_name = full_name
        self.user_to_create = {"name":self.username,"fullname":self.full_name,"email":self.email}
        self.server.confluence2.addUser(self.token,self.user_to_create,self.password)

    def get_user_info(self):
        return self.server.confluence2.getUser(self.token,self.username)

    def get_user_groups(self):
        return self.server.confluence2.getUserGroups(self.token,self.username)

    def remove_user(self):
        self.server.confluence2.removeUser(self.token,self.username)

    def deactivate_user(self):
        self.server.confluence2.deactivateUser(self.token,self.username)

    def reactivate_user(self):
        self.server.confluence2.reactivateUser(self.token,self.username)

    def add_user_to_group(self,group):
        self.group = group
        self.server.confluence2.addUserToGroup(self.token,self.username,self.group)

    def remove_user_from_group(self,group):
        self.group = group
        self.server.confluence2.removeUserFromGroup(self.token,self.username,self.group)   

    def change_user_password(self,password):
        self.password = password
        self.server.confluence2.changeUserPassword(self.token,self.username,self.password)   


class ConfluencePage(object):
    def __init__(self,token,server,name,spaceKey,content,page_id="",label=""):
        self.server = server
        self.token = token
        self.name = name
        self.spaceKey = spaceKey
        self.content = content
        self.label = label

    def add_page(self,parent_id=0,content=""):
        if content:
            self.content = content 
        self.parent_id = parent_id
        self.newPost = {"title":self.name,"content":self.content,"space":self.spaceKey,"parentId":str(self.parent_id)}
        self.post_to_wiki = self.server.confluence2.storePage(self.token,self.newPost)
        self.created_page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        self.page_url = self.created_page["url"]
        self.page_id = self.created_page["id"]
        if self.label:
            self.set_page_label()
        return {"url": self.page_url, "id": self.page_id}

    def update_page(self,content,parent_id=0):
        self.remove_page()
        self.parent_id = parent_id
        self.add_page(str(parent_id),content)

    def get_page(self):
        self.wanted_page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        return self.wanted_page

    def get_page_content(self):
        self.wanted_page_id = self.get_page_id
        self.content_values = {"style": "clean"}
        self.page_content = self.wanted_page = self.server.confluence2.renderContet(self.token, self.wanted_page_id,self.content_values)
        return self.page_content
        

    def get_page_id(self):
        return self.get_page()['id']

    def get_page_content(self):
        return self.get_page()['content']

    def remove_page(self):
        self.page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        self.server.confluence2.removePage(self.token, self.page["id"])

    def set_page_label(self):
        self.page_id = self.get_page_id()
        self.server.confluence2.addLabelByName(self.token, self.label, self.page_id) 

    def get_page_content(self):
        return self.get_page()['content']

    def get_page_version(self):
        return self.get_page()['version']

class ConfluenceAuth(object):
    def __init__(self,server,username,password):
        self.server = server
        self.username = username
        self.password = password

    def login(self):
        self.token = self.server.confluence2.login(self.username, self.password)
        return self.token

def error_out(error_message):
    print("Error: ")
    print(error_message)
    exit()


def Parser():
    parser = argparse.ArgumentParser(description="Confluence wiki API")
    parser.add_argument("-w", "--wikiurl", help="Wiki URL (only FQDN, no / and such)", required=True)
    parser.add_argument("-u", "--username", help="Login Username", required=True)
    parser.add_argument("-p", "--password", help="Login Password", required=True)
    parser.add_argument("-n", "--name", help="(New) page or (new) Space name")
    parser.add_argument("-P", "--parentpage", help="Parent page ID", default="0")
    parser.add_argument("-l", "--label", help="Page label", default="created_via_api")
    parser.add_argument("-a", "--action", help="What to do?", choices=
        ['addpage', 'removepage', 'updatepage', 'getpagecontent', 'addspace', 
         'removespace', 'listspaces', 'adduser', 'removeuser', 'changeuserpassword', 
         'listusergroups', 'listuserinfo', 'addgroup', 'listgroups', 'deactivateuser',
        'removegroup', 'addusertogroup', 'removeuserfromgroup', 'reactivateuser'], required=True)
    parser.add_argument("-s", "--spacekey", help="Space Key")
    parser.add_argument("-U", "--newusername", help="Username for user to add or remove or update")
    parser.add_argument("-N", "--fullname", help="Full name for new user")
    parser.add_argument("-E", "--email", help="Email address for new user")
    parser.add_argument("-X", "--userpassword", help="Password for new user")
    parser.add_argument("-G", "--groupname", help="Group name for group to add, remove or add or remove user to/from.")
    parser.add_argument("-D", "--description", help="Space description")
    files = parser.add_mutually_exclusive_group()
    files.add_argument("-f", "--file", help="Read content from this file")
    files.add_argument("-S", "--stdin", help="Read content from STDIN", action="store_true")
    args = parser.parse_args()
    return args

def Content(args):
    if args.file:
        try:
            content = open(args.file, 'rb').read()
        except:
            error = "Cannot open file: ", filename
            raise
    elif args.stdin:
        content = sys.stdin.read()
    else:
        content = ""
    return content

def Connect(args):
    wiki_url = args.wikiurl + "/rpc/xmlrpc"
    xml_server = xmlrpclib.Server(wiki_url)
    try:
        token = ConfluenceAuth(xml_server,args.username,args.password).login()
    except xmlrpclib.Fault as err:
        error_out("%d: %s" % ( err.faultCode, err.faultString))
    return {"token":token,"xml_server":xml_server}

def Actions(token,xml_server,args,content):
    if args.action == "addpage":
        if not content:
            error_out("Content (-f for filename or -S for STDIN) is required")
        if not args.name:
            error_out("Page name (-n) is required")
        if not args.spacekey:
            error_out("Space key (-s) is required")
        try:
            new_page = ConfluencePage(token,xml_server,args.name,args.spacekey,content,args.label)
            new_page.add_page(args.parentpage)
            print(new_page.get_page()["url"])
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "updatepage":
        if not content:
            error_out("Content (-f for filename or -S for STDIN) is required")
        if not args.name:
            error_out("Page name (-n) is required")
        if not args.spacekey:
            error_out("Space key (-s) is required")
        try:
            update_page = ConfluencePage(token,xml_server,args.name,args.spacekey,content,args.parentpage,args.label)
            update_page.update_page(content,args.parentpage)
            update_page.set_page_label()
            print(update_page.get_page()['url'])
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "getpagecontent":
        if not args.name:
            error_out("Page name (-n) is required")
        if not args.spacekey:
            error_out("Space key (-s) is required")
        try:
            get_page = ConfluencePage(token,xml_server,args.name,args.spacekey,content).get_page_content()
            print(get_page)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "removepage":
        if not args.name:
            error_out("Page name (-n) is required.")
        if not args.spacekey:
            error_out("Space key (-s) is required.")
        try:
            removed_page = ConfluencePage(token,xml_server,args.name,args.spacekey,"").remove_page()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "addspace":
        if not args.name:
            error_out("Space name (-n) is required.")
        if not args.spacekey:
            error_out("Space key (-s) is required.")
        try:
            add_space = ConfluenceSpace(token,xml_server).create_space(args.spacekey,args.name)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "removespace":
        if not args.spacekey:
            error_out("Space key (-s) is required.")
        try:
            remove_space = ConfluenceSpace(token,xml_server).remove_space(args.spacekey)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "listspaces":
        try:
            all_spaces = ConfluenceSpace(token,xml_server).get_all_spaces()
            for space in all_spaces:
                print(("%s, %s, %s") % (
                     space['key'], space['name'], space['url']))
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "adduser":
        if not args.newusername:
            error_out("Username (-U) is required.")
        if not args.fullname:
            error_out("Users Full Name (-N) is required.")
        if not args.email:
            error_out("Email address for user (-E) is required.")
        if not args.userpassword:
            error_out("Password for new user (-X) is required.")
        try:
            add_user = ConfluenceUser(token,xml_server,args.newusername).create_user(args.fullname,args.email,args.userpassword)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "removeuser":
        if not args.newusername:
            error_out("Username (-U) to remove is required.")
        try:
            remove_user = ConfluenceUser(token,xml_server,args.newusername).remove_user()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "deactivateuser":
        if not args.newusername:
            error_out("Username (-U) to deactivate is required.")
        try:
            deactivate_user = ConfluenceUser(token,xml_server,args.newusername).deactivate_user()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "reactivateuser":
        if not args.newusername:
            error_out("Username (-U) to reactivate is required.")
        try:
            reactivate_user = ConfluenceUser(token,xml_server,args.newusername).reactivate_user()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "changeuserpassword":
        if not args.newusername:
            error_out("Username to change password for (-U) is required.")
        if not args.userpassword:
            error_out("Password to change (-X) is required.")
        try:
            change_pass = ConfluenceUser(token,xml_server,args.newusername).change_user_password(args.userpassword)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "listuserinfo":
        if not args.newusername:
            error_out("Username (-U) is required.")
        try:
            user_info = ConfluenceUser(token,xml_server,args.newusername).get_user_info()
            for key,value in user_info.items():
                print(("%s: %s") % (key,value))
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "addgroup":
        if not args.groupname:
            error_out("Groupname (-G) is required.")
        try:
            add_group = ConfluenceGroup(token,xml_server,args.groupname).add_group()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "removegroup":
        if not args.groupname:
            error_out("Groupname (-G) is required.")
        try:
            remove_group = ConfluenceGroup(token,xml_server,args.groupname).remove_group()
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "addusertogroup":
        if not args.groupname:
            error_out("Groupname (-G) is required.")
        if not args.newusername:
            error_out("Username (-U) to add to group is required.")
        try:
            add_user_to_group = ConfluenceUser(token,xml_server,args.newusername).add_user_to_group(args.groupname)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "removeuserfromgroup":
        if not args.groupname:
            error_out("Groupname (-G) is required.")
        if not args.newusername:
            error_out("Username (-U) to remove from group is required.")
        try:
            remove_user_from_group = ConfluenceUser(token,xml_server,args.newusername).remove_user_from_group(args.groupname)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "listgroups":
        try:
            allgroups = ConfluenceGroup(token,xml_server,"users").get_all_groups()
            for group in allgroups:
                print(group)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

    elif args.action == "listusergroups":
        if not args.newusername:
            error_out("Username (-U) to get groups is required.")
        try:
            user_groups = ConfluenceUser(token,xml_server,args.newusername).get_user_groups()
            for group in user_groups:
                print(group)
        except xmlrpclib.Fault as err:
            print(("Error: %d: %s") % (err.faultCode, err.faultString))

def main():
    args = Parser()
    content = Content(args)
    server = Connect(args)
    Actions(server["token"],server["xml_server"],args,content)

main()