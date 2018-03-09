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

        imageURL = action.props.get('image_url', '')
        imageData = self._getImageData(imageURL)

        filename = self.substitute(action.props.get('filename', ''))
        filename = now.strftime(filename)

        self._saveLocalFile(filename, imageData)

    #---------------------------------------------------------------------------
    def doFtpPutFile(self, action):
        now = datetime.datetime.now();

        imageURL = action.props.get('image_url', '')
        imageData = self._getImageData(imageURL)

        server = action.props.get('server', '')
        username = action.props.get('username', '')
        password = action.props.get('password', '')

        filename = self.substitute(action.props.get('filename', ''))
        filename = now.strftime(filename)

        self._putFtpFile(server, username, password, filename, imageData)

    #---------------------------------------------------------------------------
    def _saveLocalFile(self, filename, data):
        self.logger.debug(u'saving %d bytes to %s', len(data), filename)

        with open(filename, 'wb') as fh:
            fh.write(data)

    #---------------------------------------------------------------------------
    def _putFtpFile(self, server, username, password, path, data):
        ftp = ftplib.FTP()

        self.logger.debug(u'connecting to FTP server: %s', server)
        ftp.connect(server)
        ftp.login(username, password)

        self.logger.debug(u'saving %d bytes to %s', len(data), path)
        strbuf = StringIO.StringIO(data)
        ftp.storbinary('STOR ' + path, strbuf)

        self.logger.debug(u'closing FTP session')
        ftp.quit()

    #---------------------------------------------------------------------------
    def _getImageData(self, url):
        self.logger.debug(u'downloading image: %s', url)

        resp = urllib2.urlopen(url)
        self.logger.debug(u'HTTP: %d', resp.getcode())

        data = resp.read()
        self.logger.debug(u'downloaded %d bytes', len(data))

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
