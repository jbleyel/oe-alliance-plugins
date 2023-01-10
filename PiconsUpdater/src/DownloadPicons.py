# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from _collections import deque
from . import _, printToConsole, getPiconsPath, getTmpLocalPicon, PICON_TYPE_NAME, PICON_TYPE_KEY
from .DownloadJob import DownloadJob
from .EventDispatcher import dispatchEvent
from .DiskUtils import getCleanFileName
from .BouquetParser import getChannelKey
DOWNLOAD_ALL_FINISHED = 'downloadAllFinished'
DOWNLOAD_FINISHED = 'downloadFinished'
CONCURRENT_DOWNLOADS = 5


class DownloadPicons:

    def __init__(self, serviceList, piconsUrl, targetPath, piconNameType):
        self.serviceList = serviceList
        self.piconsUrl = piconsUrl
        self.targetPath = targetPath
        self.piconNameType = piconNameType
        self.downloadsFinished = 0
        self.downloadsFailed = 0
        self.totalDownloads = 0
        self.channelsNotFoundList = []
        self.downloadPicons()

    def abortDownload(self):
        printToConsole('abortDownload')
        self.queueDownloadList = deque()

    def downloadPicons(self):
        for i in ['4097', '5001', '5002', '5003']:  # essential remove of obstructive Picon-filenames
            obstructive = getTmpLocalPicon('%s_0_1_0_0_0_0_0_0_0' % i)
            if os.path.isfile(obstructive):
                os.remove(obstructive)
            obstructive = getPiconsPath().getValue() + '/%s_0_1_0_0_0_0_0_0_0.png' % i
            if os.path.isfile(obstructive):
                os.remove(obstructive)
        self.queueDownloadList = deque()
        printToConsole('Picons to download: %d' % len(self.serviceList))
        for service in self.serviceList:
            channelKey = getChannelKey(service)
            if self.piconNameType is PICON_TYPE_NAME:
                piconName = getCleanFileName(service.getServiceName())
            else:
                piconName = channelKey
            if any(channelKey.find(i) + 1 for i in ['4097', '5001', '5002', '5003']):  # Internetstream found, therefore use SNP:
                channelKey = piconName.replace('-', '')
            if not piconName:
                continue
            urlPng = self.piconsUrl % piconName
            self.queueDownloadList.append((str(urlPng), str(self.targetPath + '/' + channelKey + '.png')))

        self.totalDownloads = len(self.queueDownloadList)
        if self.totalDownloads > CONCURRENT_DOWNLOADS:
            concurrentDownloads = CONCURRENT_DOWNLOADS
        else:
            concurrentDownloads = self.totalDownloads
        for i in range(concurrentDownloads):
            self.executeDownloadQueue()

    def executeDownloadQueue(self):
        # print('executeDownloadQueue:' + str(len(self.queueDownloadList)) + 'FIN:' + str(self.downloadsFinished) + ' FAILED:' + str(self.downloadsFailed) + 'Total :' + str(self.totalDownloads))
        if len(self.queueDownloadList) == 0 and self.downloadsFinished + self.downloadsFailed == self.totalDownloads:
            printToConsole('downloadsFinished: ' + str(self.downloadsFinished))
            printToConsole('downloadsFailed: ' + str(self.downloadsFailed))
            printToConsole('totalDownloads: ' + str(self.totalDownloads))
            printToConsole('picons not found: ' + str(self.channelsNotFoundList))
            dispatchEvent(DOWNLOAD_ALL_FINISHED, self)
        elif len(self.queueDownloadList) > 0:
            download = self.queueDownloadList.popleft()
            DownloadJob(download[0], download[1], self.__downloadFinished, self.__downloadFailed)

    def addChannelToNoFoundList(self, channel, url):
        self.channelsNotFoundList.append((channel, url))

    def __downloadFinished(self, downloadJob):
        self.downloadsFinished += 1
        printToConsole("downloadFinished '%s'" % downloadJob.downloadUrl)
        self.dispatchDownloadFinished()
        self.executeDownloadQueue()

    def __downloadFailed(self, downloadJob):
        self.downloadsFailed += 1
        self.addChannelToNoFoundList(downloadJob.targetFileName, downloadJob.downloadUrl)
        printToConsole("[Download Error] '%s'" % downloadJob.errorMessage)
        self.dispatchDownloadFinished()
        self.executeDownloadQueue()

    def dispatchDownloadFinished(self):
        dispatchEvent(DOWNLOAD_FINISHED, self.downloadsFinished + self.downloadsFailed)
