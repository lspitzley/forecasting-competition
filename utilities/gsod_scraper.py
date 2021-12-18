# -*- coding: utf-8 -*-
"""
This code was copied and adapted from

https://github.com/tagomatech/ETL/tree/master/gsod

on 2021-09-28.

It has not been compared to the output of the R script
that does a similar download. 
"""

# """ gsodscraper.py """

import requests, os, re, gzip, folium, sys
import numpy as np
import pandas as pd
import datetime as dt

TMP = 'tmp/'

#%%
class GSOD(object):

    def __init__(self, wx_list_flag=False, country=None, state=None, start=None, end=None):

        # It is assume that NOAA doesn't rename the isd-historycsv file
        self.file_csv = os.path.join(TMP, 'isd-history.csv')

        self.wx_list_flag = wx_list_flag

        self.ctry = country
        if isinstance(self.ctry, str):
            self.ctry = self.ctry.split()

        self.sta = state
        if isinstance(self.sta, str):
            self.sta = self.sta.split()

        if isinstance(start, str):
            self.start = pd.Timestamp(start)

        if isinstance(start, dt.date):
            self.start = pd.Timestamp(start)

        if not start:
            self.start = pd.Timestamp(dt.date(dt.datetime.now().year, 1, 1))

        if isinstance(end, str):
            self.end = pd.Timestamp(end)

        if isinstance(end, dt.date):
            self.end = pd.Timestamp(end)

        if not end:
            now = dt.datetime.now()
            self.end = pd.Timestamp(dt.date(now.year, now.month, now.day) + \
            dt.timedelta(days=-3)) # <aybe adjusting the end parameter?

    def _ISDwXstationSlist(self):
        # iT is a factory function

        df_mapping = {'USAF' : str,
                        'WBAN' : str,
                        'STATION NAME' : str,
                        'CTRY' : str,
                        'STATE' : str,
                        'ICAO' : str,
                        'LAT' : float,
                        'LON' : float,
                        'ELEV' : float}#,
                        #'BEGIN' : str,
                        #'END' : str}
        date_parser = ['BEGIN' , 'END']

        if self.wx_list_flag:
            # Read weather list of available weather stations on NOAA servers
            try:
                print('Wait! Downloading isd-history.csv file from NOAA servers...')
                #url =  'http://www1.ncdc.noaa.gov/pub/data/noaa/isd-history.csv'
                #url = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv'
                url = 'https://www1.ncdc.noaa.gov/pub/data/noaa/isd-history.csv' # Wx stations list here is longer than others showed at alternative URLs 

                df_isd = pd.read_csv(url,
                                        dtype=df_mapping,
                                        parse_dates=date_parser)
                print('Download complete!')
                #print(df_isd.head())

                # Rename 'STATION NAME' to 'STATION_NAME'
                #df_isd = df_isd.rename(index=str, columns={'STATION NAME' : 'STATION_NAME'})
                df_isd = df_isd.rename(index=str, columns={'STATION NAME' : 'STATION_NAME', 'ELEV(M)' : 'ELEV'})

                # Merge 'USAF' and 'WBAN'
                df_isd['STATION_ID'] = df_isd.USAF + '-' + df_isd.WBAN
                
                # Get rid of useless columns
                #df_isd = df_isd.drop(['USAF', 'WBAN', 'ICAO', 'ELEV(M)'], axis=1)
                df_isd = df_isd.drop(['USAF', 'WBAN', 'ICAO'], axis=1)

                df_isd.to_csv(self.file_csv, index=False)

                self.wx_list_flag = False

                return df_isd

            except Exception as err:
                print(err)

        else:
            # Read the csv file already downloaded and stored in GSOD folder
            try:
                df_isd = pd.read_csv(self.file_csv, dtype=df_mapping, parse_dates=date_parser)
                #print(df_isd.head())
                return df_isd

            except IOError as err:
                print('Cannot find isd-history.csv on the disk...')
                self.wx_list_flag = True
                df_isd = self._ISDwXstationSlist()
                return df_isd

    def getAvailableWxStations(self):
        '''
        Return a list of available weather stations given a set of parameters
        that simply slice the original dataframe comprising all ISD weather stations

        '''
        # Level 1 selection: use start date and end date in the isd-history file
        if self.ctry == None and self.sta == None:
            print('''Requires at least 'country' or 'state' keyword argument!\n''')
            raise Exception()

        df_isd = self._ISDwXstationSlist()

        if self.ctry:
            #df_sliced = df_isd[df_isd.CTRY.isin(self.ctry)]

            df_sliced = df_isd[(df_isd.CTRY.isin(self.ctry)) & (df_isd.BEGIN <= self.start) & 
                (df_isd.END >= self.end)]

        if self.sta:
            #df_sliced = df_isd[df_isd.STATE.isin(self.sta)]
            df_sliced = df_isd[(df_isd.STATE.isin(self.sta)) & (df_isd.BEGIN <= self.start) & 
                (df_isd.END >= self.end)]

        # Level 2 selection: get through the folders on  NOAA servers for each year from
        # the year of 'start' parameter to 'end'

        start_year = self.start.year
        end_year = self.end.year
        list_stns = df_sliced.STATION_ID
        #print(list_stns)
        df_avail = pd.DataFrame()

        for y in range(start_year, end_year+1):
            #print(y)
            url = os.path.join('https://www1.ncdc.noaa.gov/pub/data/gsod/', str(y))
            #print(url)
            req = requests.get(url)
            acc= []
            for stn in list_stns:
                if bool(re.search(stn, req.text)):
                    acc.append(1)
                else:
                    acc.append(pd.np.nan)

            df_tmp = pd.DataFrame({ y : acc}, index=list_stns)

            df_avail =pd.concat([df_avail, df_tmp], axis=1)
    
        list_stns_avail = df_avail.dropna(axis=0, how='any').index.tolist()


        return df_isd[df_isd.STATION_ID.isin(list_stns_avail)].reset_index(drop=True)


    @staticmethod
    def plotWxStations(df):
        '''
        Plot weather stations on a map (inside a notebook). Input parameter 'df'
        is a pandas.dataFrame() similar to the one out of the getAvailableWxStations() function
        '''
        mid_lat = df.LAT.mean()
        mid_lon = df.LON.mean()
        map_ = folium.Map(location=[mid_lat, mid_lon],
                              width='85%',
                              height='85%',
                              #line_color='#3186cc',
                              #fill_color='#3186cc',
                              #fillOpacity=0.6,
                              zoom_start=5)
        for lat, lon, stn_id, stn_nam in zip(df.LAT, df.LON, df.STATION_ID, df.STATION_NAME):
            folium.Marker([lat, lon], popup='{}:\n{}'.format(stn_id, stn_nam)).add_to(map_)
            
        return map_


    def get_data(self, station=None, start_year=dt.datetime.now().year, end_year=dt.datetime.now().year, **kwargs):
        '''
        Get weather data from the internet as memory stream
        '''
        big_df = pd.DataFrame()

        for year in range(start_year, end_year+1):

            # Define URL
            url = 'http://www1.ncdc.noaa.gov/pub/data/gsod/' + str(year) + '/' + str(station) \
                + '-' + str(year) + '.op.gz'

            # Define data stream
            stream = requests.get(url)

            # Unzip on-the-fly
            decomp_bytes = gzip.decompress(stream.content)
            data = decomp_bytes.decode('utf-8').split('\n')

            # Remove start and end elements
            data.pop(0) # Remove first line header
            data.pop()  # Remove last element

            # Define lists
            (stn, wban, date, mean_tmp, mean_tmp_f, dew_point, dew_point_f,
             mean_sea_level_press, mean_sea_level_press_f, mean_stn_pressure, mean_stn_pressure_f, visib, visib_f,
             mean_wind_speed, mean_wind_speed_f, max_wind_speed, max_gust_speed, max_tmp, max_tmp_f, min_tmp, min_tmp_f,
             prcp, prcp_f, snow_depth, fog_f, rain_or_drizzle_f, snow_or_ice_pellets_f, hail_f, thunder_f, tornado_f) = ([] for i in range(30))

            # Fill in lists
            for i in range(0, len(data)):
                stn.append(data[i][0:6])
                wban.append(data[i][7:12])
                date.append(data[i][14:22])         
                mean_tmp.append(data[i][25:30])
                mean_tmp_f.append(data[i][31:33])
                dew_point.append(data[i][36:41])
                dew_point_f.append(data[i][42:44])
                mean_sea_level_press.append(data[i][46:52])      # Mean sea level pressure
                mean_sea_level_press_f.append(data[i][53:55])
                mean_stn_pressure.append(data[i][57:63])      # Mean station pressure
                mean_stn_pressure_f.append(data[i][64:66])
                visib.append(data[i][68:73])
                visib_f.append(data[i][74:76])
                mean_wind_speed.append(data[i][78:83])
                mean_wind_speed_f.append(data[i][84:86])
                max_wind_speed.append(data[i][88:93])
                max_gust_speed.append(data[i][95:100])
                max_tmp.append(data[i][103:108])
                max_tmp_f.append(data[i][108])
                min_tmp.append(data[i][111:116])
                min_tmp_f.append(data[i][116])
                prcp.append(data[i][118:123])
                prcp_f.append(data[i][123])
                snow_depth.append(data[i][125:130])   # Snow depth in inches to tenth
                fog_f.append(data[i][132])          # Fog
                rain_or_drizzle_f.append(data[i][133])          # Rain or drizzle
                snow_or_ice_pellets_f.append(data[i][134])          # Snow or ice pallet
                hail_f.append(data[i][135])          # Hail
                thunder_f.append(data[i][136])         # Thunder
                tornado_f.append(data[i][137])         # Tornado or funnel cloud

            '''
            Replacements
            min_tmp_f & max_tmp_f
            blank   : explicit => e
            *       : derived => d
            '''
            max_tmp_f = [re.sub(pattern=' ', repl='e', string=x) for x in max_tmp_f] # List comprenhension
            max_tmp_f = [re.sub(pattern='\*', repl='d', string=x) for x in max_tmp_f]

            min_tmp_f = [re.sub(pattern=' ', repl='e', string=x) for x in min_tmp_f]
            min_tmp_f = [re.sub(pattern='\*', repl='d', string=x) for x in min_tmp_f]

            # Create intermediate matrix
            mat = np.matrix(data=[stn, wban, date, mean_tmp, mean_tmp_f, dew_point, dew_point_f,
                   mean_sea_level_press, mean_sea_level_press_f, mean_stn_pressure, mean_stn_pressure_f, visib, visib_f,
                   mean_wind_speed, mean_wind_speed_f, max_wind_speed, max_gust_speed, max_tmp, max_tmp_f, min_tmp, min_tmp_f,
                   prcp, prcp_f, snow_depth, fog_f, rain_or_drizzle_f, snow_or_ice_pellets_f, hail_f, thunder_f, tornado_f]).T

            # Define header names
            headers = ['stn', 'wban', 'timestamp', 'mean_tmp', 'mean_tmp_f', 'dew_point', 'dew_point_f', 'mean_sea_level_press',
                        'mean_sea_level_press_f', 'mean_stn_pressure', 'mean_stn_pressure_f', 'visib', 'visib_f', 'mean_wind_speed',
                        'mean_wind_speed_f', 'max_wind_speed', 'max_gust_speed', 'max_tmp', 'max_tmp_f', 'min_tmp', 'min_tmp_f',
                        'prcp', 'prcp_f', 'snow_depth', 'fog_f', 'rain_or_drizzle_f', 'snow_or_ice_pellets_f', 'hail_f', 'thunder_f', 'tornado_f']

            # Set precision
            pd.set_option('precision', 3)

            # Create dataframe from matrix object
            df = pd.DataFrame(data=mat, columns=headers)

            # Replace missing values with NAs
            df = df.where(df != ' ', 9999.9)

            # Create station ids
            df['STATION_ID'] = df['stn'].map(str) + '-' + df['wban'].map(str)
            df = df.drop(['stn', 'wban'], axis=1)

            # Convert to numeric
            df[['mean_tmp', 'mean_tmp_f', 'dew_point', 'dew_point_f', 'mean_sea_level_press', 'mean_sea_level_press_f',
                'mean_stn_pressure', 'mean_stn_pressure_f', 'visib', 'visib_f', 'mean_wind_speed', 'mean_wind_speed_f',
                'max_wind_speed',  'max_gust_speed', 'max_tmp', 'min_tmp', 'prcp', 'snow_depth']] = df[['mean_tmp', 'mean_tmp_f', 'dew_point',
                                                                       'dew_point_f', 'mean_sea_level_press', 'mean_sea_level_press_f', 'mean_stn_pressure',
                                                                       'mean_stn_pressure_f', 'visib', 'visib_f', 'mean_wind_speed',
                                                                       'mean_wind_speed_f', 'max_wind_speed', 'max_gust_speed', 'max_tmp',
                                                                       'min_tmp', 'prcp', 'snow_depth']].apply(pd.to_numeric)
            # Replace missing weather data with NaNs
            df = df.replace(to_replace=[99.99, 99.9,999.9,9999.9], value=np.nan)
            
            # Convert to date format
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d')

            big_df = pd.concat([big_df, df])

        #print(big_df.head())

        # Add weather station information to the dataframe
        df_isd = self._ISDwXstationSlist() # OK print(df_isd.head())
                
        stn_id = ''.join(str(x) for x in big_df.STATION_ID.head(1).values)
        big_df['ctry'] = np.repeat(df_isd.CTRY[df_isd.STATION_ID == stn_id].values, big_df.shape[0])

        big_df['state'] = np.repeat(df_isd.STATE[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        big_df['station_name'] = np.repeat(df_isd.STATION_NAME[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        big_df['lat'] = np.repeat(df_isd.LAT[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        big_df['lon'] = np.repeat(df_isd.LON[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        # Added ELEV
        big_df['elevation'] = np.repeat(df_isd.ELEV[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        big_df['begin'] = np.repeat(df_isd.BEGIN[df_isd.STATION_ID == stn_id].values, big_df.shape[0])
        big_df['end'] = np.repeat(df_isd.END[df_isd.STATION_ID == stn_id].values, big_df.shape[0])

        big_df.columns = map(str.lower, big_df.columns)

        #return big_df

        # Make transformations on data, clean, convert
        df = self._dataCleanerConverter(big_df)
        return df


    def _dataCleanerConverter(self, df):
        """
        """
        ''' 
        Precipitation: transform prcp based on prcp_f, then convert to inch. to mm

        A = 1 report of 6-hour precipitation amount.
        B = Summation of 2 reports of 6-hour precipitation amount.
        C = Summation of 3 reports of 6-hour precipitation amount.
        D = Summation of 4 reports of 6-hour precipitation amount.
        E = 1 report of 12-hour precipitation amount.
        F = Summation of 2 reports of 12-hour precipitation amount.
        G = 1 report of 24-hour precipitation amount.
        H = Station reported '0' as the amount for the day (eg, from 6-hour reports),
            but also reported at least one occurrence of precipitation in hourly observations
            --this could indicate a trace occurred, but should be considered as incomplete data for the day.
        I = Station did not report any precip data for the day and did not report any occurrences of
            precipitation in its hourly observations--it's still possible that precip occurred but was not reported.
        '''
        df['prcp_fct'] = np.nan
        df.loc[df.prcp_f == 'A', 'prcp_fct'] = 4
        df.loc[df.prcp_f == 'B', 'prcp_fct'] = 2
        df.loc[df.prcp_f == 'C', 'prcp_fct'] = 4/3
        df.loc[df.prcp_f == 'D', 'prcp_fct'] = 1
        df.loc[df.prcp_f == 'E', 'prcp_fct'] = 2
        df.loc[df.prcp_f == 'F', 'prcp_fct'] = 1
        df.loc[df.prcp_f == 'G', 'prcp_fct'] = 1
        df.loc[df.prcp_f == 'H', 'prcp_fct'] = 1
        df.loc[df.prcp_f == 'I', 'prcp_fct'] = 1
        df.prcp_fct = df.prcp_fct.replace(np.nan, 1, regex=True)

        df.prcp = df.prcp * df.prcp_fct
        df = df.drop(labels='prcp_fct', axis=1)

        # Conversion to Europe/metric units
        df.prcp = df.prcp / 0.0393701
        df.mean_tmp  = (df.mean_tmp - 32) * 5 / 9
        df.max_tmp  = (df.max_tmp - 32) * 5 / 9
        df.min_tmp  = (df.min_tmp - 32) * 5 / 9

        # Replace NAs
        df.prcp = df.prcp.fillna(value=0)
        df.state = df.state.fillna(value='not_applicable')

        
        return df


    # "Unpivoted table" to feed SQL server
    def SQLFeeder(self, df, attribute):
        if isinstance(attribute, str):
            attribute = [attribute]
        
        df_out = pd.DataFrame()
        
        for attr in attribute:
            df_tmp = pd.DataFrame()
            df_tmp['country'] = df.ctry
            df_tmp['state'] = df.state
            df_tmp['station_id'] = df.station_id
            df_tmp['station_name'] = df.station_name
            df_tmp['latitude'] = df.lat
            df_tmp['longitude'] = df.lon

            # TODO: adding *ELEVATION* column

            df_tmp['timestamp'] = df.timestamp
            df_tmp['start_date'] = df.begin
            df_tmp['end_date'] = df.end # At max will be 2 or 3 days before the date data were downloaded from NOAA servers
            df_tmp['attribute'] = attr
            df_tmp['value'] = df[attr]
            
            df_out = pd.concat([df_out, df_tmp], axis=0)


        '''
        # CAUTION!!!  the unit conversion steps have been commented in the code above!!
        # Add column for unit
        df_out['unit'] = pd.np.nan
        #
        df_out.loc[df_out.attribute == 'prcp', 'unit'] = 'mm'
        df_out.loc[df_out.attribute == 'mean_tmp', 'unit'] = 'C'
        # Do the same for other attributes ...
        '''
        return df_out

        #d = SQLFeeder(df, ['prcp', 'mean_tmp'])