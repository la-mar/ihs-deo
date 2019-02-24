from app.connection import *
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'
EB = zeep.Client(wsdl=eb_wsdl)

def get_layers():
    return EB.service.GetLayers(_soapheaders = [header_value])

def get_formats():
    return EB.service.GetSpatialExportFormats(_soapheaders = [header_value])

# ns1:SpatialExportParameters(LatMin: xsd:double, LatMax: xsd:double, LongMin: xsd:double, LongMax: xsd:double, Layers: ns2:ArrayOfStrings, Format: xsd:string)

# BuildSpatialExport(
#                               Parameters: ns1:SpatialExportParameters,
#                               Target: ns2:MyFilesTarget,
#                               _soapheaders={request_header: ns0:Header}
#                               )
#                               -> JobID: xsd:string

param = {
    'LatMin': 0,
    'LatMax':0,
    'LongMin': 0,
    'LongMax' : 0,
    'Layers' : get_layers(),
    'Format' : get_formats()
}

target = {
  'Filename':'Sample',
'Overwrite': 'True'
}

EB.service.BuildSpatialExport(param, target, _soapheaders = [header_value])