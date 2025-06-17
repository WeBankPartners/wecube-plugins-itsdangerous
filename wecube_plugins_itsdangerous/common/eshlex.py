# coding=utf-8
"""
wecube_plugins_itsdangerous.common.eshlex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供增强的shlex功能

"""
import shlex


class EShlex(shlex.shlex):
    def __init__(self, instream=None, infile=None, posix=False, punctuation_chars=False):
        super(EShlex, self).__init__(instream=instream, infile=infile, posix=posix, punctuation_chars=punctuation_chars)
        self.commentstate = False

    def read_token_ex(self):
        '''
        return extra lineno + token 
        '''
        quoted = False
        escapedstate = ' '
        token_line = self.lineno
        is_punctuation = False
        line_continue = False
        while True:
            if self.punctuation_chars and self._pushback_chars:
                nextchar = self._pushback_chars.pop()
            else:
                nextchar = self.instream.read(1)
                if nextchar == '':
                    return token_line, None, is_punctuation, line_continue
            if nextchar == '\n':
                self.lineno += 1
            if self.debug >= 3:
                print("shlex: in state %r I see character: %r" % (self.state, nextchar))
            if self.state is None:
                self.token = ''  # past end of file
                break
            elif self.state == ' ':
                if not nextchar:
                    self.state = None  # end of file
                    break
                elif nextchar in self.whitespace:
                    if self.debug >= 2:
                        print("shlex: I see whitespace in whitespace state")
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    elif nextchar == '\n':
                        is_punctuation = True
                        self.token = '\n'
                        break
                    else:
                        continue
                elif nextchar in self.commenters:
                    self.commentstate = True
                    break
                elif self.commentstate:
                    self.instream.readline()
                    self.lineno += 1
                    token_line = self.lineno
                    self.commentstate = False
                elif self.posix and nextchar in self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                elif nextchar in self.wordchars:
                    self.token = nextchar
                    self.state = 'a'
                elif nextchar in self.punctuation_chars:
                    self.token = nextchar
                    self.state = 'c'
                elif nextchar in self.quotes:
                    if not self.posix:
                        self.token = nextchar
                    self.state = nextchar
                elif self.whitespace_split:
                    self.token = nextchar
                    self.state = 'a'
                else:
                    self.token = nextchar
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
            elif self.state in self.quotes:
                quoted = True
                if not nextchar:  # end of file
                    if self.debug >= 2:
                        print("shlex: I see EOF in quotes state")
                    # XXX what error should be raised here?
                    raise ValueError("No closing quotation")
                if nextchar == self.state:
                    if not self.posix:
                        self.token += nextchar
                        self.state = ' '
                        break
                    else:
                        self.state = 'a'
                elif (self.posix and nextchar in self.escape and self.state in self.escapedquotes):
                    escapedstate = self.state
                    self.state = nextchar
                else:
                    self.token += nextchar
            elif self.state in self.escape:
                if not nextchar:  # end of file
                    if self.debug >= 2:
                        print("shlex: I see EOF in escape state")
                    # XXX what error should be raised here?
                    raise ValueError("No escaped character")
                # In posix shells, only the quote itself or the escape
                # character may be escaped within quotes.
                if (escapedstate in self.quotes and nextchar != self.state and nextchar != escapedstate):
                    self.token += self.state
                if not (escapedstate == 'a' and nextchar == '\n'):
                    # escape with newline mean the same line
                    self.token += nextchar
                    self.state = escapedstate
                if escapedstate == 'a' and nextchar == '\n':
                    line_continue = True
                    token_line = self.lineno
                    self.state = ' '
            elif self.state in ('a', 'c'):
                if not nextchar:
                    self.state = None  # end of file
                    break
                elif nextchar in self.whitespace:
                    if self.debug >= 2:
                        print("shlex: I see whitespace in word state")
                    self.state = ' '
                    if self.token or (self.posix and quoted):
                        if not quoted and self.token in self.punctuation_chars:
                            is_punctuation = True
                        break  # emit current token
                    else:
                        continue
                elif nextchar in self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                    token_line = self.lineno
                    if self.posix:
                        self.state = ' '
                        if self.token or (self.posix and quoted):
                            break  # emit current token
                        else:
                            continue
                elif self.state == 'c':
                    if nextchar in self.punctuation_chars:
                        self.token += nextchar
                        is_punctuation = True
                    else:
                        if nextchar not in self.whitespace:
                            self._pushback_chars.append(nextchar)
                        is_punctuation = True
                        self.state = ' '
                        break
                elif self.posix and nextchar in self.quotes:
                    self.state = nextchar
                elif self.posix and nextchar in self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                elif (nextchar in self.wordchars or nextchar in self.quotes
                      or (self.whitespace_split and nextchar not in self.punctuation_chars)):
                    self.token += nextchar
                else:
                    if self.punctuation_chars:
                        self._pushback_chars.append(nextchar)
                    else:
                        self.pushback.appendleft(nextchar)
                    if self.debug >= 2:
                        print("shlex: I see punctuation in word state")
                    self.state = ' '
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
        result = self.token
        self.token = ''
        if self.posix and not quoted and result == '' and not self.commentstate:
            result = None
        if self.debug > 1:
            if result:
                print("shlex: raw token=" + repr(result))
            else:
                print("shlex: raw token=EOF")
        return token_line, result, is_punctuation, line_continue
