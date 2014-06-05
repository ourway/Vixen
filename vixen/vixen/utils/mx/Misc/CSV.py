""" CSV (Comma Separated Values) table format reader/writer.

    The two classes read and write CSV data. It's a fairly simple
    format for data exchange with nearly all spreadsheets, databases,
    organizers, etc.

    The reader class is built to be easy on the data passed in: small
    errors like missing commas don't cause an exception (but do set a
    variable to indicate this). Data is converted from CSV text into a
    an internal format which can then be extracted into different
    forms of table representation.

    The writer writes standard CSV files and knows about quoting
    rules, separator handling etc. so that interfacing to spreadsheets
    and databases should pose no problem.

    Both classes can be subclassed to enhance/modify their behaviour.

    Copyright (c) 2000-2005, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2008, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
__version__ = '1.0'
_debug = 0

import re,string,sys,types,exceptions
import mx.Tools.NewBuiltins
from mx import TextTools

### Errors

class Error(exceptions.StandardError):
    pass

### Reader base class

class Reader:

    # Did decoding have errors ?
    errors = 0

    # If there were errors, then this list contains the line number of
    # the lines with errors
    errorlines = None
    
    # List of lines, each being a list of strings
    lines = None

    # Width of the received data (max. number of entries per line)
    width = 0
    
    # List of column names found in the data's first row; possibly
    # filtered through .filter_header()
    columns = None

    # String of separator characters which are used to separate items
    # on an input line
    separators = ',;\t'

    # My version, which runs in exponential time for '"abcdefgh...'
    # parseitem = re.compile(r'"([^"]+|"")*"|[^",;\015\012]*')

    # Thanks to Andrew Kuchling for helping me with this "simple" RE
    parseitem = re.compile(r'"([^"]|"")*"|[^"' + separators + r'\015\012]*')

    def __init__(self, separators=None):

        if separators is not None:
            self.parseitem = re.compile(r'"([^"]|"")*"|[^"'
                                        + separators + r'\015\012]*')

    def flush(self):

        """ Empty the object and reset errors
        """
        self.lines = None
        self.width = 0
        self.errors = 0
        self.columns = None

    def load(self, file, header=1, columns=None,

             StringType=types.StringType):

        """ Read a file.

            If header is true (default), the first line of input is
            interpreted as list of column names.

            If columns is given as list of strings, these columns
            names are used.

            If both header and columns are used, columns overrides the
            columns set by reading the header line. This is useful to
            override header information from the input data.

        """
        if type(file) == StringType:
            file = open(file,'rb')
        text = file.read()
        file.close()
        self.lines = self._decode(text)
        if header:
            self.process_header()
        if columns is not None:
            self.set_columns(columns)

    def loads(self, text, header=1, columns=None):

        """ Read the given text

            If header is true (default), the first line of input is
            interpreted as list of column names.

            If columns is given as list of strings, these columns
            names are used.

            If both header and columns are used, columns overrides the
            columns set by reading the header line. This is useful to
            override header information from the input data.

        """
        self.lines = self._decode(text)
        if header:
            self.process_header()
        if columns is not None:
            self.set_columns(columns)

    def list(self):

        """ Return the current data as list of lists, each having
            self.width string entries.

            Missing entries are set to None.

        """
        width = self.width
        lines = self.lines
        table = [None] * len(lines)
        for i, row in irange(lines):
            row = row[:]
            if len(row) < width:
                row[len(row):] = [None]*(width-len(row))
            table[i] = row
        return table

    def dictionary(self):

        """ Return the current data as dictionary of lists of strings,
            with one entry for each column.

            .columns must have been set using .set_columns() or by
            processing a given CSV header.

        """
        table = {}
        lines = self.lines
        keys = self.columns
        if keys is None:
            raise Error,'no columns set'
        rows = len(lines)
        for k in keys:
            table[k] = [None] * rows
        for i, key in irange(keys):
            column = table[key]
            for j, row in irange(lines):
                if len(row) > i:
                    column[j] = row[i]
        return table

    def objects(self,constructor):

        """ Builds a list of objects by calling the given constructor
            with keywords defined by mapping column names to values for
            each input line.

            .columns must have been set using .set_columns() or by
            processing a given CSV header.

        """
        lines = self.lines
        keys = self.columns
        if keys is None:
            raise Error,'no columns set'
        objs = [None] * len(lines)
        for i,line in lines:
            kws = dict(tuples(keys, line))
            objs[i] = apply(constructor,(),kws)
        return l

    def process_header(self):

        """ Process the header data.

            This also sets the .columns attribute. The header is
            removed from the data in .lines after having been
            processed.

            The header is passed through .filter_header() before
            interpreting it as list of column names.

        """
        lines = self.lines
        if len(lines) < 1:
            raise Error,'missing header data'
        self.columns = self.filter_header(lines[0])
        del lines[0]

    def set_columns(self, columns):

        """ Sets the column names to use.

            This overrides any column names possibly given in the read
            data.

        """
        self.columns = columns

    def filter_header(self, header,

                      lower=TextTools.lower,split=string.split,
                      join=string.join):

        """ Filter the given header line.

            The base class converts the column names to all lowercase
            and removes any whitespace included in the header.

            This method is only called in case the header was read
            from the data provided to the object.

        """
        l = [''] * len(header)
        for i,column in irange(header):
            l[i] = join(split(lower(column)),'')
        return l

    def description(self, header=1):

        """ Return a list of tuples (column name, max length) found in the
            data. 

            If header is true (default), the column names themselves
            are included in the calculation.

        """
        lines = self.lines
        columns = self.columns
        width = len(columns)
        if header:
            lengths = []
            for column in columns:
                lengths.append(len(column))
        else:
            lengths = [0] * width
        for row in self.lines:
            for i,o in irange(row[:width]):
                if len(o) > lengths[i]:
                    lengths[i] = len(o)
        return map(None,columns,lengths)

    def _decode(self,text,

                find=string.find):

        """ Decode the CSV data in text.

            Internal method. Do not use directly.
        
        """
        lines = []
        x = 0
        length = len(text)
        width = 0
        errorlines = []
        match = self.parseitem.match
        separators = self.separators
        while x < length:
            l = []
            while x <= length:
                # Find next token
                m = match(text,x)
                if not m:
                    # End of line
                    break
                y = m.regs[0][1]
                l.append(text[x:y])
                if _debug:
                    print x,repr(l[-1])
                x = y + 1
                if x > length:
                    break
                # Check validity
                if text[y:x] not in separators:
                    if text[y:y+2] == '\015\012':
                        # Handle CRLF
                        x = y + 2
                    elif text[y:x] not in '\015\012':
                        # Syntax error: missing ',' or ';'
                        # Action: skip to end of line
                        y = find(text,'\012',x)
                        if y < 0:
                            y = find(test,'\015',x)
                        if y < 0:
                            # Skip to end of text
                            x = length
                        else:
                            x = y + 1
                        if _debug:
                            print 'errors in',l,x
                        errorlines.append(len(lines))
                    # else: found single CR or LF
                    break
            if len(l) > width:
                width = len(l)
            if _debug:
                print 'adding',l,x,repr(text[x:x+5])
            lines.append(l)
        self.width = width
        if errorlines:
            self.errors = 1
            self.errorlines = errorlines
        return map(self._unquote,lines)

    def _unquote(self,line,

                 replace=string.replace):

        """ Unquote a CSV style quoted line of text.

            Internal method. Do not use directly.
        
        """
        for i,text in irange(line):
            if text[:1] == '"' and text[-1:] == '"':
                text = text[1:-1]
            line[i] = replace(text,'""','"')
        return line

    def __len__(self):

        return len(self.lines)

    def __str__(self):

        lines = self.list()
        desc = self.description()
        width = 0
        output = []
        write = output.append
        for col in desc:
            write('%-*s|' % (col[1],col[0]))
        write('\n')
        for col in desc:
            write('=' * col[1] + '+')
        write('\n')
        for line in lines:
            for i,item in irange(line):
                write('%-*s|' % (desc[i][1],item))
            write('\n')
        return string.join(output,'')

### Writer base class

class Writer:

    # Column names
    columns = None

    # CSV text
    text = ''

    # Separator to use for separating fields of a row (default: comma)
    separator = ','

    # End-of-line marker to use (default: CRLF)
    lineend = '\015\012'

    def __init__(self, separator=None, lineend=None):

        if separator is not None:
            self.separator = separator
        if lineend is not None:
            self.lineend = lineend

    def flush(self):

        """ Flush the data currently stored in the writer.
        """
        self.text = ''
        self.columns = None

    def set_columns(self, columns, header=1,

                    join=string.join):

        """ Sets the output columns.

            If header is true, a column name line is added to the
            output.

            Columns can only be set once per session and must be set
            prior to adding any data. columns has to be a list of
            column names.

            It is assured that no more than len(columns) items are
            written for each row. All rows are filled up with ""
            entries to have an equal number of items.

        """
        if columns == self.columns and not header:
            # Nothing to do
            return
        elif self.columns:
            raise Error,'cannot write columns more than once per session'
        self.columns = columns
        if header:
            if self.text:
                raise Error,'cannot add header to already written data'
            headerline = self._quote(columns)
            self.text = join(headerline, self.separator) + self.lineend

    def feed_list(self,table,

                  join=string.join):

        """ Feeds a table (list of rows) which is converted
            to CSV. 

            No more than len(columns) items are written for each
            row. All rows are filled up with "" entries to have an
            equal number of items. None entries are converted to empty
            strings, all other objects are stringified.

        """
        columns = self.columns
        if columns:
            rowlen = len(columns)
        else:
            # Calculate the max. number of columns in the table
            rowlen = max(map(len,table))

        # Prepare an empty table
        t = [None] * len(table)
        _quote = self._quote

        # Fill in data
        for i,row in irange(table):
            row = _quote(row[:rowlen])
            if len(row) < rowlen:
                row[len(row):] = ['""'] * (rowlen - len(row))
            t[i] = join(row,self.separator)

        # Add final CRLF and add as CSV text
        t.append('')
        self.text = self.text + join(t,self.lineend)

    def feed_dict(self,table,rows=None,

                  join=string.join):

        """ Feeds a table (dict of lists) which is converted
            to CSV. 

            Only the keys set as column names are used to form the CSV
            data.

            All lists in the dictionary must have equal length or at
            least rows number of entries, if rows is given. None
            entries are converted to empty strings, all other objects
            are stringified.

        """
        columns = self.columns
        if not columns:
            raise Error,'no output columns set'
        rowlen = len(columns)

        # Create an emtpy table
        if not rows:
            rows = 0
            for column in columns:
                nrows = len(table[column])
                if nrows > rows:
                    rows = nrows
        rowindices = trange(rows)
        t = [None] * rows
        for i in rowindices:
            t[i] = [None] * rowlen
            
        # Fill the table
        for j,k in irange(columns):
            for i in rowindices:
                t[i][j] = table[k][i]
                
        # Quote and join lines
        t = map(self._quote,t)
        t = map(join,t,(self.separator,) * rows)

        # Add final CRLF and store CSV text
        t.append('')
        self.text = self.text + join(t,self.lineend)

    def feed_objects(self,objects,

                     join=string.join,getattr=getattr):

        """ Feeds a sequence of objects which is converted to CSV. 

            For each object the set column names are interpreted as
            object attributes and used as basis for the CSV data.

            None values are converted to empty strings, all other
            attributes are added stringified.

        """
        columns = self.columns
        if not columns:
            raise Error,'no output columns set'
        rowlen = len(columns)

        # Create an emtpy table
        rows = len(objects)
        rowindices = trange(rows)
        t = [None] * rows
        for i in rowindices:
            t[i] = [None] * rowlen
            
        # Fill the table
        icols = irange(columns)
        for i in rowindices:
            obj = objects[i]
            for j,name in icols:
                t[i][j] = str(getattr(obj, name))
                
        # Quote and join lines
        t = map(self._quote, t)
        t = map(join,t,(self.separator,) * rows)

        # Add final CRLF and store CSV text
        t.append('')
        self.text = self.text + join(t,self.lineend)

    def dumps(self):

        """ Returns the data as CSV text
        """
        return self.text

    def dump(self, file,

             StringType=types.StringType):

        """ Write the converted CSV data to a file
        """
        if type(file) == StringType:
            file = open(file,'wb')
            file.write(self.text)
            file.close()
        else:
            file.write(self.text)

    def _quote(self, line,

               replace=string.replace,str=str):

        """ CSV style quote the given line of text.
        """
        nline = ['""'] * len(line)
        for i,item in irange(line):
            if item is not None:
                text = str(item)
            else:
                text = ''
            nline[i] = '"%s"' % replace(text,'"','""')
        return nline

def _test():
    import sys
    global _debug

    # Turn on debugging output
    #_debug = 1

    s = """"key1","key2",key3,key4
"abc",0,,0,"def""ghi
Eine neue Zeile
0","hallo",
"line",with"errors,
"text with,embedded,commas",2,3,4
newline,new,luck,;123,""\015
\"""Quote""\",1,2,3,"""#"

    r = Reader()
    r.loads(s)
    lt = r.list()
    print lt
    print r.dictionary()
    r.set_columns(('Name','Vorname'))
    print r.dictionary()
    print r.description()
    print '-' * 72


    w = Writer()
    w.feed_list(r.list())
    w.feed_list(r.list())
    s = w.dumps()
    print s

    #w.dump('test.txt')
    w.flush()
    dict = r.dictionary()
    w.set_columns(dict.keys())
    w.feed_dict(dict)
    s = w.dumps()
    print '-->',s

    r.flush()
    r.loads(s)
    lt = r.list()
    print lt
    print r.dictionary()
    r.set_columns(('Name','Vorname'))
    print r.dictionary()
    print r.description()
    print '-' * 72

    class Obj:
        pass
    data = []
    for i in range(10):
        o = Obj()
        o.id = i
        o.str = str(i)
        data.append(o)
    w.flush()
    w.set_columns(('id', 'str'))
    w.feed_objects(data)
    w.feed_objects(data)
    s = w.dumps()
    print '-->',s
    r.flush()
    r.loads(s)
    lt = r.list()
    print lt
    print r.dictionary()
    r.set_columns(('id','str'))
    print r.dictionary()
    print r.description()
    print '-' * 72


    print
    print 'Read File:',sys.argv[1]
    r.flush()
    f = open(sys.argv[1])
    r.load(f)
    print r

if __name__ == '__main__':
    _test()
