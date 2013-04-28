# Confluence.py

Simple python script to use a Atlassian Confluence Wiki via the CLI. 

## Usage
    
    $ ./confluence.py
    usage: confluence.py [-h] -w WIKIURL -u USERNAME -p PASSWORD [-n NAME]
                         [-P PARENTPAGE] [-l LABEL] -a
                         {addpage,removepage,updatepage,getpagecontent,addspace,removespace,listspaces,adduser,removeuser,changeuserpassword,listusergroups,listuserinfo,addgroup,listgroups,removegroup,addusertogroup,removeuserfromgroup}
                         [-s SPACEKEY] [-U NEWUSERNAME] [-N FULLNAME] [-E EMAIL]
                         [-X USERPASSWORD] [-G GROUPNAME] [-D DESCRIPTION]
                         [-f FILE | -S]

## Examples

Add page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a addpage -f ./content.txt -n "CLI New Page" -s "RAY"
    http://wiki.raymii.org/display/RAY/CLI+New+Page


Remove Page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a removepage -n "CLI New Page" -s "RAY"


Update Page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a updatepage -f ./content.txt -n "CLI New Page" -s "RAY"
    http://wiki.raymii.org/display/RAY/CLI+New+Page

Get page content (HTML):

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a getpagecontent -n "CLI New Page" -s "RAY"
    <h1>Table of Contents</h1>
    <p><ac:macro ac:name="toc" /></p>
    <h1>Information</h1>

Add Space:

    ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a addspace -n "New Space" -s "NS"

Remove Space:

    ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a removespace -s "NS"

List all spaces:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a listspaces
    NS, New Space, http://wiki.raymii.org/display/NS
    ITS, IT Staff, http://wiki.raymii.org/display/ITS


Add user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a adduser -U "newuser" -N "New user" -E "newuser@raymii.org" -X "password"

Remove user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a removeuser -U newuser

Deactivate user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a deactivateuser -U newuser

Reactivate user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" -a reactivateuser -U newuser


For more actions, run `./confluence.py -h` or see the usage section above.

## More info

[Raymii.org](https://raymii.org)