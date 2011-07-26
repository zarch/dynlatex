# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:14:52 2011

@author: Pietro Zambelli
"""

import csv
import jinja2
import os


def get_cvsdata(csvfile, delimiter):
    """Return a list from a csv file"""
    f_csv = open(csvfile, 'rb')
    csvdata = csv.reader(f_csv, delimiter = delimiter)
    return [r for r in csvdata]

def datetimeformat(value, form='%H:%M / %d-%m-%Y'):
    """Return date string format as you want"""
    return value.strftime(form)

def add_separator(iterable, lines, separator):
    """Insert separetor in a list"""
    if lines:
        index_add = 0
        for line in lines:
            line = len(iterable) if line == -1 else line
            iterable.insert(line+index_add, separator)
            index_add += 1
    return iterable
    
def get_line(line):
    """Return the layout
    >>> get_line('0,-1')
    [0, -1]
    """
    if line:
        return [int(v) for v in str(line).strip().split(',')]
    
def get_layout(layout):
    """Return the layout
    >>> get_layout('0:l, 1:c, 2:r')
    [(0, 'l'), (1, 'c'), (2, 'r')]
    """
    if layout:
        return [(int(i), t) for i, t in [l.strip().split(':') 
                for l in layout.split(',')]]


def do_columntab(csvfile, vline='', layout='', default='c', delimiter=','):
    """Return a string with the column layout
    Create an example file
    
    >>> data = '''1;2;3
    ... 4;5;6'''
    >>> dat = file('data.csv','w')
    >>> dat.write(data)
    >>> dat.close()
    >>> do_columntab('data.csv',delimiter=';')
    'ccc'
    >>> do_columntab('data.csv', default='r',delimiter=';')
    'rrr'
    >>> do_columntab('data.csv', vline = '0, -1',delimiter=';')
    '|ccc|'
    >>> do_columntab('data.csv', vline = '1',delimiter=';')
    'c|cc'
    >>> do_columntab('data.csv', layout = '0:l',delimiter=';')
    'lcc'
    >>> do_columntab('data.csv', layout = '0:l,1:c,2:r',delimiter=';')
    'lcr'
    """
    data = get_cvsdata(csvfile, delimiter)
    ncols = len(data[0])
    vline = get_line(vline)
    layout = get_layout(layout)
    columns = [default]*ncols
    if layout:
        for clayout in layout:
            i, lay = clayout
            columns[i] = lay
    if vline:
        add_separator(columns, vline, '|')
    return ''.join(columns)
 
   
def make_row(data, hline=[], numberformat = '{0:.2f}'):
    """Return data as require for a latex table
    >>> data = [[1,2,3],[4,5,6]]
    >>> print(make_row(data, numberformat = '{0:.0f}'))
    1 & 2 & 3 \\\\
    4 & 5 & 6 \\\\
    >>> print(make_row(data, numberformat = '{0:.0f}', hline = [0, -1]))
    \hline
    1 & 2 & 3 \\\\
    4 & 5 & 6 \\\\
    \hline
    >>> data = [['Name', 'Weight', 'Heigth'],
    ...         ['Pippo', 58.789, 1.828],
    ...         ['Pluto', 16.983, 0.608]]
    >>> print(make_row(data, hline = [0, 1, -1]))
    \hline
    Name & Weight & Heigth \\\\
    \hline
    Pippo & 58.79 & 1.83 \\\\
    Pluto & 16.98 & 0.61 \\\\
    \hline
    """
    rows = []
    for row in data:
        r_new = []
        for dat in row:
            try:
                r_new.append(numberformat.format(float(dat)))
            except:
                r_new.append(str(dat))
        rows.append(' & '.join(r_new)+' \\\\')
    rows = add_separator(rows, hline, '\hline')
    return '\n'.join(rows)
    
    
def transforminput(vline, hline, layout):
    """Read string and return a list of option
    >>> transforminput('', '', '0:l, 1:c, 2:r')
    ([], [], [(0, 'l'), (1, 'c'), (2, 'r')])
    """
    vline = [int(v) for v in str(vline).strip().split(',')] if vline else []
    hline = [int(h) for h in str(hline).strip().split(',')] if hline else []
    layout = [(int(i), t) for i, t in [l.strip().split(':') 
              for l in layout.split(',')]] if layout else []
    return vline, hline, layout


def do_datatab(csvfile, delimiter = ',',
               numberformat = '{0:.2f}',
               add_hline = ''):
    """Return only the data formating as latex
    >>> import csv
    >>> data = [['Name', 'Weight', 'Heigth'],
    ...         ['Pippo', 58.789, 1.828],
    ...         ['Pluto', 16.983, 0.608]]
    >>> with open('examples/some.csv', 'wb') as f:
    ...     writer = csv.writer(f)
    ...     writer.writerows(data)
    >>> print(do_datatab('examples/some.csv', delimiter=',', add_hline='0,-1'))
    \hline
    Name & Weight & Heigth \\\\
    Pippo & 58.79 & 1.83 \\\\
    Pluto & 16.98 & 0.61 \\\\
    \hline
    """
    #print 'inset data Table from file: ', csvfile
    csvdata = get_cvsdata(csvfile, delimiter)
    add_hline = get_line(add_hline)
    return make_row(csvdata, hline=add_hline, numberformat=numberformat)


def do_table(csvfile, delimiter = ',',
             numberformat = '{0:.2f}',
             position = 'htb!',
             add_vline = '', add_hline = '',
             col_layout = '', col_layout_default='c',
             label = '', caption = '',
             more = '\\scriptsize \n  \\centering'):
    """Read a csv file and return a LaTex table
    >>> import csv
    >>> data = [['Name', 'Weight', 'Heigth'],
    ...         ['Pippo', 58.789, 1.828],
    ...         ['Pluto', 16.983, 0.608]]
    >>> with open('examples/some.csv', 'wb') as f:
    ...     writer = csv.writer(f)
    ...     writer.writerows(data)
    >>> print(do_table('examples/some.csv', delimiter=',',
    ...                add_vline='1', add_hline='0,-1',
    ...                col_layout='0:l', label='WH',
    ...                caption='Weight and height of Pluto and Pippo')
    ...       )
    \\begin{table}[htb!]
      \\scriptsize 
      \\centering
      \\begin{tabular}{ l|cc }
    \\hline
    Name & Weight & Heigth \\\\
    Pippo & 58.79 & 1.83 \\\\
    Pluto & 16.98 & 0.61 \\\\
    \\hline
      \\end{tabular}
      \\caption{ Weight and height of Pluto and Pippo }
      \\label{ WH }
    \\end{table}
    """
    #print 'insert Table from file: ', csvfile
    data = do_datatab(csvfile, delimiter = delimiter,
                      numberformat = numberformat,
                      add_hline = add_hline)
    column = do_columntab(csvfile, delimiter = delimiter, vline=add_vline,
                          layout=col_layout, default=col_layout_default)    
    return table.render(position=position, more=more, column=column, 
                        data=data, caption=caption, label=label)



def get_file(path, extension):
    """Return a list of dictionary with path and name of characterize 
    by a particular extension"""
    flist = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            name, ext = os.path.splitext(filename)
            if ext in extension:
                # It's a figure
                flist.append({'path':filepath, 
                              'name':name})
    return flist
    
def shape(lis, col):
    """Return a iterator to divide a list in different columns
    >>> shped = shape([0,1,2,3,4,5,6,7,8,9], col=3)
    >>> for row in shped:
    ...     print row
    [0, 1, 2]
    [3, 4, 5]
    [6, 7, 8]
    [9]
    """
    cont = 0
    while cont + col < len(lis):
        yield lis[cont:cont + col]
        cont += col
    yield lis[cont:]
                
def do_figure(path, position = 'htb!', more = '\\centering', width=1,
                 caption='', label='',
                 extension = ['.png', '.pdf','.jpg'], col=2):
    """Return Latex code to include figures
    #>>> fig = 'geostat/es1/scatterogram.pdf'
    #>>> do_figure(fig)   
    """
    if os.path.isfile(path):
        #print "insert Figure: ", path
        return figure.render(position=position, more=more, width=width, 
                             fig=path, caption=caption, label=label)
    else:
        #print "insert Figure conatined in:", path
        figulist = get_file(path, extension)
        #import pdb; pdb.set_trace()
        return subfigure.render(position=position, more=more, 
                           figulist=shape(figulist,int(col)), width=width,
                           caption=caption, label=label) 

#==============================================================
# load template from directory
#print '\n\n  filters:',os.getcwd()

abs_pathtemplate = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'templates')
#print 'where the template is: ', abs_pathtemplate

jinjaloader = jinja2.FileSystemLoader(abs_pathtemplate)
environment = jinja2.Environment(loader=jinjaloader)

# add the new filter
environment.filters['datetimeformat'] = datetimeformat
environment.filters['datatab'] = do_datatab
environment.filters['table'] = do_table
environment.filters['figure'] = do_figure

Environment = environment

# instance template
table = environment.get_template('table.tex')  
figure = environment.get_template('figure.tex')  
subfigure = environment.get_template('subfigure.tex')  



if __name__ == "__main__":
    import doctest
    doctest.testmod()