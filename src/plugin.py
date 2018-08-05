#!/usr/bin/env python2.5

import urllib2
import datetime
import ftplib
import StringIO

import iplug

################################################################################
class Plugin(iplug.PluginBase):

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, deviceId):
        errors = indigo.Dict()

        iplug.validateConfig_URL('image_url', values, errors)
        iplug.validateConfig_String('username', values, errors, True)
        iplug.validateConfig_String('password', values, errors, True)

        if (typeId == 'save_file'):
            iplug.validateConfig_Path('filename', values, errors)
        elif (typeId == 'ftp_put'):
            iplug.validateConfig_Hostname('server', values, errors)
            iplug.validateConfig_Path('filename', values, errors)

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def doSaveLocalFile(self, action):
        now = datetime.datetime.now()
        imageData = self._downloadImageFromAction(action)

        if (imageData is None):
            return False

        userValue = action.props.get('filename', '')
        filename = self.substitute(userValue)
        filename = now.strftime(filename)

        self._saveLocalFile(filename, imageData)

        return True

    #---------------------------------------------------------------------------
    def doFtpPutFile(self, action):
        now = datetime.datetime.now()
        imageData = self._downloadImageFromAction(action)

        if (imageData is None):
            return False

        server = action.props.get('server', '')
        username = action.props.get('username', '')
        password = action.props.get('password', '')

        userValue = action.props.get('filename', '')
        filename = self.substitute(userValue)
        filename = now.strftime(filename)

        return self._putFtpFile(server, username, password, filename, imageData)

    #---------------------------------------------------------------------------
    def _saveLocalFile(self, filename, data):
        self.logger.debug(u'saving %d bytes to %s', len(data), filename)

        with open(filename, 'wb') as fh:
            fh.write(data)

    #---------------------------------------------------------------------------
    def _putFtpFile(self, server, username, password, path, data):
        ftp = ftplib.FTP()

        uploaded = False

        try:
            self.logger.debug(u'connecting to FTP server: %s', server)
            ftp.connect(server)

            self.logger.debug(u'initiating FTP login: %s', username)
            ftp.login(username, password)

            self.logger.debug(u'saving %d bytes to %s', len(data), path)
            strbuf = StringIO.StringIO(data)
            ftp.storbinary('STOR ' + path, strbuf)

            # if we make it this far, the file was uploaded
            uploaded = True

            self.logger.debug(u'closing FTP session')
            ftp.quit()

        except EOFError:
            self.logger.warn(u'FTP session closed by server')

        except ftplib.error_perm as err:
            self.logger.warn(u'FTP error: %s', err)

        return uploaded

    #---------------------------------------------------------------------------
    def _downloadImageFromAction(self, action):
        auth = action.props.get('auth', None)
        url = action.props.get('image_url', '')

        if ((auth is None) or (auth == 'none')):
            self.logger.debug(u'no auth handler configured')

        elif (auth == 'basic'):
            uname = action.props.get('username', None)
            passwd = action.props.get('password', None)

            self.logger.debug(u'configuring for basic auth - %s', uname)
            self._configureBasicAuth(url, uname, passwd)

        else:
            self.logger.warn(u'unknown authentication method - %s', auth)

        return self._getImageData(url)

    #---------------------------------------------------------------------------
    def _configureBasicAuth(self, url, user, passwd):
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, url, user, passwd)

        hdlr = urllib2.HTTPBasicAuthHandler(passmgr)
        opener = urllib2.build_opener(hdlr)

        urllib2.install_opener(opener)

    #---------------------------------------------------------------------------
    def _getImageData(self, url):
        self.logger.debug(u'downloading image: %s', url)

        data = None

        try:
            resp = urllib2.urlopen(url)
            self.logger.debug(u'HTTP: %d', resp.getcode())

            data = resp.read()
            self.logger.debug(u'downloaded %d bytes', len(data))

        except urllib2.HTTPError as err:
            self.logger.warn(u'HTTP Error: %s', err.reason)

        return data

