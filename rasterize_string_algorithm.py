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

import processing

from PyQt5.QtCore import QCoreApplication
# from qgis.core import (QgsProcessing,
                       # QgsFeatureSink,
                       # QgsProcessingAlgorithm,
                       # QgsProcessingParameterFeatureSource,
                       # QgsProcessingParameterFeatureSink)

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsRasterFileWriter,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination)


class RasterizeStringAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    BURN = 'BURN'
    WIDTH = 'WIDTH'
    HEIGHT = 'HEIGHT'
    UNITS = 'UNITS'
    NODATA = 'NODATA'
    EXTENT = 'EXTENT'
    INIT = 'INIT'
    INVERT = 'INVERT'
    ALL_TOUCH = 'ALL_TOUCH'
    OPTIONS = 'OPTIONS'
    DATA_TYPE = 'DATA_TYPE'
    OUTPUT = 'OUTPUT'
    
    TYPES = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']
    def initAlgorithm(self, config=None):
        self.units = [self.tr("Pixels"),
                      self.tr("Georeferenced units")]

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterField(self.FIELD,
                                                      self.tr('Field to use for a burn-in value'),
                                                      None,
                                                      self.INPUT,
                                                      QgsProcessingParameterField.Any,
                                                      optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.BURN,
                                                       self.tr('A fixed value to burn'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=0.0,
                                                       optional=True))
        self.addParameter(QgsProcessingParameterEnum(self.UNITS,
                                                     self.tr('Output raster size units'),
                                                     self.units))
        self.addParameter(QgsProcessingParameterNumber(self.WIDTH,
                                                       self.tr('Width/Horizontal resolution'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       minValue=0.0,
                                                       defaultValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(self.HEIGHT,
                                                       self.tr('Height/Vertical resolution'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       minValue=0.0,
                                                       defaultValue=0.0))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT,
                                                       self.tr('Output extent')))
        self.addParameter(QgsProcessingParameterNumber(self.NODATA,
                                                       self.tr('Assign a specified nodata value to output bands'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=0.0,
                                                       optional=True))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation options'),
                                                     defaultValue='',
                                                     optional=True)
        options_param.setFlags(options_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        options_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.algs.gdal.ui.RasterOptionsWidget.RasterOptionsWidgetWrapper'}})
        self.addParameter(options_param)

        dataType_param = QgsProcessingParameterEnum(self.DATA_TYPE,
                                                    self.tr('Output data type'),
                                                    self.TYPES,
                                                    allowMultiple=False,
                                                    defaultValue=5)
        dataType_param.setFlags(dataType_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(dataType_param)

        init_param = QgsProcessingParameterNumber(self.INIT,
                                                  self.tr('Pre-initialize the output image with value'),
                                                  type=QgsProcessingParameterNumber.Double,
                                                  defaultValue=0.0,
                                                  optional=True)
        init_param.setFlags(init_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(init_param)

        invert_param = QgsProcessingParameterBoolean(self.INVERT,
                                                     self.tr('Invert rasterization'),
                                                     defaultValue=False)
        invert_param.setFlags(invert_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(invert_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Rasterized')))

    def getUniqueValues(self,layer,fieldname):
        res = set()
        for f in layer.getFeatures():
            res.add(f[fieldname])
        return res
        
    def processAlgorithm(self, parameters, context, feedback):
        # Dummy function to enable running an alg inside an alg
        def no_post_process(alg, context, feedback):
            pass
            
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        fieldname = self.parameterAsString(parameters,self.FIELD,context)
        
        vals = self.getUniqueValues(input,fieldname)
        feedback.pushDebugInfo(str(vals))
        
        res = processing.run("gdal:rasterize",parameters,onFinish=no_post_process,context=context,feedback=feedback)
        
        return res

    def name(self):
        return 'rasterizestring'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Conversion'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RasterizeStringAlgorithm()