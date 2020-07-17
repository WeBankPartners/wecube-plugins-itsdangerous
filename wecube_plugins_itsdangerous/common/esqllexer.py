# coding=utf-8
"""
wecube_plugins_itsdangerous.common.esqllexer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供增强的sql lexer功能

"""
from sqlparse import engine
from sqlparse import lexer
from sqlparse import tokens
from sqlparse import sql, tokens as T
from sqlparse.keywords import SQL_REGEX
from sqlparse.compat import text_type, file_types
from sqlparse.utils import consume
from sqlparse.engine import grouping


class ELexer(lexer.Lexer):
    @staticmethod
    def get_tokens(text, encoding=None):
        if isinstance(text, file_types):
            text = text.read()

        if isinstance(text, text_type):
            pass
        elif isinstance(text, bytes):
            if encoding:
                text = text.decode(encoding)
            else:
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    text = text.decode('unicode-escape')
        else:
            raise TypeError(u"Expected text or file-like object, got {!r}".
                            format(type(text)))

        iterable = enumerate(text)
        for pos, char in iterable:
            for rexmatch, action in SQL_REGEX:
                m = rexmatch(text, pos)
                if not m:
                    continue
                elif isinstance(action, tokens._TokenType):
                    yield pos, action, m.group()
                elif callable(action):
                    action_new, new_group = action(m.group())
                    yield pos, action_new, new_group

                consume(iterable, m.end() - pos - 1)
                break
            else:
                yield 1, tokens.Error, char


class EStatementSplitter(engine.StatementSplitter):
    def process(self, stream):
        """Process the stream"""
        EOS_TTYPE = T.Whitespace, T.Comment.Single, T.Comment.Multiline
        C_TTYPE = T.Comment.Single, T.Comment.Multiline
        
        # Run over all stream tokens
        for params in stream:
            pos, ttype, value = params
            if self.consume_ws and ttype not in EOS_TTYPE:
                yield pos, sql.Statement(self.tokens)
                self._reset()
            self.level += self._change_splitlevel(ttype, value) 
            self.tokens.append(sql.Token(ttype, value))
            if self.level <= 0 and ttype is T.Punctuation and value == ';':
                self.consume_ws = True
            elif ttype in C_TTYPE:
                self.consume_ws = True
        if self.tokens:
            yield pos, sql.Statement(self.tokens)



class EFilterStack(engine.FilterStack):
    def run(self, sql, encoding=None):
        stream = ELexer().get_tokens(sql, encoding)
        # Process token stream
        for filter_ in self.preprocess:
            stream = filter_.process(stream)

        splitter = EStatementSplitter()
        stream = splitter.process(stream)

        # Output: Stream processed Statements
        for params in stream:
            pos, stmt = params
            if self._grouping:
                stmt = grouping.group(stmt)

            for filter_ in self.stmtprocess:
                filter_.process(stmt)

            for filter_ in self.postprocess:
                stmt = filter_.process(stmt)

            yield pos,stmt
            

def split(sql, encoding=None):
    """Split *sql* into single statements.

    :param sql: A string containing one or more SQL statements.
    :param encoding: The encoding of the statement (optional).
    :returns: A list of strings.
    """
    stack = EFilterStack()
    return [(pos,text_type(stmt).strip()) for pos,stmt in stack.run(sql, encoding)]
