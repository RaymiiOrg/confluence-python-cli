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

import sys, xmlrpclib, argparse, string, logging

#
# Logging
#

logger = logging.getLogger(__name__.rpartition('.')[0])
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class ConfluenceSpace(object):
    def __init__(self, token, server):
        self.server = server
        self.token = token

    def get_all(self):
        self.spaces = self.server.confluence2.getSpaces(self.token)
        return self.spaces

    def get_by_key(self,space_key):
        self.space_key = space_key
        self.space = self.server.confluence2.getSpace(self.token,self.space_key)
        return self.space

    def create(self,space_key,space_name):
        self.space_key = space_key
        self.space_name = space_name
        self.space_to_create = {"key":self.space_key,"name":self.space_name}
        self.server.confluence2.addSpace(self.token,self.space_to_create)
        return self.get_by_key(space_key)

    def remove(self,space_key):
        self.space_key = space_key
        self.server.confluence2.removeSpace(self.token,self.space_key)

    def get_all_pages(self,spaceKey):
        self.spacekey = spaceKey
        return self.server.confluence2.getPages(self.token, self.spacekey)

class ConfluenceGroup(object):
    def __init__(self,token,server,groupname):
        self.server = server
        self.token = token
        self.groupname = groupname

    def get_all(self):
        return self.server.confluence2.getGroups(self.token)

    def add(self):
        self.server.confluence2.addGroup(self.token,self.groupname)

    def remove(self):
        self.server.confluence2.removeGroup(self.token,self.groupname,"confluence-users")

class ConfluenceUser(object):
    def __init__(self,token,server,username):
        self.server = server
        self.token = token
        self.username = username

    def create(self,full_name,email,password):
        self.password = password
        self.email = email
        self.full_name = full_name
        self.user_to_create = {"name":self.username,"fullname":self.full_name,"email":self.email}
        self.server.confluence2.addUser(self.token,self.user_to_create,self.password)

    def get_info(self):
        return self.server.confluence2.getUser(self.token,self.username)

    def get_groups(self):
        return self.server.confluence2.getUserGroups(self.token,self.username)

    def remove(self):
        self.server.confluence2.removeUser(self.token,self.username)

    def deactivate(self):
        self.server.confluence2.deactivateUser(self.token,self.username)

    def reactivate(self):
        self.server.confluence2.reactivateUser(self.token,self.username)

    def add_to_group(self,group):
        self.group = group
        self.server.confluence2.addUserToGroup(self.token,self.username,self.group)

    def remove_from_group(self,group):
        self.group = group
        self.server.confluence2.removeUserFromGroup(self.token,self.username,self.group)

    def change_password(self,password):
        self.password = password
        self.server.confluence2.changeUserPassword(self.token,self.username,self.password)

    def get_all(self):
        return self.server.confluence2.getActiveUsers(self.token, True)

class ConfluencePage(object):
    def __init__(self,token,server,name,spaceKey,content,page_id="",label=""):
        self.server = server
        self.token = token
        self.name = name
        self.spaceKey = spaceKey
        self.content = content
        self.label = label
        self.logger = logging.getLogger(
            __name__ + '.'+ self.__class__.__name__
        )
        self.logger.debug('Creating a new instance (name="{}", label="{}")'.format(name, label))

    def add(self,parent_id=0,content=""):
        self.logger.debug("Add page '{}'; label = [{}]".format(self.name, self.label))
        if content:
            self.content = content
        self.parent_id = parent_id
        self.newPost = {"title":self.name,"content":self.content,"space":self.spaceKey,"parentId":str(self.parent_id)}
        self.post_to_wiki = self.server.confluence2.storePage(self.token,self.newPost)
        self.created_page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        self.page_url = self.created_page["url"]
        self.page_id = self.created_page["id"]
        if self.label:
            self.set_label()
        return {"url": self.page_url, "id": self.page_id}

    def update(self,content,parent_id=0):
        self.remove()
        self.parent_id = parent_id
        self.add(str(parent_id),content)

    def get(self):
        self.wanted_page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        return self.wanted_page

    def get_content(self):
        self.wanted_page_id = self.get_page_id
        self.content_values = {"style": "clean"}
        self.page_content = self.wanted_page = self.server.confluence2.renderContet(self.token, self.wanted_page_id,self.content_values)
        return self.page_content


    def get_id(self):
        return self.get()['id']

    def get_content(self):
        return self.get()['content']

    def remove(self):
        self.page = self.server.confluence2.getPage(self.token, self.spaceKey, self.name)
        self.server.confluence2.removePage(self.token, self.page["id"])

    def set_label(self):
        self.page_id = self.get_id()
        self.logger.debug("Set label '{}' on page {}".format(
            self.label, self.page_id))
        if not self.server.confluence2.addLabelByName(self.token, self.label, self.page_id):
            self.logger.debug("Unable to set label '{}' on page ID {}".format(
                self.label, self.page_id))

    def get_content(self):
        return self.get()['content']

    def get_version(self):
        return self.get()['version']

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
    parser.add_argument("-v", "--verbose", help="Enable debug logging", action="store_true")
    subparsers = parser.add_subparsers(dest="action")

    parser_addpage = subparsers.add_parser('addpage', help='Add a page')
    parser_addpage.add_argument("-n", "--name", help="(New) page name", required=True)
    parser_addpage.add_argument("-P", "--parentpage", help="Parent page ID", default="0")
    parser_addpage.add_argument("-l", "--label", help="Page label", default="created_via_api")
    parser_addpage.add_argument("-s", "--spacekey", help="Space Key", required=True)
    files_addpage = parser_addpage.add_mutually_exclusive_group()
    files_addpage.add_argument("-f", "--file", help="Read content from this file")
    files_addpage.add_argument("-S", "--stdin", help="Read content from STDIN", action="store_true")

    parser_addpage = subparsers.add_parser('copypage', help='Copy a page')
    parser_addpage.add_argument("-n", "--name", help="(New) page name", required=True)
    parser_addpage.add_argument("-P", "--parentpage", help="Parent page ID", default="0")
    parser_addpage.add_argument("-l", "--label", help="Page label", default="created_via_api")
    parser_addpage.add_argument("-s", "--spacekey", help="Space Key", required=True)
    parser_addpage.add_argument("-o", "--origin", help="Origin page name", required=True)

    parser_updatepage = subparsers.add_parser('updatepage', help='Update a page')
    parser_updatepage.add_argument("-n", "--name", help="Page name", required=True)
    parser_updatepage.add_argument("-s", "--spacekey", help="Space Key", required=True)
    parser_updatepage.add_argument("-P", "--parentpage", help="Parent page ID", default="0")
    parser_updatepage.add_argument("-l", "--label", help="Page label", default="created_via_api")
    files_updatepage = parser_updatepage.add_mutually_exclusive_group()
    files_updatepage.add_argument("-f", "--file", help="Read content from this file")
    files_updatepage.add_argument("-S", "--stdin", help="Read content from STDIN", action="store_true")

    parser_listpages = subparsers.add_parser('listpages', help='List pages in one or all spaces')
    parser_listpages.add_argument("-s", "--spacekey", help="Space Key", default="")
    parser_listpages.add_argument("-d", "--delimiter", help="Field delimiter", default=", ")

    parser_removepage = subparsers.add_parser('removepage', help='Remove a page')
    parser_removepage.add_argument("-n", "--name", help="Page name", required=True)
    parser_removepage.add_argument("-s", "--spacekey", help="Space Key", required=True)

    parser_getpage = subparsers.add_parser('getpagecontent', help='Get page content')
    parser_getpage.add_argument("-n", "--name", help="Page name", required=True)
    parser_getpage.add_argument("-s", "--spacekey", help="Space Key", required=True)

    parser_getpagesummary = subparsers.add_parser('getpagesummary', help='Get page summary')
    parser_getpagesummary.add_argument("-s", "--spacekey", help="Space Key", required=True)
    parser_getpagesummary.add_argument("-n", "--name", help="Page name", required=True)
    parser_getpagesummary.add_argument("-d", "--delimiter", help="Field delimiter", default=", ")

    parser_listspaces = subparsers.add_parser('listspaces', help='List all spaces')

    parser_addspace = subparsers.add_parser('addspace', help='Add a space')
    parser_addspace.add_argument("-s", "--spacekey", help="Space Key", required=True)
    parser_addspace.add_argument("-D", "--description", help="Space description", required=True)

    parser_removespace = subparsers.add_parser('removespace', help='Remove a space')
    parser_removespace.add_argument("-s", "--spacekey", help="Space Key", required=True)

    parser_adduser = subparsers.add_parser('adduser', help='Add a user')
    parser_adduser.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)
    parser_adduser.add_argument("-N", "--fullname", help="Full name for new user", required=True)
    parser_adduser.add_argument("-E", "--email", help="Email address for new user", required=True)
    parser_adduser.add_argument("-X", "--userpassword", help="Password for new user", required=True)

    parser_removeuser = subparsers.add_parser('removeuser', help='Remove a user')
    parser_removeuser.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    parser_deactuser = subparsers.add_parser('deactivateuser', help='Deactivate a user')
    parser_deactuser.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    parser_reactuser = subparsers.add_parser('reactivateuser', help='Reactivate a user')
    parser_reactuser.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    parser_changepass = subparsers.add_parser('changeuserpassword', help='Change user password')
    parser_changepass.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)
    parser_changepass.add_argument("-X", "--userpassword", help="Password for user", required=True)

    parser_addgroup = subparsers.add_parser('addgroup', help='Add a goup')
    parser_addgroup.add_argument("-G", "--groupname", help="Group name to perform action on.", required=True)

    parser_removegroup = subparsers.add_parser('removegroup', help='Remove a goup')
    parser_removegroup.add_argument("-G", "--groupname", help="Group name to perform action on.", required=True)

    parser_listgroups = subparsers.add_parser('listgroups', help='List all goup')

    parser_usersgroups = subparsers.add_parser('listusers', help='List all users')

    parser_allpages = subparsers.add_parser('getallpages', help='Save all pages to local files.')

    parser_addutog = subparsers.add_parser('addusertogroup', help='Add user to a group')
    parser_addutog.add_argument("-G", "--groupname", help="Group name to perform action on.", required=True)
    parser_addutog.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    parser_removeufromg = subparsers.add_parser('removeusergromgroup', help='Remove user from a group')
    parser_removeufromg.add_argument("-G", "--groupname", help="Group name to perform action on.", required=True)
    parser_removeufromg.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    parser_listusergroups = subparsers.add_parser('listusergroups', help='List groups user is in')
    parser_listusergroups.add_argument("-U", "--newusername", help="Username to perform action on.", required=True)

    args = parser.parse_args()
    return args

def Content(args):
    if not hasattr(args, 'file') or not hasattr(args, 'stdin'):
        content = ""
    elif args.file:
        try:
            content = open(args.file, 'rb').read()
        except:
            error = "Cannot open file: ", args.file
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
    try:
        if args.action == "addpage":
            logger.debug('Command: "addpage", args.name = "{}", args.label = "{}"'.format(
                args.name, args.label))
            new_page = ConfluencePage(
                token,xml_server,args.name,args.spacekey,content,label=args.label)
            new_page.add(args.parentpage)
            print(new_page.get()["url"])
        elif args.action == "copypage":
            content = ConfluencePage(token,xml_server,args.origin,args.spacekey,content).get_content()
            copy_page = ConfluencePage(
                token,xml_server,args.name,args.spacekey,content,label=args.label)
            copy_page.add(args.parentpage)
            print(copy_page.get()["url"])
        elif args.action == "updatepage":
            update_page = ConfluencePage(token,xml_server,args.name,args.spacekey,content,args.parentpage,label=args.label)
            update_page.update(content,args.parentpage)
            update_page.set_label()
            print(update_page.get()['url'])

        elif args.action == "getpagecontent":
            get_page = ConfluencePage(token,xml_server,args.name,args.spacekey,content).get_content()
            print(get_page)

        elif args.action == "getpagesummary":
            page = ConfluencePage(token,xml_server,args.name,args.spacekey,content).get()
            print args.delimiter.join((
             page['id'], page['space'], page['parentId'], page['title'], page['url']))

        elif args.action == "listpages":
            if args.spacekey == "":
                spaces = ConfluenceSpace(token,xml_server).get_all()
            else:
                spaces = [ConfluenceSpace(token,xml_server).get_by_key(args.spacekey)]
            for space in spaces:
                all_pages = ConfluenceSpace(token,xml_server).get_all_pages(space['key'])
                for page in all_pages:
                    print args.delimiter.join((
                     page['id'], page['space'], page['parentId'], page['title'], page['url']))

        elif args.action == "removepage":
            removed_page = ConfluencePage(token,xml_server,args.name,args.spacekey,"").remove()

        elif args.action == "addspace":
            add_space = ConfluenceSpace(token,xml_server).create(args.spacekey,args.name)

        elif args.action == "removespace":
            remove_space = ConfluenceSpace(token,xml_server).remove(args.spacekey)

        elif args.action == "listspaces":
            all_spaces = ConfluenceSpace(token,xml_server).get_all()
            for space in all_spaces:
                print(("%s, %s, %s") % (
                 space['key'], space['name'], space['url']))

        elif args.action == "getallpages":
            all_spaces = ConfluenceSpace(token,xml_server).get_all()
            for space in all_spaces:
                all_pages = ConfluenceSpace(token,xml_server).get_all_pages(space['key'])
                print("Saving space: %s" % space['name'])
                print("------------")
                for page in all_pages:
                    page_content = ConfluencePage(token,xml_server,page['title'],space['key'],"").get_content()
                    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
                    page_filename = space['key'] + "_" + page['title'] + ".html"
                    page_filename = ''.join(c for c in page_filename if c in valid_chars)
                    with open(page_filename, "w") as page_file:
                        try:
                            page_file.write(page_content)
                            page_file.close()
                            print("Saved page: %s" % page_filename)
                        except IOError:
                            error_out('Could not write file: %s' % page['title'])

        elif args.action == "adduser":
            add_user = ConfluenceUser(token,xml_server,args.newusername).create(args.fullname,args.email,args.userpassword)

        elif args.action == "removeuser":
            remove_user = ConfluenceUser(token,xml_server,args.newusername).remove()

        elif args.action == "deactivateuser":
            deactivate_user = ConfluenceUser(token,xml_server,args.newusername).deactivate()

        elif args.action == "reactivateuser":
            reactivate_user = ConfluenceUser(token,xml_server,args.newusername).reactivate()

        elif args.action == "changeuserpassword":
            change_pass = ConfluenceUser(token,xml_server,args.newusername).change_password(args.userpassword)

        elif args.action == "listuserinfo":
            user_info = ConfluenceUser(token,xml_server,args.newusername).get_info()
            for key,value in user_info.items():
                print(("%s: %s") % (key,value))

        elif args.action == "addgroup":
            add_group = ConfluenceGroup(token,xml_server,args.groupname).add()

        elif args.action == "removegroup":
            remove_group = ConfluenceGroup(token,xml_server,args.groupname).remove()

        elif args.action == "addusertogroup":
            add_user_to_group = ConfluenceUser(token,xml_server,args.newusername).add_to_group(args.groupname)

        elif args.action == "removeuserfromgroup":
            remove_user_from_group = ConfluenceUser(token,xml_server,args.newusername).remove_from_group(args.groupname)

        elif args.action == "listgroups":
            allgroups = ConfluenceGroup(token,xml_server,"users").get_all()
            for group in allgroups:
                print(group)

        elif args.action == "listusers":
            allusers = ConfluenceUser(token,xml_server,"users").get_all()
            for user in allusers:
                print(user)

        elif args.action == "listusergroups":
            user_groups = ConfluenceUser(token,xml_server,args.newusername).get_groups()
            for group in user_groups:
                print(group)

    except xmlrpclib.Fault as err:
        print(("Error: %d: %s") % (err.faultCode, err.faultString))

def main():
    args = Parser()

    if args.verbose:
        console_handler.setLevel(logging.DEBUG)

    content = Content(args)
    server = Connect(args)
    Actions(server["token"],server["xml_server"],args,content)

if __name__ == '__main__':
    main()
