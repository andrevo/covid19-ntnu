'''
Author: Helge Bergo
Date: January 2021
File: analysis.py

This file contains different analysis and plot functions, to analyse the results
from the main simulation in model.py. 
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob, os

plt.style.use('master.mplstyle')


def load_data(filename='stateLog_200_trondheim'):
    df = pd.read_csv(f'results/{filename}.csv')
    print(df)
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


def plot_stateLog(filename='stateLog_Trondheim'):
    df = load_data(filename)
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8,4)

    df.drop(['Susceptible','Recovered','Tested'], axis=1).plot(ax=ax)
    plt.xlabel('Day')
    plt.ylabel('N')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('plots/{}.png'.format(filename), dpi=300)


def plot_infLog(filename='infLogByLayer_Trondheim_n500_d50'):
    # df = load_data(filename)
    df = pd.read_csv(f'results/{filename}.csv')
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8,4)
    
    df.plot(ax=ax)
    plt.xlabel('Day')
    plt.ylabel('N')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(f'plots/{filename}.png', dpi=300)


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



def plot_latest_simulation(path='./results/'):
    paths = [os.path.join(path, basename) for basename in os.listdir(path)]
    latest_file = max(paths, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    print(df)


def main():
    filename = 'stateLog_Trondheim_n500_d50'
    # load_data(filename)
    # plot_sir(filename)
    
    # plot_tests()
    # plot_stateLog(filename)
    # plot_infLog()

    plot_latest_simulation()


main()
