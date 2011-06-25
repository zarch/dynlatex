# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:14:52 2011

@author: Pietro Zambelli
"""

import csv
import jinja2
import os



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


def make_column(data, vline=[], layout=[], default='c'):
    """Return a string with the column layout
    >>> data = [[1,2,3],[4,5,6]]
    >>> make_column(data)
    'ccc'
    >>> make_column(data, default='r')
    'rrr'
    >>> make_column(data, vline = [0, -1])
    '|ccc|'
    >>> make_column(data, vline = [1,])
    'c|cc'
    >>> make_column(data, layout = [(0, 'l')])
    'lcc'
    >>> make_column(data, layout = [(0, 'l'),(1,'c'),(2,'r')])
    'lcr'
    """
    ncols = len(data[0])
    columns = [default]*ncols
    if layout:
        for clayout in layout:
            i, lay = clayout
            columns[i] = lay
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
    #print 'csvfile: ',csvfile
    f_csv = open(csvfile, 'rb')
    csvdata = csv.reader(f_csv, delimiter = delimiter)
    csvdata = [r for r in csvdata]
    add_vline, add_hline, col_layout = transforminput(add_vline, add_hline, 
                                                      col_layout)
    column = make_column(csvdata, vline=add_vline, layout=col_layout, 
                         default=col_layout_default)
    data = make_row(csvdata, hline=add_hline, numberformat=numberformat)
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
    

                
def do_figure(path, position = 'htb!', more = '\\centering', width=1,
                 caption='', label='',
                 extension = ['.png', '.pdf','.jpg']):
    """Return Latex code to include figures
    #>>> fig = 'geostat/es1/scatterogram.pdf'
    #>>> do_figure(fig)   
    """
    if os.path.isfile(path):
        return figure.render(position=position, more=more, width=width, 
                             fig=path, caption=caption, label=label)
    else:
        figulist = get_file(path, extension)
        #sub_figures.render() # TODO: fix

#==============================================================
# load template from directory
environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

# add the new filter
environment.filters['datetimeformat'] = datetimeformat
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