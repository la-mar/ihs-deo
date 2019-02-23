


import zeep

wsdl = 'C:\Repositories\Collector-IHS\docs\DirectConnect\wsdl.v10\Session.wsdl'
client = zeep.Client(wsdl=wsdl)

proxy = client.bind()

user = 'brock@driftwoodenergy.com'
password = 'YrUs0LAME!'

from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport

session = Session()
session.auth = HTTPBasicAuth(user, password)
c = Client(wsdl,
    transport=Transport(session=session))

# s = c.wsdl.services
# s = s['SessionService']

c.service.Login()

b = c.bind()

b.Login()





