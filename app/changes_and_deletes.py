
from app.connection import *
from time import sleep



# , '2019/01/01', '2019/01/31'
QB.service.GetDailyUpdateInterval()
QB.service.GetChangesAndDeletes('Well', '2019/01/01', '2019/02/01', 1, _soapheaders=[header_value])