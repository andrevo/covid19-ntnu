import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import pstats

plt.style.use('master.mplstyle')


def load_data(filename='stateLog_200_trondheim'):
    df = pd.read_csv('results/{}.csv'.format(filename))
    df['I'] = df.Ia + df.Is + df.Ip + df.H + df.ICU
    states = ['Susceptible', 'Exposed', 'Asymptomatic ', 'Presymptomatic', 'Symptomatic', 
              'Recovered', 'Hospitalised', 'ICU', 'Dead', 'Tested', 'Infected']
    df.columns = states
    return df


def plot_sir(filename='stateLog_200_trondheim'):
    df = load_data(filename)
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8,4)

    df[['Susceptible', 'Exposed', 'Infected', 'Recovered']].plot(ax=ax)
    plt.xlabel('Day')
    plt.ylabel('N')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('plots/sir_{}.png'.format(filename), dpi=300)


def plot_stateLog(filename='statelog'):
    df = load_data(filename)
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8,4)

    df.drop(['Susceptible','Recovered'], axis=1).plot(ax=ax)
    plt.xlabel('Day')
    plt.ylabel('N')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('plots/{}.png'.format(filename), dpi=300)


def plot_tests(filename):
    df = load_data(filename)
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8,4)

    df[['Infected', 'Tested']].plot(ax=ax)
    plt.xlabel('Day')
    plt.ylabel('N')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('plots/tested.png'.format(filename), dpi=300)


def main():
    filename = 'stateLog_50'
    # load_data(filename)
    # plot_sir(filename)
    
    plot_tests(filename)

    # plot_stateLog('stateLog_200_oslo')
    

main()
