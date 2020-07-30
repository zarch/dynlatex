# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:14:52 2011

@author: Pietro Zambelli

Dynamic LaTex Generator


"""
import configparser
import os
import shutil
import sys
from datetime import datetime
from optparse import OptionParser

from filters import Environment

# print "where we are: ", os.getcwd()
# print "where dyn.py is", os.path.abspath(__file__)
sys.path.append(os.path.abspath(__file__))


def makedir(path):
    """Create directories and subdirectories like `mkdir -p` """
    directories = path.split(os.sep)
    origdir = os.path.abspath(os.path.curdir)
    # print 'makedir: ', path
    for _ in directories:
        if os.path.exists(_) == False:
            os.mkdir(_)
        os.chdir(_)
    # return to the previous directory
    os.chdir(origdir)


def renderfile(_src, _dst, kargs):
    """Generate a rendred file from a jinja template.
    >>> makedir('build')
    >>> opt = {'info': {'surname': 'Bonaparte', 'name': 'Napoleone'}, 
    ...        'tab' : {'add_hline': '0,1,-1', 'col_layout': '0:l'}}
    >>> renderfile('examples/main.tex', 'build', opt)
    >>> os.path.isfile('build/main.tex')
    True
    >>> shutil.rmtree('build/')
    """
    # load the template
    with open(_src, "r") as srcfile:
        srcbytes = srcfile.read()

    template = Environment.from_string(srcbytes)
    srcname = os.path.split(_src)[1]
    # get the new paths, for directory and file
    # newdirpath, newfilepath = get_newpath(_src, _dst)
    # no error if existing, make parent directories as needed
    newfilepath = os.path.join(_dst, srcname)
    makedir(_dst)  # like in a shell the comand "make -p"
    with open(newfilepath, "w") as newf:
        # record path, where we are as original directory
        _odir = os.path.abspath(os.path.curdir)
        # move into the directory contain the template
        # in order to respect the path contained in the tempalate
        os.chdir(os.path.split(_src)[0])
        # do a render and write it to a file
        # import pdb; pdb.set_trace()
        try:
            newf.write(template.render(**kargs))
            newf.close()
        except TypeError:
            print(
                ("\n".join(["{0} : {1}".format(k, v) for k, v in list(kargs.items())]))
            )
            raise TypeError(
                "Are you calling in your template a dictionary or \
    obj not define in your configuration file?"
            )
    # could be a variable that as been wrong defined,
    # for example if you delete the int() trasformation of col
    # variable in filter.do_figure
    # move back to original directory
    os.chdir(_odir)


def istemplate(_src, extensions=[".tex"]):
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
    if link:  # make a link
        os.symlink(_src, _dst)
    else:  # copy
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


def processrc(srclist, default, _dst="build", srcext=[".tex",], link=False):
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
    >>> os.listdir('build/')
    ['main.tex']
    >>> processrc(['examples/',], opt, srcext=['.tex',], link=True)
    >>> directory = os.listdir('build/examples/') 
    >>> directory.sort()
    >>> directory # doctest:+ELLIPSIS
    ['copy.txt', ..., 'test.cfg']
    >>> shutil.rmtree('build/')"""
    if type(srclist) == list:
        # start the cicle to render all files
        for _src in srclist:
            if _src[-1] == os.sep:
                _src = _src[:-1]
            # check if src is a file or a directory
            if istemplate(_src, srcext):
                # print 'is a template src: ', _src
                makedir(_dst)
                # src is a file
                renderfile(_src, _dst, default)
            elif os.path.isfile(_src):
                # src is file but not a templpate _dst
                # check, if not unix link=False
                # print 'is a file: ', _src
                if os.name != "posix":
                    link = False
                srcdir, srcname = os.path.split(_src)
                try:
                    makedir(_dst)
                    copy(_src, os.path.join(_dst, srcname), link)
                except OSError:
                    # print "OSError: File exists ", os.path.join(_dst, srcname)
                    # print " the file will not be copied
                    # import pdb; pdb.set_trace()
                    pass
            else:
                # src is a directory
                srcdir = os.path.split(_src)[1]
                _dst = os.path.join(_dst, srcdir)
                # import pdb; pdb.set_trace()
                makedir(_dst)
                # get a list of new sources

                slist = get_filelist(_src)
                # and then process
                processrc(slist, default, _dst=_dst, srcext=srcext, link=link)
    else:
        raise TypeError("Srclist must be a list here! ;-)")


class Option:
    """Define an empty object"""

    pass


def readgeneral(config):
    """Return an Option object with general information"""
    general = Option()
    items = list(dict(config.items("general")).keys())
    if "imgext" in items:
        general.imgext = config.get("general", "imgext")
    else:
        general.imgext = ".png, .pdf, .jpg"

    if "srcext" in items:
        general.srcext = config.get("general", "srcext")
    else:
        general.srcext = ".tex"

    if "verbose" in items:
        general.verbose = config.getboolean("general", "verbose")
    else:
        general.verbose = False

    if "compile" in items:
        general.compile = config.getboolean("general", "compile")
    else:
        general.compile = False

    if "link" in items:
        general.link = config.getboolean("general", "link")
    else:
        general.link = True

    if "pdfcommand" in items:
        general.pdfcommand = config.get("general", "pdfcommand")
    else:
        general.pdfcommand = "pdflatex build/main.tex"

    if "dest" in items:
        general.dest = config.get("general", "dest")
    else:
        general.dest = "build"

    if "source" in items:
        general.source = config.get("general", "source").replace(" ", "").split(",")

    return general


def readcfg(cfg):
    """Return a dictionary with the information read from a 
    configuration file"""
    config = configparser.ConfigParser()
    config.readfp(open(cfg))
    sections = config.sections()
    # import pdb; pdb.set_trace()
    opt = {}
    opt["general"] = readgeneral(config)
    sections.remove("general")
    for sec in sections:
        # build a dictionary
        opt[sec] = dict(config.items(sec))
    return opt


if __name__ == "__main__":
    usage = "usage: %prog [options] SOURCE"
    parser = OptionParser(usage)
    parser.add_option(
        "-d",
        "--dest",
        dest="dest",
        default="build",
        help="Default is put inside a 'build' directory",
        metavar="DIRECTORY",
    )
    parser.add_option(
        "-c",
        "--cfg",
        dest="cfg",
        default="",
        help="Define your configure file",
        metavar="FILE",
    )
    parser.add_option(
        "-s",
        "--srcext",
        dest="srcext",
        default=".tex",
        help="Source valid extensions like:'.tex, .txt' ",
        metavar="STRING",
    )
    parser.add_option(
        "-i",
        "--imgext",
        dest="imgext",
        default=".png, .pdf, .jpg",
        help="Images valid extensions like:'.png, .pdf, .jpg' ",
        metavar="STRING",
    )
    parser.add_option(
        "-x",
        "--compile",
        action="store_true",
        dest="compile",
        default=False,
        metavar="BOOLEAN",
        help="Compile generated latex to produce pdf",
    )
    parser.add_option(
        "-p",
        "--pdfcommand",
        dest="pdfcommand",
        default="pdflatex build/main.tex",
        help="Define the comand that you want to use to compile\
 LaTex files",
        metavar="STRING",
    )
    parser.add_option(
        "-l",
        "--link",
        action="store_true",
        dest="link",
        default=False,
        metavar="BOOLEAN",
        help="For not source files, make  a link the build\
 directory",
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        metavar="BOOLEAN",
        help="Get more Info",
    )

    (options, args) = parser.parse_args()

    optcompile = options.compile

    # print '\n\n   dyn: ', os.getcwd()
    odir = os.path.abspath(os.path.curdir)

    if options.cfg:
        print((options.cfg))
        opt = readcfg(options.cfg)
        options = opt.pop("general")
    else:
        opt = {}

    if args:
        options.source = args

    if options.source:
        if options.dest == None:
            # destination is not define, then make a "build" directory
            # in the folder where we run the program
            options.dest = os.path.join(os.getcwd(), "build")

        # Start to process sources
        processrc(
            options.source,
            opt,
            _dst=options.dest,
            srcext=options.srcext.replace(" ", "").split(","),
            link=options.link,
        )
    else:
        print("Give me a latex source! Use cfg file or cmd line")

    if optcompile:
        # change dir

        odir = os.path.abspath(os.path.curdir)
        print(("moving into: ", options.dest))
        os.chdir(options.dest)
        # run compile comand
        print("Start to compile using: ")
        print((options.pdfcommand))
        print(("=" * 50))
        os.system(options.pdfcommand)
    os.chdir(odir)


# ===============================================================================
