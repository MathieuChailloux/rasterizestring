# -*- coding: utf-8 -*-

"""
/***************************************************************************
 RasterizeString
                                 A QGIS plugin
 This plugin extends gdal rasterize command to burn values from non-numeric field.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-03-28
        copyright            : (C) 2019 by Mathieu Chailloux
        email                : mathieu@chailloux.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Mathieu Chailloux'
__date__ = '2019-03-28'
__copyright__ = '(C) 2019 by Mathieu Chailloux'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .rasterize_string_provider import RasterizeStringProvider
from .rasterize_string_algorithm import RasterizeStringAlgorithm

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class RasterizeStringPlugin(object):

    def __init__(self,iface):
        self.provider = RasterizeStringProvider()
        self.iface = iface
        #self.alg = RasterizeStringAlgorithm()
        #self.name = "&Rasterize from string field"
        
    # def run(self):
        # alg = RasterizeStringAlgorithm()
        # alg.run()

    def initGui(self):
        #self.actionMain = QAction(QIcon(":/plugins/testplug/icon.png"),self.name,self.iface.mainWindow())
        #self.actionMain.triggered.connect(self.run)
        #self.iface.addPluginToRasterMenu("RasterizeString",self.actionMain)
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        #self.iface.removePluginMenu("RasterizeString", self.actionMain)
        QgsApplication.processingRegistry().removeProvider(self.provider)
