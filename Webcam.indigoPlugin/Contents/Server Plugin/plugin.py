#!/usr/bin/env python2.5

import urllib2
import datetime
import ftplib
import StringIO

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self._loadPluginPrefs(pluginPrefs)

    #---------------------------------------------------------------------------
    def __del__(self):
        indigo.PluginBase.__del__(self)

    #---------------------------------------------------------------------------
    def validatePrefsConfigUi(self, values):
        errors = indigo.Dict()

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def closedPrefsConfigUi(self, values, canceled):
        if canceled: return
        self._loadPluginPrefs(values)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def doSaveLocalFile(self, action):
        now = datetime.datetime.now();
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
        now = datetime.datetime.now();
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

    #---------------------------------------------------------------------------
    def _loadPluginPrefs(self, values):
        logLevelTxt = values.get('logLevel', None)

        if logLevelTxt is None:
            self.logLevel = 20
        else:
            logLevel = int(logLevelTxt)
            self.logLevel = logLevel

        self.indigo_log_handler.setLevel(self.logLevel)

