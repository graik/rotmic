import os.path as osp

def absfile( filename, resolveLinks=1 ):
    """
    Get absolute file path::
      - expand ~ to user home, change
      - expand ../../ to absolute path
      - resolve links
      - add working directory to unbound files ('ab.txt'->'/home/raik/ab.txt')

    @param filename: name of file
    @type  filename: str
    @param resolveLinks: eliminate any symbolic links (default: 1)
    @type  resolveLinks: 1|0
    
    @return: absolute path or filename
    @rtype: string

    @raise ToolsError: if a ~user part does not translate to an existing path
    """
    if not filename:
        return filename
    r = osp.abspath( osp.expanduser( filename ) )

    if '~' in r:
        raise ToolsError, 'Could not expand user home in %s' % filename

    if resolveLinks:
        r = osp.realpath( r )
    r = osp.normpath(r)
    return r

def approot():
    """
    Root of labrack project.
    
    @return: absolute path of the root of current django app::
             i.e. '/home/py/rotmicproject/'
    @rtype: string
    """
    ## get location of this module
    f = absfile(__file__)
    ## extract path and assume it is 'project_root/rotmic/utils'
    f = osp.split( f )[0] + '/../../'
    return absfile( f )
