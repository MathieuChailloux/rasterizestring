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

from .generate_integer_field_algorithm import GenerateIntegerFieldCreationAlgorithm

from PyQt5.QtCore import QCoreApplication
# from qgis.core import (QgsProcessing,
                       # QgsFeatureSink,
                       # QgsProcessingAlgorithm,
                       # QgsProcessingParameterFeatureSource,
                       # QgsProcessingParameterFeatureSink)

from qgis.core import (QgsProject,
                       QgsVectorLayer,
                       QgsProcessing,
                       QgsProcessingUtils,
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

        # dataType_param = QgsProcessingParameterEnum(self.DATA_TYPE,
                                                    # self.tr('Output data type'),
                                                    # self.TYPES,
                                                    # allowMultiple=False,
                                                    # defaultValue=5)
        # dataType_param.setFlags(dataType_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        # self.addParameter(dataType_param)

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
        
        all_touch_param = QgsProcessingParameterBoolean(self.ALL_TOUCH,
                                                     self.tr('ALL_TOUCHED mode'),
                                                     defaultValue=False)
        all_touch_param.setFlags(all_touch_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(all_touch_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Rasterized')))

    def getUniqueValues(self,layer,fieldname):
        res = set()
        for f in layer.getFeatures():
            res.add(f[fieldname])
        return res
        
    def getSmallestType(self,max_val):
        assert(max_val >= 0)
        if max_val < 256:
            return 'Byte'
        elif max_val < pow(2,16):
            return 'UInt16'
        elif max_val < pow(2,32):
            return 'UInt32'
        else:
            return 'Float32'
        
    def processAlgorithm(self, parameters, context, feedback):
        # Dummy function to enable running an alg inside an alg
        def no_post_process(alg, context, feedback):
            pass
            
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        fieldname = self.parameterAsString(parameters,self.FIELD,context)
        
        alg_parameters = { GenerateIntegerFieldCreationAlgorithm.INPUT : input,
                           GenerateIntegerFieldCreationAlgorithm.INPUT_FIELD : fieldname,
                           GenerateIntegerFieldCreationAlgorithm.OUTPUT : 'memory:' }
        res_new = processing.run("RasterizeString:generateIntegerFieldCreation",alg_parameters,
                                 onFinish=no_post_process,context=context,feedback=feedback)
        new_layer_id = res_new[GenerateIntegerFieldCreationAlgorithm.OUTPUT]
        assoc = res_new[GenerateIntegerFieldCreationAlgorithm.OUTPUT_ASSOC]
        
        max_val = len(assoc)
        data_type = self.TYPES.index(self.getSmallestType(max_val))
        parameters[self.DATA_TYPE] = data_type
        parameters['INPUT'] = new_layer_id
        parameters['FIELD'] = GenerateIntegerFieldCreationAlgorithm.OUTPUT_FIELD_DEFAULT
        feedback.pushDebugInfo("New parameters : " + str(parameters))
        
        res = processing.run("gdal:rasterize",parameters,onFinish=no_post_process,context=context,feedback=feedback)
        
        return res

    def name(self):
        return 'rasterizestring'

    def displayName(self):
        return self.tr('Rasterize string field')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return None#'Conversion'
        
    def shortHelpString(self):
        return self.tr("Conversion from vector to raster. This algorithm is a wrapper of gdal rasterize that allows to specify a non-numeric field.\nOutput raster values are automatically generated according to input field values. A temporary integer field is created and a new integer value is associated to each input unique value (from 1 to N with N = number of unique values). Such association is loaded is CSV file 'Association.csv'.\nOutput data type is chosen according to data range (unsigned integer type of minimal range, e.g. Byte, UInt16 or UInt32).")

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RasterizeStringAlgorithm()
