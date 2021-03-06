"""
시장 가격 데이터 다운로드, 상품별 오브젝트 생성등을 포괄하는 파일
"""

import csv
import os
from datetime import datetime
import h5py
import quandl
import pandas as pd

# meachine learning
import numpy as np
from sklearn.cluster import KMeans
from tslearn.clustering import TimeSeriesKMeans
from tslearn.utils import to_time_series



quandl.ApiConfig.api_key = "6GRDzQGAm5PpBzWdcBT5"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
METAFILE = os.path.join(BASE_DIR, 'instruments.csv')
HISTORYFILE = os.path.join(BASE_DIR, 'history', 'futures.h5py')

class Instrument:
    """
    상품 정보 및 과거 데이터를 포함하는 오브젝트
    """ 
    
    def __init__(self, symbol, name, exchange, currency, market, region\
                 ,startdate, tickunit, tickprice, margin, depth, decimallength, has_history, is_tradable):
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
        self.currency = currency
        self.market = market
        self.region = region
        self.startdate = startdate
        self.tickunit = tickunit
        self.tickprice = tickprice
        self.margin = margin
        self.depth = depth
        self.decimallength = decimallength
        self.has_history = has_history
        self.is_tradable = is_tradable
        self.code = f'{self.exchange}_{self.symbol}'
    
    def __repr__(self):
        return f"{self.name}({self.symbol})"
    
    def history(self, start=0, length=0):
        db = h5py.File(HISTORYFILE, mode='r')
        if start == 0:
            history = db[self.code][:]
        elif length == 0:
            history = db[self.code][-start:]
        else:
            history = db[self.code][-start:-start+length]
        db.close()
        return history
    
    def to_df(self, start=0, length=0):
        """
        * 한 상품의 ohlcv 데이터를 pandas dataframe 형식으로 바꿔주는 함수
        * Output:
          - pandas dataframe
        """
        columns = ['date','open','high','low','close','volume','op_int']
        df = pd.DataFrame(data=self.history(start, length), columns=columns)
        df['date'] = df['date'].astype('M8[ms]')
        df.set_index('date', inplace=True)
        return df

    def context_object(self):
        return dict(
            symbol=self.symbol,
            name=self.name,
            exchange=self.exchange,
            currency=self.currency,
            market=self.market,
            region = self.region,
            startdate = self.startdate,
            tickunit = self.tickunit,
            tickprice = self.tickprice,
            margin = self.margin,
            depth = self.depth,
            decimallength = self.decimallength,
            has_history = self.has_history,
            is_tradable = self.is_tradable,
            code = f'{self.exchange}_{self.symbol}',
        )
        
        
class Instruments:
    _lists = [] #개별 상품 인스턴트 리스트
    with open(METAFILE ,'r', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _instruments = list(reader)
        
        for instrument in _instruments:
            __instrument = Instrument(
                symbol=instrument['symbol'].lower(),
                name=instrument['name'].lower(),
                exchange=instrument['exchange'].lower(),
                currency=instrument['currency'].lower(),
                market=instrument['market'].lower(),
                region=instrument['region'].lower(),
                startdate=datetime.strptime(instrument['startdate'],'%Y-%m-%d'),
                tickunit=float(instrument['tickunit']),
                tickprice=float(instrument['tickprice']),
                margin=float(instrument['margin']),
                depth=int(instrument['depth']),
                decimallength=int(instrument['decimallength']),
                has_history=True if instrument['has_history']=='y' else False,
                is_tradable=True if instrument['is_tradable']=='y' else False
            )
            _lists.append(__instrument)
    del f, instrument, reader
    

    @staticmethod
    def get(**kwargs):
            #symbol=None,name=None, exchange=None, startdate=None, currency=None, region=None\
            #,tickunit=None, tickprice=None, margin=None, depth=None, decimal_length=None\
            #,has_history=None, is_tradable=None):
        attrs = ['symbol','name','exchange','startdate','currency','region','code'\
                ,'tickunit','tickprice','margin','depth','decimallength','has_history','is_tradable']
        def func(ins):
            for key, value in kwargs.items():
                value = value.lower() if isinstance(value, str) else value
                if key not in attrs:
                    return False
                
                if getattr(ins, key) != value:
                    return False
            return True
        return [ret for ret in filter(func, Instruments._lists)]


    #quandl에서 history 다운 받아 DB 업데이트 
    @staticmethod
    def update_history():
        with open(METAFILE ,'r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            instruments = []
            for row in reader:
                instruments.append(row)
        
        db = h5py.File(HISTORYFILE, mode='w')
        db.attrs['columns'] = 'date;open;high;low;close;volume;op_int'
        db.attrs['last_update'] = str(datetime.today().date())
        print("*** 업데이트 시작... ***")
        for instrument in instruments:
            if instrument['has_history'] == 'y':
                print(instrument['name'])
                
                exch = instrument['exchange'].lower()
                symbol = instrument['symbol'].lower()
                depth = instrument['depth']
                code = f"{exch}_{symbol}{depth}_OB"
                df=quandl.get_table('SCF/PRICES', quandl_code=code, paginate=True)[::-1]
                df['date'] = df['date'].astype('int64')/1e6
                data = df[['date','open','high','low','settle','volume','prev_day_open_interest']]
                group = db.create_dataset((exch+'_'+symbol).lower(), data.shape, data=data, dtype='float64')
                group.attrs['symbol'] = symbol
                group.attrs['exchange'] = exch
                group.attrs['name'] = instrument['name'].lower()
                group.attrs['code'] = code.lower()
        print("*** 완료 ***")

    #최종 업데이트 날짜
    @staticmethod
    def last_update():
        db = h5py.File(HISTORYFILE, mode='r')
        last = db.attrs['last_update']
        db.close()
        return last

    #자동 섹터 분류
    @staticmethod
    def define_sectors(window=40):
        instruments = Instruments.get(is_tradable=True, has_history=True)
        codes = [instrument.code for instrument in instruments]
        arr = []
        for a in instruments:
            b = a.history(start=window)[:,1:5]
            b = (b-b.min())/(b.max()-b.min()) #data normalize
            arr.append(b)
        arr = np.array(arr)
        km = TimeSeriesKMeans(n_clusters=8, n_init=200, max_iter=300).fit(arr)
        n_codes = np.array(codes)
        sectors = [n_codes[np.where(km.labels_ == i)[0]].tolist() for i in range(8)]
        
        #db파일에 attribute로 저장
        db = h5py.File(HISTORYFILE, mode='r+')
        # 섹터내의 종목들은 ';' 로, 섹터들은 '/' 로 구분됨
        # ex) 'ice_dx;ice_sb/cme_bp;cme_c;cme_o;cme_pl;cme_rb;cme_rr;cme_si'
        db.attrs['sectors'] = '/'.join([';'.join(sector) for sector in sectors])
        db.close()

    @staticmethod
    def sectors():
        db = h5py.File(HISTORYFILE, mode='r')
        sectors = db.attrs['sectors']
        db.close()
        codes = [ sector.split(';') for sector in sectors.split('/') ]
        return [[ Instruments.get(code=c)[0] for c in i ] for i in codes]

        
