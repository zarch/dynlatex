 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:14:52 2011

@author: Pietro Zambelli

Dynamic LaTex Generator


"""
from datetime import datetime
from filters import Environment
from optparse import OptionParser
import os, shutil
import ConfigParser

def makedir(path):
    """Create directories and subdirectories like `mkdir -p` """
    directories = path.split(os.sep)
    origdir = os.path.abspath(os.path.curdir)
    for _ in directories:
        if os.path.exists(_)==False:
            os.mkdir(_)
        os.chdir(_)
    # return to the previous directory
    os.chdir(origdir)


def get_newpath(filepath, dest):
    """Return the modify directory path and file path given a destination
    >>> get_newpath('something/main.tex', 'build')
    ('build/something', 'build/something/main.tex')
    """
    # split the path in directories and in filename
    dirpath, filename = os.path.split(filepath)
    # split in subdirectories
    directories = dirpath.split(os.sep)
    # insert the destination
    directories.insert(0, dest)
    newdirpath = os.sep.join(directories)
    directories.append(filename)
    newfilepath = os.sep.join(directories)
    return newdirpath, newfilepath



def renderfile(_src, _dst, kargs):
    """Generate a rendred file from a jinja template.
    >>> opt = {'info': {'surname': 'Bonaparte', 'name': 'Napoleone'}, 
    ...        'tab' : {'add_hline': '0,1,-1', 'col_layout': '0:l'}}
    >>> renderfile('examples/main.tex', 'build', opt)
    >>> os.path.isfile('build/examples/main.tex')
    True
    >>> shutil.rmtree('build/')
    """
    # load the template
    template = Environment.from_string(open(_src, 'rb').read())
    # get the new paths, for directory and file
    newdirpath, newfilepath = get_newpath(_src, _dst)
    # no error if existing, make parent directories as needed
    makedir(newdirpath) # like in a shell the comand "make -p" 
    newf = open(newfilepath, 'w')
    # record path, where we are as original directory
    odir = os.path.abspath(os.path.curdir)
    # move into the directory contain the template
    os.chdir(os.path.split(_src)[0])
    # do a render and write it to a file
    #import pdb; pdb.set_trace()
    try:
        newf.write(template.render(**kargs))
        newf.close()
    except TypeError:
        raise TypeError("Are you calling in your template a dictionary or \
obj not define in your configuration file?")
    # move back to original directory
    os.chdir(odir)
    
def istemplate(_src, extensions=['.tex']):
    """Return True the file is a template
    >>> istemplate('examples/main.tex')
    True
    >>> istemplate('examples/main.txt')
    False
    >>> istemplate('examples/main.txt', extensions=['.tex','.txt'])
    True
    """
    ext = os.path.splitext(_src)[-1]
    # src is a template file
    return os.path.isfile(_src) and (ext in extensions)
        


def copy(_src, _dst, link):
    """Make a copy or a link to a file
    >>> copy('examples/copy.txt','examples/copy_no_link.txt', False)
    >>> os.path.islink('examples/copy_no_link.txt')
    False
    >>> copy('examples/copy.txt','examples/copy_link.txt', True)
    >>> os.path.islink('examples/copy_link.txt')
    True
    >>> os.remove('examples/copy_no_link.txt')
    >>> os.remove('examples/copy_link.txt')
    """
    if link: # make a link
        os.symlink(_src, _dst)
    else: # copy
        shutil.copy(_src, _dst)


def get_filelist(_src):
    """Return a filelist given a path
    >>> get_filelist('examples/') # doctest:+ELLIPSIS
    ['examples/style.tex', ..., 'examples/some.csv']
    """
    slist = os.listdir(_src)
    filelist = []
    for _ in slist:
        filelist.append(os.path.join(_src, _))
    return filelist



def processrc(srclist, default, _dst='build', srcext=['.tex',], link='False'): 
    """Process a list of file, understand if is a source file 
    and using as a template for jinja, It work recursively in the directories
    >>> opt = {'info': {'surname': 'Bonaparte', 'name': 'Napoleone'}, 
    ...        'tab' : {'add_hline': '0,1,-1', 'col_layout': '0:l'},
    ...        'euro': {'add_hline': '0,1,-1', 'col_layout': '0:l', 
    ...                 'numberformat' : '{0:.2f} euro'}, #.decode('utf-8')},
    ...        'dollar': {'add_hline': '0,1,-1', 'col_layout': '0:l', 
    ...                 'numberformat' : '{0:.2f} dollar'}, #.decode('utf-8')},
    ...       }
    >>> processrc(['examples/main.tex',], opt, srcext=['.tex',], link=True)
    >>> os.listdir('build/examples/')
    ['main.tex']
    >>> processrc(['examples/',], opt, srcext=['.tex',], link=True)
    >>> directory = os.listdir('build/examples/') 
    >>> directory.sort()
    >>> directory # doctest:+ELLIPSIS
    ['copy.txt', ..., 'test.cfg']
    >>> shutil.rmtree('build/')"""
    if type(srclist)==list:
        for _src in srclist:
            # check if src is a file or a directory
            if istemplate(_src, srcext):
                # src is a file
                renderfile(_src, _dst, default)
            elif os.path.isfile(_src):
                # src is file but not a templpate
                # check, if not unix link=False
                if os.name != 'posix':
                    link = False
                newdirpath, newfilepath = get_newpath(_src, _dst)
                copy(_src, newfilepath, link)
            else:
                # src is a directory
                # get a list of new sources
                #import pdb; pdb.set_trace()
                slist = get_filelist(_src)
                # and then process
                processrc(slist, default, _dst=_dst, srcext=srcext, link=link)
    else:
        raise TypeError('Srclist must be a list here! ;-)')



class Option():
    """Define an empty object"""
    pass



def readgeneral(config):
    """Return an Option object with general information"""
    general = Option()
    items = dict(config.items('general')).keys()
    if 'imgext' in items:
        general.imgext = config.get('general','imgext')
    else:
        general.imgext = '.png, .pdf, .jpg'
        
    if 'srcext' in items:
        general.srcext = config.get('general','srcext')
    else:
        general.srcext = '.tex'
        
    if 'verbose' in items:
        general.verbose = config.getboolean('general','verbose')
    else:
        general.verbose = False
        
    if 'compile' in items:
        general.compile = config.getboolean('general','compile')
    else:
        general.compile = False
        
    if 'link' in items:
        general.link = config.getboolean('general','link')
    else:
        general.link = True
        
    if 'pdfcomand' in items:
        general.pdfcomand = config.get('general','pdfcomand')
    else:
        general.pdfcomand = 'pdflatex build/main.tex'
        
    if 'dest' in items:
        general.dest = config.get('general','dest')
    else:
        general.dest = 'build'
        
    if 'source' in items:
        general.source = config.get('general',
                                    'source').replace(' ','').split(',')

    return general
        

def readcfg(cfg):
    """Return a dictionary with the information read from a 
    configuration file"""
    config = ConfigParser.ConfigParser()
    config.readfp(open(cfg))
    sections = config.sections()
    #import pdb; pdb.set_trace()
    opt = {}
    opt['general'] = readgeneral(config)
    sections.remove('general')
    for sec in sections:
        # build a dictionary
        opt[sec] = dict(config.items(sec))
    return opt

    
if __name__ == "__main__":
    usage = "usage: %prog [options] SOURCE"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dest", dest="dest", default='build',
                      help="Default is put inside a 'build' directory", 
                      metavar="DIRECTORY")
    parser.add_option("-c", "--cfg", dest="cfg", default='',
                      help="Define your configure file", metavar="FILE")
    parser.add_option("-s", "--srcext", dest="srcext", default='.tex',
                      help="Source valid extensions like:'.tex, .txt' ", 
                      metavar="STRING")
    parser.add_option("-i", "--imgext", dest="imgext", 
                      default='.png, .pdf, .jpg',
                      help="Images valid extensions like:'.png, .pdf, .jpg' ", 
                      metavar="STRING")
    parser.add_option("-x", "--compile", action="store_true", dest="compile", 
                      default=False, metavar="BOOLEAN",
                      help="Compile generated latex to produce pdf")
    parser.add_option("-p", "--pdfcomand", dest="pdfcomand", 
                      default='pdflatex build/main.tex',
                      help="Define the comand that you want to use to compile LaTex files", 
                      metavar="STRING")
    parser.add_option("-l", "--link", action="store_true", dest="link", 
                      default=False,  metavar="BOOLEAN",
                      help="For not source files, make  a link the build directory")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", 
                      default=False,  metavar="BOOLEAN",
                      help="Get more Info")
    
    (options, args) = parser.parse_args()
    
    if options.cfg:
        print options.cfg
        opt = readcfg(options.cfg)
        options = opt.pop('general')
    else:
        opt = {}
    
    if args:
        options.source = args
    
    if options.source:
        #import pdb; pdb.set_trace()
        # last comand:
        # $ python2 dyn.py -c examples/test.cfg examples/main.tex
        processrc(options.source, opt, 
                  _dst=options.dest, 
                  srcext=options.srcext.replace(' ','').split(','),
                  link=options.link)
    else:
         print('Give me a latex source! Use cfg file or cmd line')
#    if options['compile']:
#        # run compile comand
#        pass
        

#===============================================================================

