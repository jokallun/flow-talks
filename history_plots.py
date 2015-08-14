import json
import pandas as pd
from datetime import datetime, timedelta
import urllib2
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages

www = 'http://flow.rista.net/logs'

def open_msg(msg):
    sdatas = msg['sensors']
    dd = {k: msg[k] for k in ['msg', 'name']}
    dd['ts'] = datetime.strptime(msg['timestamp'].split('.')[0], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)
    for sdata in sdatas:
        dd[sdata['name']] = sdata['value']
    return dd


def read_files():
    msgs = []
    for day in range(5, 15):
        fname = 'Parrulaituri-201508{:02d}.txt'.format(day)
        try:
            f = urllib2.urlopen('{}/{}'.format(www, fname))
        except:
            print('cannot open {}'.format(fname))
            continue
        for line in f:
            try:
                msg = json.loads(line[:-1])
                msgs.append(open_msg(msg))
            except:
                pass
    return msgs


def plot_axis(spec, idx, s, title, ylabel=None, bgimg=None):
    ax = plt.subplot(spec)
    ax.set_title(title)
    ax.plot_date(idx.to_pydatetime(), s, '-')
    ax.xaxis.set_major_locator(dates.HourLocator(byhour=(0, 6, 12, 18)))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_minor_locator(dates.DayLocator())
    ax.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))
    if bgimg is not None:
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.imshow(bgimg, extent=[x0, x1, y0, y1], aspect='auto')
    if ylabel:
        ax.set_ylabel(ylabel)
    plt.show()
    return ax


def plot_all_to_pdf(dfs, sensors, bgimg, fname):

    fig = plt.figure(figsize=(23, 12))
    plt.subplots_adjust(left=0.05, right=0.95)
    i = 0
    idx = dfs[i].index
    s = dfs[i]['Illuminance log10']
    plot_axis(323, idx, s, 'Illuminance',
              ylabel='', bgimg=bgimg)

    i = 1
    idx = dfs[i].index
    s = (4095.0 - dfs[i]['Rain drops']) / 4095.0 * 100.0
    cond = (s >= 0)
    s = s[cond]
    idx = idx[cond]
    plot_axis(321, idx, s, 'Rain drops', bgimg=bgimg)

    idx = dfs[i].index
    s = (4095.0 - dfs[i]['Soil moisture']) / 4095.0 * 100.0
    cond = (s >= 0)
    s = s[cond]
    idx = idx[cond]
    plot_axis(322, idx, s, 'Soil moisture', bgimg=bgimg)

    # i = 2
    # idx = dfs[i].index
    # s = dfs[i].icol(0)
    # plot_axis(324, idx, s, '{}\nTemperature'.format(sensors[i]), 'Celsius', bgimg=bgimg)

    i = 3
    idx = dfs[i].index
    s = dfs[i]['Air pressure']
    plot_axis(325, idx, s, 'Air pressure', 'mbar', bgimg=bgimg)

    s = dfs[i]['Temperature']
    plot_axis(326, idx, s, 'Temperature', 'Celsius', bgimg=bgimg)

    with PdfPages(fname) as pdf:
        pdf.savefig()
        plt.close()
    return fig


def plot_data(idx, s, title, ylabel=None, fname=None, y_log_scale=False, bgimg=None):
    fig, ax = plt.subplots(figsize=(20, 7.5))
    # img = plt.imshow(bgimg)
    # ax = img.axes
    ax.set_title(title)
    ax.plot_date(idx.to_pydatetime(), s, '-')
    ax.xaxis.set_major_locator(dates.HourLocator(byhour=(0, 4, 8, 12, 16, 20)))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_minor_locator(dates.DayLocator())
    ax.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))
    if bgimg is not None:
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.imshow(bgimg, extent=[x0, x1, y0, y1], aspect='auto')
    if y_log_scale:
        ax.set_yscale('log')
    if ylabel:
        ax.set_ylabel(ylabel)
    plt.show()
    if fname:
        plt.savefig(fname)
    return ax


def plot_all_to_files(dfs, sensors, bgimg):
    i = 0
    idx = dfs[i].index
    s = dfs[i]['Illuminance log10']
    plot_data(idx, s, '{}\nIlluminance'.format(sensors[i]),
              ylabel='lx', fname='plots/illuminance.png', bgimg=bgimg)

    i = 1
    idx = dfs[i].index
    s = (4095.0 - dfs[i]['Rain drops']) / 4095.0 * 100.0
    cond = (s >= 0)
    s = s[cond]
    idx = idx[cond]
    plot_data(idx, s, '{}\nRain drops'.format(sensors[i]), fname='plots/rain_drops.png', bgimg=bgimg)

    idx = dfs[i].index
    s = (4095.0 - dfs[i]['Soil moisture']) / 4095.0 * 100.0
    cond = (s >= 0)
    s = s[cond]
    idx = idx[cond]
    plot_data(idx, s, '{}\nSoil moisture'.format(sensors[i]), fname='plots/soil_moisture.png',
              bgimg=bgimg)

    i = 2
    idx = dfs[i].index
    s = dfs[i].icol(0)
    plot_data(idx, s, '{}\nTemperature'.format(sensors[i]), 'Celsius', 'plots/temperature1.png',
              bgimg=bgimg)

    i = 3
    idx = dfs[i].index
    s = dfs[i]['Air pressure']
    plot_data(idx, s, '{}\nAir pressure'.format(sensors[i]), 'mbar', 'plots/air_pressure.png',
              bgimg=bgimg)

    s = dfs[i]['Temperature']
    plot_data(idx, s, '{}\nTemperature'.format(sensors[i]), 'Celsius', 'plots/temperature2.png',
              bgimg=bgimg)


def resample(df, interval='1Min'):
    rdf = df.resample(interval)
    cc = ['Temperature_thermometer' if x == 'DS28-00000505b13c' else x.replace(' ', '_')
          for x in rdf.columns]
    rdf.columns = cc
    return rdf


def main():
    plt.style.use('flow_talks')
    msgs = read_files()
    df = pd.DataFrame(msgs).set_index('ts')
    dfs = []
    sensors = []
    grpd = df.groupby('msg')
    for k in grpd.groups.keys():
        dfs.append(grpd.get_group(k).dropna(axis=1, how='all'))
        sensors.append(k)
    bgimg = plt.imread('flowtalksbg.png')
    # onedf = resample(df)
    plot_all_to_pdf(dfs, sensors, bgimg, 'plots/parrulaituri.pdf')
    # plot_all_to_files(dfs, sensors, bgimg)


if __name__ == '__main__':
    main()
