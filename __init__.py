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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Mathieu Chailloux'
__date__ = '2019-03-28'
__copyright__ = '(C) 2019 by Mathieu Chailloux'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RasterizeString class from file RasterizeString.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rasterize_string import RasterizeStringPlugin
    return RasterizeStringPlugin(iface)
