Prefixes:
     xsd: http://www.w3.org/2001/XMLSchema
     ns0: http://www.ihsenergy.com/Enerdeq/Schemas/Header
     ns1: http://www.ihsenergy.com/Enerdeq/Schemas/ExportBuilder
     ns2: http://www.ihsenergy.com/Enerdeq/Schemas/Types

Global elements:
     ns1:BuildExportFromQueryRequest(Parameters: ns1:ExportParameters2, Target: ns2:MyFilesTarget)
     ns1:BuildExportRequest(Parameters: ns1:ExportParameters, Target: ns2:MyFilesTarget)
     ns1:BuildExportResponse(JobID: xsd:string)
     ns1:BuildOnelineExportFromQueryRequest(Parameters: ns1:OnelineExportParameters2, Target: ns2:MyFilesTarget)
     ns1:BuildOnelineExportRequest(Parameters: ns1:OnelineExportParameters, Target: ns2:MyFilesTarget)
     ns1:BuildProdSummaryFromQueryRequest(Parameters: ns1:OnelineExportParameters2, Target: ns2:MyFilesTarget)
     ns1:BuildProdSummaryReportRequest(Parameters: ns1:OnelineExportParameters, Target: ns2:MyFilesTarget)
     ns1:BuildSpatialExportRequest(Parameters: ns1:SpatialExportParameters, Target: ns2:MyFilesTarget)
     ns1:DeleteExportRequest(JobID: xsd:string)
     ns1:DeleteExportResponse(Result: xsd:boolean)
     ns1:GetCompleteExportsRequest()
     ns1:GetCompleteExportsResponse(ExportNames: ns2:ArrayOfStrings)
     ns1:GetExportStatusRequest(JobID: xsd:string)
     ns1:GetExportStatusResponse(Status: ns2:StatusType)
     ns1:GetExportTemplatesRequest(Domain: xsd:string, DataType: xsd:string)
     ns1:GetExportTemplatesResponse(Templates: ns2:ArrayOfStrings)
     ns1:GetLayersRequest()
     ns1:GetLayersResponse(Layers: ns2:ArrayOfStrings)
     ns1:GetSpatialExportFormatsRequest()
     ns1:GetSpatialExportFormatsResponse(Formats: ns2:ArrayOfStrings)
     ns1:RetrieveExportRequest(JobID: xsd:string, Compress: xsd:boolean)
     ns1:RetrieveExportResponse(ByteArray: xsd:base64Binary)
     ns0:Header(Username: xsd:string, Password: xsd:string, Application: xsd:string)
     ns2:ExistsRequest(JobID: xsd:string)
     ns2:ExistsResponse(Result: xsd:boolean)
     ns2:GetDatatypesRequest(Domain: xsd:string)
     ns2:GetDatatypesResponse(Datatypes: ns2:ArrayOfStrings)
     ns2:GetDomainsRequest()
     ns2:GetDomainsResponse(Domains: ns2:ArrayOfStrings)
     ns2:IsCompleteRequest(JobID: xsd:string)
     ns2:IsCompleteResponse(Result: xsd:boolean)


Global types:
     xsd:anyType
     ns1:ExportParameters(Domain: xsd:string, DataType: xsd:string, Template: xsd:string, Ids: ns2:ArrayOfId)
     ns1:ExportParameters2(Domain: xsd:string, DataType: xsd:string, Template: xsd:string, Query: xsd:string)
     ns1:OnelineExportParameters(Domain: xsd:string, DataType: xsd:string, Ids: ns2:ArrayOfId, Template: xsd:string, FileType: xsd:string)
     ns1:OnelineExportParameters2(Query: xsd:string, Template: xsd:string, FileType:
xsd:string, Domain: xsd:string)
     ns1:SpatialExportParameters(LatMin: xsd:double, LatMax: xsd:double, LongMin: xsd:double, LongMax: xsd:double, Layers: ns2:ArrayOfStrings, Format: xsd:string)
     ns2:ArrayOfId(Id: xsd:string[])
     ns2:ArrayOfStrings(Item: xsd:string[])
     ns2:MyFilesTarget(Filename: xsd:string, Overwrite: ns2:OverwriteType)
     ns2:OverwriteType
     ns2:PagingResponse(Page: xsd:int, PageCount: xsd:int, DefaultPageSize: xsd:int,
Pages: xsd:int, TotalCount: xsd:int)
     ns2:StatusType
     xsd:ENTITIES
     xsd:ENTITY
     xsd:ID
     xsd:IDREF
     xsd:IDREFS
     xsd:NCName
     xsd:NMTOKEN
     xsd:NMTOKENS
     xsd:NOTATION
     xsd:Name
     xsd:QName
     xsd:anySimpleType
     xsd:anyURI
     xsd:base64Binary
     xsd:boolean
     xsd:byte
     xsd:date
     xsd:dateTime
     xsd:decimal
     xsd:double
     xsd:duration
     xsd:float
     xsd:gDay
     xsd:gMonth
     xsd:gMonthDay
     xsd:gYear
     xsd:gYearMonth
     xsd:hexBinary
     xsd:int
     xsd:integer
     xsd:language
     xsd:long
     xsd:negativeInteger
     xsd:nonNegativeInteger
     xsd:nonPositiveInteger
     xsd:normalizedString
     xsd:positiveInteger
     xsd:short
     xsd:string
     xsd:time
     xsd:token
     xsd:unsignedByte
     xsd:unsignedInt
     xsd:unsignedLong
     xsd:unsignedShort

Bindings:
     Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/ExportBuilder}ExportBuilderServiceSoap

Service: ExportBuilderService
     Port: ExportBuilderServiceSoap (Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/ExportBuilder}ExportBuilderServiceSoap)
         Operations:

          BuildExport(
                    Parameters: ns1:ExportParameters,
                    Target: ns2:MyFilesTarget,
                    _soapheaders={request_header: ns0:Header}
                    )
                    -> JobID: xsd:string

          BuildSpatialExport(
                              Parameters: ns1:SpatialExportParameters,
                              Target: ns2:MyFilesTarget,
                              _soapheaders={request_header: ns0:Header}
                              )
                              -> JobID: xsd:string

          DeleteExport(
                       JobID: xsd:string,
                       _soapheaders={request_header: ns0:Header}
                       )
                       -> Result: xsd:boolean

          Exists(
               JobID: xsd:string,
                    _soapheaders={request_header: ns0:Header})
                    -> Result: xsd:boolean

               GetCompleteExports(
                                   _soapheaders={request_header: ns0:Header}
                                   )
                                   -> ExportNames: ns2:ArrayOfStrings

          GetDatatypes(
               Domain: xsd:string,
                    _soapheaders={request_header: ns0:Header}
                    )
                    -> Datatypes: ns2:ArrayOfStrings
               GetDomains(
                         _soapheaders={request_header: ns0:Header}
                         ) -> Domains: ns2:ArrayOfStrings

          GetExportStatus(
               JobID: xsd:string,
                    _soapheaders={request_header: ns0:Header}
                    )
                    -> Status: ns2:StatusType
               GetExportTemplates(
                              Domain: xsd:string,
                              DataType: xsd:string,
                              _soapheaders={request_header: ns0:Header}
                              )
                              -> Templates: ns2:ArrayOfStrings

          GetLayers(
               _soapheaders={request_header: ns0:Header}
                    )
                    -> Layers: ns2:ArrayOfStrings

          GetSpatialExportFormats(
               _soapheaders={request_header: ns0:Header}
               )
               -> Formats: ns2:ArrayOfStrings

          IsComplete(
          JobID: xsd:string,
          _soapheaders={request_header: ns0:Header}
          )
          -> Result: xsd:boolean

          RetrieveExport(
               JobID: xsd:string,
               Compress: xsd:boolean,
               _soapheaders={request_header: ns0:Header}
               )
               -> ByteArray: xsd:base64Binary