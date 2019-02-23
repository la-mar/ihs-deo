Prefixes:
     xsd: http://www.w3.org/2001/XMLSchema
     ns0: http://www.ihsenergy.com/Enerdeq/Schemas/Header
     ns1: http://www.ihsenergy.com/Enerdeq/Schemas/Types
     ns2: http://www.ihsenergy.com/Enerdeq/Schemas/QueryBuilder

Global elements:
     ns0:Header(Username: xsd:string, Password: xsd:string, Application: xsd:string)
     ns2:DeleteQueryRequest(QueryName: xsd:string)
     ns2:DeleteQueryResponse(Result: xsd:string)
     ns2:GetAttributesRequest(Query: xsd:string)
     ns2:GetAttributesResponse(Result: xsd:string)
     ns2:GetChangesAndDeletesFromIdsRequest(DataType: xsd:string, Ids: ns1:ArrayOfId, FromDate: xsd:string, ToDate: xsd:string, Domain: xsd:string)
     ns2:GetChangesAndDeletesRequest(DataType: xsd:string, FromDate: xsd:string, ToDate: xsd:string, Page: xsd:int, Domain: xsd:string)
     ns2:GetChangesAndDeletesResponse(PagingDetails: ns1:PagingResponse, Result: xsd:string)
     ns2:GetCountRequest(Query: xsd:string, TagrgetDatatype: xsd:string, Domain: xsd:string)
     ns2:GetCountResponse(Result: xsd:string)
     ns2:GetCurrentIdsRequest(Domain: xsd:string, DataType: xsd:string, Page: xsd:int)
     ns2:GetCurrentIdsResponse(Ids: ns1:ArrayOfId, PagingDetails: ns1:PagingResponse)
     ns2:GetDailyUpdateIntervalRequest(UpdateDate: xsd:string)
     ns2:GetDailyUpdateIntervalResponse(UpdateStarted: xsd:dateTime, UpdateEnded: xsd:dateTime)
     ns2:GetEntityTypeRequest(Parameters: ns2:GetEntityTypeParameters)
     ns2:GetEntityTypeResponse(Result: xsd:string)
     ns2:GetKeysRequest(Query: xsd:string, TagrgetDatatype: xsd:string, Domain: xsd:string)
     ns2:GetKeysResponse(Result: ns1:ArrayOfStrings)
     ns2:GetLookupsRequest(DataType: xsd:string)
     ns2:GetLookupsResponse(Result: ns2:ArrayOfLookupTypes)
     ns2:GetProductionEntityAttributesRequest(Parameters: ns2:GetProductionEntityAttributesParameters)
     ns2:GetProductionEntityAttributesResponse(Result: xsd:string)
     ns2:GetQueryDefinitionRequest(QueryName: xsd:string)
     ns2:GetQueryDefinitionResponse(Result: xsd:string)
     ns2:GetSQLRequest(Query: xsd:string, Type: ns2:SQLType)
     ns2:GetSQLResponse(Result: xsd:string)
     ns2:GetSavedQueriesRequest(Domain: xsd:string, Datatype: xsd:string)
     ns2:GetSavedQueriesResponse(Queries: ns1:ArrayOfStrings)
     ns2:LookupAttributesRequest(Parameters: ns2:LookupAttrsParameters)
     ns2:LookupAttributesResponse(Result: xsd:string)
     ns2:LookupCodeRequest(Parameters: ns2:LookupParameters)
     ns2:LookupCodeResponse(Codes: ns1:ArrayOfStrings)
     ns2:LookupNameCodeRequest(Parameters: ns2:LookupParameters, SearchType: ns2:NameCodeType)
     ns2:LookupNameCodeResponse(NameCodes: ns2:ArrayOfNameCodes)
     ns2:LookupNameRequest(Parameters: ns2:LookupParameters)
     ns2:LookupNameResponse(Names: ns1:ArrayOfStrings)
     ns2:LookupStateCountyRequest(Parameters: ns2:StateCountyParameters, SearchType: ns2:StateCountyType)
     ns2:LookupStateCountyResponse(StateCounty: ns2:ArrayOfStateCounty)
     ns2:QueryBuilderFault(message: xsd:string)
     ns2:SaveQueryRequest(QueryName: xsd:string, CriteriaXML: xsd:string)
     ns2:SaveQueryResponse(Result: xsd:string)
     ns2:ValidateIdsRequest(Domain: xsd:string, DataType: xsd:string, Ids: ns1:ArrayOfId)
     ns2:ValidateIdsResponse(Ids: ns1:ArrayOfId)
     ns1:ExistsRequest(JobID: xsd:string)
     ns1:ExistsResponse(Result: xsd:boolean)
     ns1:GetDatatypesRequest(Domain: xsd:string)
     ns1:GetDatatypesResponse(Datatypes: ns1:ArrayOfStrings)
     ns1:GetDomainsRequest()
     ns1:GetDomainsResponse(Domains: ns1:ArrayOfStrings)
     ns1:IsCompleteRequest(JobID: xsd:string)
     ns1:IsCompleteResponse(Result: xsd:boolean)


Global types:
     xsd:anyType
     ns2:ArrayOfLayers(Layer: xsd:string[])
     ns2:ArrayOfLookupTypes(Item: ns2:LookupType[])
     ns2:ArrayOfNameCodes(Item: ns2:NameCode[])
     ns2:ArrayOfStateCounty(Item: ns2:StateCounty[])
     ns2:GetEntityTypeParameters(Domain: xsd:string, DataType: xsd:string, IDs: ns1:ArrayOfId, StartDate: xsd:string, EndDate: xsd:string)
     ns2:GetProductionEntityAttributesParameters(Domain: xsd:string, DataType: xsd:string, IDs: ns1:ArrayOfId, Attrs: ns1:ArrayOfStrings, StartDate: xsd:string, EndDate: xsd:string)
     ns2:LookupAttrsParameters(Domain: xsd:string, DataType: xsd:string, Attrs: ns1:ArrayOfStrings, IDs: ns1:ArrayOfId)
     ns2:LookupParameters(Domain: xsd:string, DataType: xsd:string, Attr: xsd:string, SearchValue: xsd:string, Operator: ns2:Operator)
     ns2:LookupType(Lookup: xsd:string, Type: xsd:string)
     ns2:NameCode(Name: xsd:string, Code: xsd:string)
     ns2:NameCodeType
     ns2:Operator
     ns2:SQLType
     ns2:StateCounty(StateCode: xsd:string, StateName: xsd:string, CountyName: xsd:string, CountyCode: xsd:string)
     ns2:StateCountyParameters(Domain: xsd:string, DataType: xsd:string, SearchValue: xsd:string, Operator: ns2:Operator)
     ns2:StateCountyType
     ns1:ArrayOfId(Id: xsd:string[])
     ns1:ArrayOfStrings(Item: xsd:string[])
     ns1:MyFilesTarget(Filename: xsd:string, Overwrite: ns1:OverwriteType)
     ns1:OverwriteType
     ns1:PagingResponse(Page: xsd:int, PageCount: xsd:int, DefaultPageSize: xsd:int, Pages: xsd:int, TotalCount: xsd:int)
     ns1:StatusType
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
     Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/QueryBuilder}QueryBuilderServiceSoap

Service: QueryBuilderService
     Port: QueryBuilderServiceSoap (Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/QueryBuilder}QueryBuilderServiceSoap)
         Operations:
            DeleteQuery(QueryName: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetAttributes(Query: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetChangesAndDeletes(DataType: xsd:string, FromDate: xsd:string, ToDate: xsd:string, Page: xsd:int, Domain: xsd:string, _soapheaders={request_header: ns0:Header}) -> PagingDetails: ns1:PagingResponse, Result: xsd:string
            GetChangesAndDeletesFromIds(DataType: xsd:string, Ids: ns1:ArrayOfId, FromDate: xsd:string, ToDate: xsd:string, Domain: xsd:string, _soapheaders={request_header: ns0:Header}) -> PagingDetails: ns1:PagingResponse, Result: xsd:string
            GetCount(Query: xsd:string, TagrgetDatatype: xsd:string, Domain: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetCurrentIds(Domain: xsd:string, DataType: xsd:string, Page: xsd:int, _soapheaders={request_header: ns0:Header}) -> Ids: ns1:ArrayOfId, PagingDetails: ns1:PagingResponse
            GetDailyUpdateInterval(UpdateDate: xsd:string, _soapheaders={request_header: ns0:Header})
-> UpdateStarted: xsd:dateTime, UpdateEnded: xsd:dateTime
            GetEntityType(Parameters: ns2:GetEntityTypeParameters, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetKeys(Query: xsd:string, TagrgetDatatype: xsd:string, Domain: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: ns1:ArrayOfStrings
            GetLookups(DataType: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: ns2:ArrayOfLookupTypes
            GetProductionEntityAttributes(Parameters: ns2:GetProductionEntityAttributesParameters, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetQueryDefinition(QueryName: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetSQL(Query: xsd:string, Type: ns2:SQLType, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetSavedQueries(Domain: xsd:string, Datatype: xsd:string, _soapheaders={request_header: ns0:Header}) -> Queries: ns1:ArrayOfStrings
            LookupAttributes(Parameters: ns2:LookupAttrsParameters, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            LookupCode(Parameters: ns2:LookupParameters, _soapheaders={request_header: ns0:Header}) -> Codes: ns1:ArrayOfStrings
            LookupName(Parameters: ns2:LookupParameters, _soapheaders={request_header: ns0:Header}) -> Names: ns1:ArrayOfStrings
            LookupNameCode(Parameters: ns2:LookupParameters, SearchType: ns2:NameCodeType, _soapheaders={request_header: ns0:Header}) -> NameCodes: ns2:ArrayOfNameCodes
            LookupStateCounty(Parameters: ns2:StateCountyParameters, SearchType: ns2:StateCountyType,
_soapheaders={request_header: ns0:Header}) -> StateCounty: ns2:ArrayOfStateCounty
            SaveQuery(QueryName: xsd:string, CriteriaXML: xsd:string, _soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            ValidateIds(Domain: xsd:string, DataType: xsd:string, Ids: ns1:ArrayOfId, _soapheaders={request_header: ns0:Header}) -> Ids: ns1:ArrayOfId