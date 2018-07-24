# -*- coding: utf-8 -*-

try:
    import hashlib
    md5_constructor = hashlib.md5
    md5_hmac = md5_constructor
    sha_constructor = hashlib.sha1
    sha_hmac = sha_constructor
except ImportError:
    import md5
    md5_constructor = md5.new
    md5_hmac = md5
    import sha
    sha_constructor = sha.new
    sha_hmac = sha

import sys
import types
reload(sys)
sys.setdefaultencoding('utf8')

md5 = md5_constructor

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def params_filter(params):
    ks = params.keys()
    ks.sort()
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, 'utf-8')
        if k not in ('sign') and v != '':
            newparams[k] = smart_str(v, 'utf-8')
            prestr += '%s%s' % (k, newparams[k])
    # prestr = prestr[:-1]
    return newparams, prestr

def sort(mes):
    '''
    作用类似与java的treemap,
    取出key值,按照字母排序后将value拼接起来
    返回字符串
    '''
    _par = []

    keys=mes.keys()
    keys.sort()
    for v in keys:
        _par.append(str(mes[v]))
    sep=''
    message=sep.join(_par)
    return message












