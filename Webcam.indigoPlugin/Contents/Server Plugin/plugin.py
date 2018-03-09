#!/usr/bin/env python2.5

import urllib2
import datetime

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

        image_url = action.props.get('image_url', '')
        image_data = self._getImage(image_url)

        filename = self.substitute(action.props.get('filename', ''))
        filename = now.strftime(filename)

        self._saveLocalFile(filename, image_data)

    #---------------------------------------------------------------------------
    def doFtpPutFile(self, action):
        now = datetime.datetime.now();

        image_url = action.props.get('image_url', '')
        local_file = self._getImage(image_url)

    #---------------------------------------------------------------------------
    def _saveLocalFile(self, filename, data):
        self.logger.debug(u'saving %d bytes to %s', len(data), filename)

        fh = open(filename, 'w')
        fh.write(data)
        fh.close()

    #---------------------------------------------------------------------------
    def _getImage(self, url):
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

