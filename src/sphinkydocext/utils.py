"""Utils for sphinkydoc"""
import re
import sys
import logging
from distutils.dir_util import mkpath
import os


__all__ = ['quote_split']

def quote_split(str):
    """Splits the string by quotes.
    
    :param str: String to be split.
    
    >>> quote_split('something test "something awesome"')
    ['something', 'test', 'something awesome']
    
    """
    return [p.strip("\" ") for p in re.split("( |[\\\"'].*[\\\"'])", str) if p.strip("\" ")]


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, 
    update=0, verbose=0, skip_dirs=None, log=None, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.
    
    Modified copy_tree, taken from distutils.dir_util.
      
    Both 'src' and 'dst' must be directory names.  If 'src' is not a directory,
    raise DistutilsFileError.  If 'dst' does not exist, it is created with
    'mkpath()'.  The end result of the copy is that every file in 'src' is
    copied to 'dst', and directories under 'src' are recursively copied to
    'dst'.  Return the list of files that were copied or might have been copied,
    using their output name.
    
    The return value is unaffected by 'update' or 'dry_run': it is simply the
    list of all files under 'src', with the names changed to be under 'dst'.
    
    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be copied as
    symlinks (on platforms that support them!); otherwise (the default), the
    destination of the symlink will be copied.
    
    'update' and 'verbose' are the same as for 'copy_file'.
    
    """
    from distutils.file_util import copy_file
    
    if log is None:
        #logging.basicConfig()
        log = logging.getLogger("sphinkydoc")
    
    skip_dirs = skip_dirs or []
    
    if not dry_run and not os.path.isdir(src):
        log.error("cannot copy tree '%s': not a directory", src)
        sys.exit(0)
    try:
        names = os.listdir(src)
    except os.error, (_errno, errstr):
        if dry_run:
            names = []
        else:
            log.error("error listing files in '%s': %s", src, errstr)
            sys.exit(0)
    if not dry_run:
        mkpath(dst)
    outputs = []
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        # pylint: disable-msg=E1101
        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name) #@UndefinedVariable
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name) #@UndefinedVariable
            outputs.append(dst_name)
            # pylint: enable-msg=E1101
        elif os.path.isdir(src_name):
            if n in skip_dirs:
                continue
            
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode, 
                    preserve_times, preserve_symlinks, update, 
                    dry_run=dry_run))
        else:
            copy_file(src_name, dst_name, preserve_mode, 
                preserve_times, update, dry_run=dry_run)
            outputs.append(dst_name)
    
    return outputs
        