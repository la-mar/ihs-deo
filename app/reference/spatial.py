from app.connection import *
# eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'
# EB = zeep.Client(wsdl=eb_wsdl)

def get_layers():
    return exportbuilder.service.GetLayers(_soapheaders = [header_value])

def get_formats():
    return exportbuilder.service.GetSpatialExportFormats(_soapheaders = [header_value])

# ns1:SpatialExportParameters(LatMin: xsd:double, LatMax: xsd:double, LongMin: xsd:double, LongMax: xsd:double, Layers: ns2:ArrayOfStrings, Format: xsd:string)

# BuildSpatialExport(
#                               Parameters: ns1:SpatialExportParameters,
#                               Target: ns2:MyFilesTarget,
#                               _soapheaders={request_header: ns0:Header}
#                               )
#                               -> JobID: xsd:string

param = {
    'LatMin': 26.4465566,
    'LatMax':36.9460185,
    'LongMin': -108.1533238,
    'LongMax' : -93.7819362,
    'Layers' : ['Well (Surface)'],
    'Format' : 'SHAPE'
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

exportbuilder.service.BuildSpatialExport(param, target, _soapheaders = [header_value])