


import zeep
from zeep import xsd


user = 'brock@driftwoodenergy.com'
password = 'YrUs0LAME!'
appName = 'driftwood_wellprod_digest'

import functools
def soapheaders(func):
    """Capture the analysis method"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # print(f"Calling {func.__name__}({signature})")
        obj = args[0]
        value = func(*args, **kwargs, _soapheaders = obj)
        return value
    return wrapper

class IHSConnector(object):

    _wsdl_dir = 'app/wsdl'
    _domain = 'US;'
    _wsdls = {
        'session' : 'Session.wsdl',
        'querybuilder' : 'QueryBuilder.wsdl',
        'exportbuilder' : 'ExportBuilder.wsdl',
    }
    _dtypes = ['Well', 'Production Allocated']

    def __init__(self, version: str = 'v10'):
        self.version = version
        self._wsdl_path = self._wsdl_dir + f'/{self.version}/'
        self.session = zeep.Client(wsdl=self._wsdl_path+self._wsdls['session'])
        self.querybuilder = zeep.Client(wsdl=self._wsdl_path+self._wsdls['querybuilder'])
        self.exportbuilder = zeep.Client(wsdl=self._wsdl_path+self._wsdls['exportbuilder'])

    # def login(self):


# client = zeep.Client(wsdl=wsdl)

def get_count():
    'Put query that worked here'




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
soapheaders = [header_value]

# session.service.Login(_soapheaders = _soapheaders)


#! Remove below once ported to object definition above

import zeep

wsdl_session = 'app/wsdl/v10/Session.wsdl'
wsdl_querybuilder = 'app/wsdl/v10/QueryBuilder.wsdl'
esdl_exportbuilder = 'app/wsdl/v10/ExportBuilder.wsdl'

session = zeep.Client(wsdl=wsdl_session)
querybuilder = zeep.Client(wsdl=wsdl_querybuilder)
exportbuilder = zeep.Client(wsdl=esdl_exportbuilder)
# client = zeep.Client(wsdl=wsdl)

API = "42383402790000"

domain = 'US'

dtypes = ['Well', 'Production Allocated']

def methods(obj) -> None:
    return [x for x in dir(obj) if not x.startswith('__')]

def m(obj):
    return methods(obj)

def get_count():
    'Put query that worked here'

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
soapheaders = [header_value]

session.service.Login(_soapheaders = _soapheaders)