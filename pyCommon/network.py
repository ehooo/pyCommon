from urlparse import urlparse
import mimetypes
import mimetools
import httplib
import urllib
import logging

logger = logging.getLogger(__name__)


def encode_multipart_formdata(fields, files):
    '''
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
    '''
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = StringIO()
    for (key, value) in fields:
            L.write('--' + BOUNDARY)
            L.write(CRLF + 'Content-Disposition: form-data; name="%s"' % key)
            L.write(CRLF + CRLF + value + CRLF)
    for (key, filename, value) in files:
            content_type = mimetypes.guess_type(os.path.basename(filename))[0] or 'application/octet-stream'
            L.write('--' + BOUNDARY)
            L.write(CRLF + 'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.write(CRLF + 'Content-Type: %s' % content_type)
            L.write(CRLF + CRLF + value + CRLF)
    L.write('--' + BOUNDARY + '--' + CRLF + CRLF)
    L.seek(0)
    body = L.read()
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def url2parmas(url):
    real_url = url
    if not url.startswith('http'):
        real_url = "http://%s"%url
    purl = urlparse(url)
    host = purl.netloc
    port = None
    secure = False
    webpath = purl.path
    if purl.hostname:
        host = purl.hostname
    if purl.port:
        port = purl.port
    elif purl.scheme.startswith('https'):
        secure = True
    if not port:
        port = 80
        if secure:
            port = 443
    return (host, webpath, port, secure)


def header2dict(headers):
    ret = {}
    for (key, value) in headers:
        ret[key] = value
    return ret


class WGet():
    def __init__(self, url=None):
        self.save_file = None
        self._tmp_file = None
        self._encode = None
        self.web(url)

    def web(self, url):
        self.host = None
        self.webpath = '/'
        self.port = 80
        self.secure = False
        self.read_header = None
        self.read_status = None
        if url:
            (self.host, self.webpath, self.port, self.secure) = url2parmas(url)

    def upload(self, filepath, data={}, fields=[]):
        if not os.path.isfile(filepath):
            raise ValueError('File not found')
        raw_file = None
        with open(filepath, 'rb') as f:
            raw_file = f.read()
            f.close()
        data['name'] = os.path.basename(filepath)
        path = '%s?%s'%(webpath, urllib.urlencode(data))
        files = [('file', webpath, raw_file)]
        return self.post_multipart(fields, files)

    def __get_conn(self):
        if secure:
            return httplib.HTTPSConnection(self.host, self.port)
        return httplib.HTTPConnection(self.host, self.port)

    def post_multipart(self, fields, files):
        '''
            Post fields and files to an http host as multipart/form-data.
            fields is a sequence of (name, value) elements for regular form fields.
            files is a sequence of (name, filename, value) elements for data to be uploaded as files
            Return the server's response page.
        '''
        content_type, body = encode_multipart_formdata(fields, files)
        h = self.__get_conn()
        h.putrequest('POST', path)
        h.putheader('Content-Type', content_type)
        h.putheader('Content-Length', str(len(body)))
        h.endheaders()
        h.send(body)

        self.read_status, errmsg, headers = h.getreply()
        self.read_header = header2dict( headers )
        content = ""
        try:
            content = h.file.read()
        except:
            try:
                c = h.getfile().next()
                while c:
                    content += c
                    c = h.getfile().next()
            except StopIteration:
                pass
        if self.read_status != httplib.OK:
            logger.debug('Status code: %s'%(self.read_status))
            logger.debug('Headers code: %s'%(self.read_header))
        logger.debug('Response: %s'%(content))
        return content

    def postsave_encode(self):
        if self.save_file:
            tmp_file = open(self.save_file, 'r')
            content = tmp_file.read()
            tmp_file.close()
            content = content.decode(self._encode, errors='replace')
            tmp_file = open(self.save_file, 'w')
            tmp_file.write(content)
            tmp_file.close()

    def save_callback(self, content, part):
        if self.save_file:
            if content is None:
                if part is None:
                    self._tmp_file.close()
                elif 'content-type' in part:
                    self._encode = 'UTF-8'
                    pos = part['content-type'].find('charset=')
                    if pos>-1:
                        self._encode = part['content-type'][pos+len('charset='):]
                    self._tmp_file = open(self.save_file, 'w')
            else:
                self._tmp_file.write(content)

    def donwload(data={}, header={}, method='GET', block=1024, update_callback=None):
        conn = self.__get_conn()
        logger.debug('Conecting with: %s %s'%(self.host, self.webpath) )
        postdata = urllib.urlencode(data)
        logger.debug('%s to %s:%s%s post:%s header:%s'%(method, self.host, self.port, self.webpath, postdata, header))
        conn.request(method, self.webpath, postdata, header)
        response = conn.getresponse()
        self.read_header = header2dict( response.getheaders() )
        logger.debug('Headers code: %s'%self.read_header )
        self.read_status = response.status
        calling = hasattr(update_callback, '__call__')
        if calling and update_callback(None, self.read_header):
            return
        content = response.read(block)
        part = 0
        while content:
            part += 1
            if calling and update_callback(content, part):
                logger.debug("Download aborted by %s"%callback)
                break
            content = response.read(block)
        conn.close()
        if calling:
            update_callback(None, None)
        return content
