# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GenerateIntegerField
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

import os, csv

import processing

from PyQt5.QtCore import QCoreApplication, QVariant
# from qgis.core import (QgsProcessing,
                       # QgsFeatureSink,
                       # QgsProcessingAlgorithm,
                       # QgsProcessingParameterFeatureSource,
                       # QgsProcessingParameterFeatureSink)

from qgis.core import (QgsVectorLayer,
                       QgsProject,
                       QgsProcessing,
                       QgsProcessingUtils,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRange,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsFeatureSink)


class GenerateIntegerFieldEditAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    INPUT_FIELD = 'FIELD'
    
    OUTPUT_FIELD = 'OUTPUT_FIELD'
    OUTPUT_ASSOC = 'OUTPUT_ASSOC'
    
    OUTPUT_FIELD_DEFAULT = 'INT_FIELD'
    
    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterField(self.INPUT_FIELD,
                                                      self.tr('Input field'),
                                                      None,
                                                      self.INPUT,
                                                      QgsProcessingParameterField.Any))

        self.addParameter(QgsProcessingParameterString(self.OUTPUT_FIELD,
                                                       self.tr('Additional creation options'),
                                                       defaultValue=self.OUTPUT_FIELD_DEFAULT,
                                                       optional=True))
        
    def processAlgorithm(self, parameters, context, feedback):
        # Dummy function to enable running an alg inside an alg
        def no_post_process(alg, context, feedback):
            pass
            
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        in_fieldname = self.parameterAsString(parameters,self.INPUT_FIELD,context)
        out_fieldname = self.parameterAsString(parameters,self.OUTPUT_FIELD,context)
        if out_fieldname in input.fields().names():
            raise QgsProcessingException("Output field '" + str(out_fieldname) + "' already exists")
        
        out_field = QgsField(out_fieldname,QVariant.Int)
        input_provider = input.dataProvider()
        input_provider.addAttributes([out_field])
        input.updateFields()
        feedback.pushInfo("input layer fields : " + str(input.fields().names()))
        
        in_field_idx = input_provider.fieldNameIndex(in_fieldname)
        unique_vals = sorted(input.uniqueValues(in_field_idx))
        feedback.pushDebugInfo("unique_vals " + str(unique_vals))
        assoc = {}
        for idx, v in enumerate(unique_vals):
            assoc[v] = idx + 1
        
        input.startEditing()
        for f in input.getFeatures():
            in_val = f[in_fieldname]
            f[out_fieldname] = assoc[in_val]
            input.updateFeature(f)
        input.commitChanges()
        
        return None

    def name(self):
        return 'generateIntegerFieldEdit'

    def displayName(self):
        return self.tr('Create integer field (layer edition)')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Aux'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GenerateIntegerFieldEditAlgorithm()
        


class GenerateIntegerFieldCreationAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    INPUT_FIELD = 'FIELD'
    RANGE = 'RANGE'
    
    OUTPUT_FIELD = 'OUTPUT_FIELD'
    OUTPUT_ASSOC = 'OUTPUT_ASSOC'
    OUTPUT = 'OUTPUT'
    
    OUTPUT_FIELD_DEFAULT = 'INT_FIELD'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer')))
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_FIELD,
                self.tr('Input field'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.String))
        self.addParameter(
            QgsProcessingParameterRange(self.RANGE,
                description=self.tr('Index range'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=[0.0,9999.0],
                optional=True))

        self.addParameter(
            QgsProcessingParameterString(
                self.OUTPUT_FIELD,
               self.tr('Output index field name'),
               defaultValue=self.OUTPUT_FIELD_DEFAULT))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer")))
        
    def processAlgorithm(self, parameters, context, feedback):
        # Dummy function to enable running an alg inside an alg
        def no_post_process(alg, context, feedback):
            pass
            
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        in_fieldname = self.parameterAsString(parameters,self.INPUT_FIELD,context)
        out_fieldname = self.parameterAsString(parameters,self.OUTPUT_FIELD,context)
        if out_fieldname in input.fields().names():
            raise QgsProcessingException("Output field '" + str(out_fieldname) + "' already exists")
        
        output_fields = QgsFields(input.fields())
        out_field = QgsField(out_fieldname,QVariant.Int)
        output_fields.append(out_field)
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            output_fields,
            input.wkbType(),
            input.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        input_provider = input.dataProvider()
        in_field_idx = input_provider.fieldNameIndex(in_fieldname)
        unique_vals = sorted(input.uniqueValues(in_field_idx))
        feedback.pushDebugInfo("unique_vals: " + str(unique_vals))
        nb_vals = len(unique_vals)
        feedback.pushDebugInfo("nb_vals = " + str(nb_vals))
        
        index_range = self.parameterAsRange(parameters,self.RANGE,context)
        if index_range:
            feedback.pushDebugInfo("index_range = " + str(index_range))
            if len(index_range) != 2:
                raise QgsProcessingException("Ill-formed index range: " + str(index_range) + "")
            min_idx, max_idx = int(index_range[0]), int(index_range[1])
            feedback.pushDebugInfo("min = " + str(min_idx))
            feedback.pushDebugInfo("max = " + str(max_idx))
            if min_idx < 0 or max_idx < 0:
                raise QgsProcessingException("Index range bounds must be positive")
            len_range = max_idx - min_idx + 1
        else:
            min_idx, max_idx, len_range = 0, nb_vals, nb_vals
        feedback.pushDebugInfo("len_range = " + str(len_range))
        if len_range < nb_vals:
            raise QgsProcessingException("Range " + str(index_range) + " is too small to store "
                                         + str(nb_vals) + " unique values")
        
        assoc = {}
        for idx, v in enumerate(unique_vals):
            assoc[v] = min_idx + idx
        #feedback.pushDebugInfo("Assoc : " + str(assoc))
        input_fields = input.fields().names()
        for f in input.getFeatures():
            in_val = f[in_fieldname]
            new_f = QgsFeature(output_fields)
            for in_field in input_fields:
                new_f[in_field] = f[in_field]
            new_f[out_fieldname] = assoc[in_val]
            new_f.setGeometry(f.geometry())
            sink.addFeature(new_f)
            
        csv_file = QgsProcessingUtils.generateTempFilename('Association.csv')
        csvt_file = csv_file + "t"
        feedback.pushDebugInfo("CSV file : " +str(csv_file))
        feedback.pushDebugInfo("CSVT file : " +str(csvt_file))
        
        col1, col2 = ('new integer field','old value')
        with open(csv_file,'w+') as f:
            fieldnames = [col1,col2]
            writer = csv.DictWriter(f,fieldnames=fieldnames)
            writer.writeheader()
            for k, v in assoc.items():
                row = { col1 : v, col2 : str(k) }
                writer.writerow(row)
                
        with open(csvt_file,'w+') as ft:
            ft.write("Integer,String")
            
        csv_layer = QgsVectorLayer(csv_file,"Association","ogr")
        if csv_layer is None:
            raise QgsProcessingException("INVALID NONE")
        if not csv_layer.isValid():
            raise QgsProcessingException("INVALID")
        QgsProject.instance().addMapLayer(csv_layer)
        tree_root = QgsProject.instance().layerTreeRoot()
        tree_root.addLayer(csv_layer)
        
        return {self.OUTPUT: dest_id, self.OUTPUT_ASSOC : assoc }

    def name(self):
        return 'generateIntegerFieldCreation'

    def displayName(self):
        return self.tr('Create integer field (new layer creation)')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Aux'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GenerateIntegerFieldCreationAlgorithm()
