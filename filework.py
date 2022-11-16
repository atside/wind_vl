import pickle
import datetime

from os.path import join

# import logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     filename='mylog.log',
#     format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
#     datefmt='%H:%M:%S')

path="data"
dt_format = '%y-%m-%d %H:%M:%S'

def save_data_file(data, file):
    with open(join(path,file), 'wb') as openfile:
        pickle.dump(data, openfile)
        # print('file saved to', file)
    return

def read_data_file(file):
    with open(join(path, file), 'rb') as openfile:
        data = pickle.load(openfile)
    return data

# save_data_file({}, 'wind_data.txt')
# print(read_data_file('wind_data.txt'))
# print(read_data_file('shipsdata.txt'))
