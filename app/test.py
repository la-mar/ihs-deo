


import zeep
wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
qb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\QueryBuilder.wsdl'
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'

CC = zeep.Client(wsdl=wsdl)
QB = zeep.Client(wsdl=qb_wsdl)
EB = zeep.Client(wsdl=eb_wsdl)
# client = zeep.Client(wsdl=wsdl)

def methods(obj) -> None:
    return [x for x in dir(obj) if not x.startswith('__')]

def m(obj):
    return methods(obj)

from zeep import xsd

user = 'brock@driftwoodenergy.com'
password = 'YrUs0LAME!'
appName = 'driftwood_wellprod_digest'

header = xsd.Element(
    '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Header',
    xsd.ComplexType([
        xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Username',
            xsd.String()),
            xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Password',
            xsd.String()),
            xsd.Element(
            '{http://www.ihsenergy.com/Enerdeq/Schemas/Header}Application',
            xsd.String())
    ])
)

header_value = header(Username=user, Password = password, Application = appName)

_soapheaders = [header_value]

CC.service.Login(_soapheaders = _soapheaders)


c = EB
s = EB.service

s.GetEntitlements(_soapheaders = _soapheaders) # works



