# coding=utf-8
"""
wecube_plugins_itsdangerous.common.reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供格式解析读取器

"""
import bisect
import io
import re

from wecube_plugins_itsdangerous.common import eshlex
from wecube_plugins_itsdangerous.common import esqllexer


def _guess_text_sql(text):
    rating = 0
    name_between_bracket_re = re.compile(r'\[[a-zA-Z_]\w*\]')
    name_between_backtick_re = re.compile(r'`[a-zA-Z_]\w*`')
    name_command_re = re.compile(r'(insert\s+into|update\s+.*\s+set|alter\s+table|create\s+table|select\s+.+\s+from|delete\s+from).+;', re.I)
    name_between_backtick_count = len(
        name_between_backtick_re.findall(text))
    name_between_bracket_count = len(
        name_between_bracket_re.findall(text))
    name_command_count = len(
        name_command_re.findall(text))
    # Same logic as above in the TSQL analysis
    dialect_name_count = name_between_backtick_count + name_between_bracket_count
    if dialect_name_count >= 1 and \
       name_between_backtick_count >= 2 * name_between_bracket_count:
        # Found at least twice as many `name` as [name].
        rating += 0.4
    elif name_between_backtick_count > name_between_bracket_count:
        rating += 0.2
    elif name_between_backtick_count > 0:
        rating += 0.1
    if name_command_count:
        rating += 0.2
    return rating


def _guess_text_shell(text):
    rating = 0
    name_begin_re = re.compile(r'^#!\s+/.*/(bash|zsh|sh|dash)')
    name_variable_re = re.compile(r'\${?[a-zA-Z_]\w*}?')
    name_command_re = re.compile(r'^(cd|cat|awk|ps|sed|find|echo|mkdir|ls) .*$', re.MULTILINE)
    if name_begin_re.search(text):
        rating = 1.0
    name_variable_count = len(
        name_variable_re.findall(text))
    name_command_count = len(
        name_command_re.findall(text))
    if name_variable_count:
        rating += 0.3
    if name_command_count:
        rating += 0.7
    return rating


def guess(text):
    rate_sql = _guess_text_sql(text)
    rate_shell = _guess_text_shell(text)
    if rate_shell >= rate_sql:
        return 'shell'
    if rate_sql > 0:
        return 'sql'
    return None


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

    def countlr(self, text, char='\n'):
        count_left = 0
        count_right = 0
        step = len(char)
        for i in range(0, len(text), step):
            if text[i:i + step] == char:
                count_left += 1
            else:
                break
        for i in range(len(text), 0 , 0 - step):
            if text[i - step:i] == char:
                count_right += 1
            else:
                break
        return count_left, count_right


class FullTextReader(Reader):

    def iter(self):
        instream = None
        if isinstance(self.content, str):
            instream = io.StringIO(self.content)
        else:
            instream = self.content
        text = instream.read()
        yield (1, 1 + text.count('\n')), [text]


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
            yield ((lineno, lineno), [l.strip('\r\n')])
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
                    yield ((lineno, lineno), tokens)
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
                yield ((lineno, lineno), tokens)


class SqlReader(Reader):

    def iter(self):
        instream = None
        if isinstance(self.content, str):
            instream = io.StringIO(self.content)
        else:
            instream = self.content
        content = instream.read()
        sqls = esqllexer.splitf(content)
        results = []
        lineno = 1
        # culculate index of \n
        newline_indexes = []
        newline_start = 0
        newline_end = len(content)
        while True:
            newline_start = content.find('\n', newline_start, newline_end) + 1
            if newline_start == 0:
                break
            else:
                newline_indexes.append(newline_start)
        for pos, sql, origin_sql in sqls:
            # lineno = self.content.count('\n', 0, pos) + 1 - sql.count('\n')
            # optimize for newline count
            lineno_end = bisect.bisect(newline_indexes, pos) + 1
            newline_count = origin_sql.count('\n')
            newline_left, newline_right = self.countlr(origin_sql)
            lineno = (lineno_end - newline_count + newline_left, lineno_end - newline_right)
            results.append((lineno, sql))
        for lineno, sql in results:
            line_s, line_o = lineno
            yield (line_s, line_o), [sql]
