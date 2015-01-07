# Confluence.py

Simple python script to use a Atlassian Confluence Wiki via the CLI. 

## Usage
    
    $ python confluence.py --help                                                                                         
    usage: confluence.py [-h] -w WIKIURL -u USERNAME -p PASSWORD
                         {addpage,updatepage,listpages,removepage,getpagecontent,getpagesummary,listspaces,addspace,removespace,adduser,removeuser,deactivateuser,reactivateuser,changeuserpassword,addgroup,removegroup,listgroups,listusers,getallpages,addusertogroup,removeusergromgroup,listusergroups}
                         ...
    
    Confluence wiki API
    
    positional arguments:
      {addpage,updatepage,listpages,removepage,getpagecontent,getpagesummary,listspaces,addspace,removespace,adduser,removeuser,deactivateuser,reactivateuser,changeuserpassword,addgroup,removegroup,listgroups,listusers,getallpages,addusertogroup,removeusergromgroup,listusergroups}
        addpage             Add a page
        updatepage          Update a page
        listpages           List pages in one or all spaces
        removepage          Remove a page
        getpagecontent      Get page content
        getpagesummary      Get page summary
        listspaces          List all spaces
        addspace            Add a space
        removespace         Remove a space
        adduser             Add a user
        removeuser          Remove a user
        deactivateuser      Deactivate a user
        reactivateuser      Reactivate a user
        changeuserpassword  Change user password
        addgroup            Add a goup
        removegroup         Remove a goup
        listgroups          List all goup
        listusers           List all users
        getallpages         Save all pages to local files.
        addusertogroup      Add user to a group
        removeusergromgroup
                            Remove user from a group
        listusergroups      List groups user is in
    
    optional arguments:
      -h, --help            show this help message and exit
      -w WIKIURL, --wikiurl WIKIURL
                            Wiki URL (only FQDN, no / and such)
      -u USERNAME, --username USERNAME
                            Login Username
      -p PASSWORD, --password PASSWORD
                            Login Password



## Examples

Add page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" addpage -f ./content.txt -n "CLI New Page" -s "RAY"
    http://wiki.raymii.org/display/RAY/CLI+New+Page


Remove Page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" removepage -n "CLI New Page" -s "RAY"


Update Page:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" updatepage -f ./content.txt -n "CLI New Page" -s "RAY"
    http://wiki.raymii.org/display/RAY/CLI+New+Page

Get page content (HTML):

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" getpagecontent -n "CLI New Page" -s "RAY"
    <h1>Table of Contents</h1>
    <p><ac:macro ac:name="toc" /></p>
    <h1>Information</h1>

Add Space:

    ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" addspace -n "New Space" -s "NS"

Remove Space:

    ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" removespace -s "NS"

List all spaces:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" listspaces
    NS, New Space, http://wiki.raymii.org/display/NS
    ITS, IT Staff, http://wiki.raymii.org/display/ITS


Add user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" adduser -U "newuser" -N "New user" -E "newuser@raymii.org" -X "password"

Remove user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" removeuser -U newuser

Deactivate user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" deactivateuser -U newuser

Reactivate user:

    $ ./confluence.py --wikiurl="http://wiki.raymii.org" -u "api" -p "" reactivateuser -U newuser


For more actions, run `./confluence.py -h` or see the usage section above.

## More info

[Raymii.org](https://raymii.org)
