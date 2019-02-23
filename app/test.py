


import zeep
wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
qb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\QueryBuilder.wsdl'
eb_wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\ExportBuilder.wsdl'

client = zeep.Client(wsdl=wsdl)

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

client.service.Login(_soapheaders=[header_value])


client.service


zeep.wsdl.wsdl()

dir(client)

dir(client.service)