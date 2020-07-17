# coding=utf-8
"""
wecube_plugins_itsdangerous.common.reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供格式解析读取器

"""
import io

import sqlparse

from wecube_plugins_itsdangerous.common import eshlex
from wecube_plugins_itsdangerous.common import esqllexer


class Reader(object):
    def __init__(self, content):
        '''
        init a reader
        :param content: file-like or str
        '''
        self.content = content
        
    def iter(self):
        # iterable: (lineno, contents)
        pass
    
    
class FullTextReader(Reader):        

    def iter(self):
        instream = None
        if isinstance(self.content, str):
            instream = io.StringIO(self.content)
        else:
            instream = self.content
        text = instream.read()
        yield 1, [text]


class LineReader(Reader):        
    def iter(self):
        instream = None
        if isinstance(self.content, str):
            instream = io.StringIO(self.content)
        else:
            instream = self.content
        lineno = 1
        l = instream.readline()
        while l:
            yield (lineno, [l.strip('\r\n')])
            l = instream.readline()
            lineno += 1
    

class ShellReader(Reader):
    def __init__(self, content):
        Reader.__init__(self, content)
        self.special_punctuation = ['|', '||', '&&', ';']
        
    def iter(self):
        ret = eshlex.EShlex(self.content, posix=True, punctuation_chars=True)
        # we want $ or chinese charatars be together
        ret.whitespace_split = True
        tokens = []
        lineno, token, is_punctuation = ret.read_token_ex()
        new_lineno = lineno
        while token:
            if is_punctuation and token in self.special_punctuation:
                if tokens:
                    yield (lineno, tokens)
                tokens = []
            else:
                if new_lineno != lineno:
                    if tokens:
                        yield (lineno, tokens)
                    tokens = []
                    lineno = new_lineno
                    tokens.append(token)
                else:
                    tokens.append(token)
            new_lineno, token, is_punctuation = ret.read_token_ex()
            if not token and tokens:
                yield (lineno, tokens)


class SqlReader(Reader):
        
    def iter(self):
        instream = None
        if isinstance(self.content, str):
            instream = io.StringIO(self.content)
        else:
            instream = self.content
        content = instream.read()
        sqls = esqllexer.split(content)
        results = []
        for pos,sql in sqls:
            lineno = self.content.count('\n', 0, pos) + 1
            lineno -= sql.count('\n')
            results.append((lineno, sqlparse.format(sql, strip_comments=True, strip_whitespace=True)))
        for lineno, sql in results:
            yield lineno, [sql]
        
