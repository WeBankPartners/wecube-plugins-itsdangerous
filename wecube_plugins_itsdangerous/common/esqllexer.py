# coding=utf-8
"""
wecube_plugins_itsdangerous.common.esqllexer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供增强的sql lexer功能

"""
from sqlparse import engine
from sqlparse import filters
from sqlparse import formatter
from sqlparse import lexer
from sqlparse import sql as S, tokens as T
from sqlparse import tokens
from sqlparse.compat import text_type, file_types
from sqlparse.engine import grouping
from sqlparse.keywords import SQL_REGEX
from sqlparse.utils import consume


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
                yield pos, tokens.Error, char


class EStatementSplitter(engine.StatementSplitter):

    def process(self, stream):
        """Process the stream"""
        EOS_TTYPE = T.Whitespace, T.Comment.Single, T.Comment.Multiline
        C_TTYPE = T.Comment.Single, T.Comment.Multiline

        # Run over all stream tokens
        for params in stream:
            pos, ttype, value = params
            if self.consume_ws and ttype not in EOS_TTYPE:
                yield pos, S.Statement(self.tokens)
                self._reset()
            self.level += self._change_splitlevel(ttype, value)
            self.tokens.append(S.Token(ttype, value))
            if self.level <= 0 and ttype is T.Punctuation and value == ';':
                self.consume_ws = True
            elif ttype in C_TTYPE:
                self.consume_ws = True
        if self.tokens:
            yield pos + len(u''.join([t.value for t in self.tokens])), S.Statement(self.tokens)


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
            origin_stmt = str(stmt)
            if self._grouping:
                stmt = grouping.group(stmt)

            for filter_ in self.stmtprocess:
                filter_.process(stmt)

            for filter_ in self.postprocess:
                stmt = filter_.process(stmt)

            yield pos, stmt, origin_stmt


def splitf(sql, encoding=None):
    """
    Split & format *sql* into single statements.
    """
    # stack = EFilterStack()
    # return [(pos, text_type(stmt).strip()) for pos, stmt in stack.run(sql, encoding)]
    stack = EFilterStack()
    options = formatter.validate_options({'strip_comments':True, 'strip_whitespace':True})
    formatter.build_filter_stack(stack, options)
    stack.postprocess.append(filters.SerializerUnicode())
    # optimize for skipping empty and comment lines
    return [(pos, stmt, str(origin_stmt)) for pos, stmt, origin_stmt in stack.run(sql, encoding)]

