Prefixes:
     xsd: http://www.w3.org/2001/XMLSchema
     ns0: http://www.ihsenergy.com/Enerdeq/Schemas/Header
     ns1: http://www.ihsenergy.com/Enerdeq/Schemas/Session

Global elements:
     ns0:Header(Username: xsd:string, Password: xsd:string, Application: xsd:string)
     ns1:EntitlementRequest()
     ns1:EntitlementResponse(Result: xsd:string)
     ns1:LatLongEntitlementRequest()
     ns1:LatLongEntitlementResponse(Result: xsd:string)
     ns1:LoginRequest()
     ns1:LoginResponse(Result: xsd:boolean)
     ns1:LogoutRequest()
     ns1:LogoutResponse()


Global types:
     xsd:anyType
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
     Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/Session}SessionServiceSoap

Service: SessionService
     Port: SessionServiceSoap (Soap11Binding: {http://www.ihsenergy.com/Enerdeq/Schemas/Session}SessionServiceSoap)
         Operations:
            GetEntitlements(_soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            GetLatLongEntitlements(_soapheaders={request_header: ns0:Header}) -> Result: xsd:string
            Login(_soapheaders={request_header: ns0:Header}) -> Result: xsd:boolean
            Logout(_soapheaders={parameters: ns1:LogoutRequest}) ->