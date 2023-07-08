from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PrepareData():
    def __init__(self, dataframe):
        self.df = dataframe
        self.outliers = self.Outliers(self.df)

    def prepare(self):
        self.outliers.drop_outliers()
        self.outliers.drop_less_populated()
        self.df = self.outliers.df
        return self.df
    
    class Outliers():
        def __init__(self, dataframe):
            self.df = dataframe
            self.group = self.df.groupby('name').price.describe().sort_values(by='mean', ascending=False)
            self.group = self.group[self.group['count'] > np.mean(self.group['count'])]

        def plot_outliers(self, include_all=False):
            if include_all:
                names = pd.unique(self.group.index)
            else:
                names = self.group[self.group['std'] > 1000].index

            fig, ax = plt.subplots()
            for i, name in enumerate(names):
                local_group = self.df[self.df['name'] == name]
                ax.boxplot(list(local_group.price), vert=False, positions=[i], widths=0.6)
            ax.set_yticklabels(names)
            ax.set_xlabel('Price')
            ax.set_ylabel('Region')

            plt.tight_layout()
            plt.show()

        def Q2(self, array):
            return np.median(array)

        def Q1(self, array):
            array = np.sort(array)
            return np.median(array[:int(len(array)/2)])

        def Q3(self, array):
            array = np.sort(array)
            return np.median(array[int(len(array)/2):])

        def IQR(self, array):
            return self.Q3(array)- self.Q1(array)

        def find_outliers(self, name):
            array = self.df[self.df['name']==name].price.sort_values(axis=0)
            q1 = self.Q1(array)
            q3 = self.Q3(array)
            iqr = stats.iqr(array)
            bad_indeces = [index for index, value in zip(array.index, array.values) if (value < q1 - 3.5*iqr) or (value > q3 + 3.5*iqr)]
            return bad_indeces

        def drop_outliers(self):
            # iqr: stat.iqr(array)
            # outlier < Q1 - 1.5*IQR
            # outlier > Q3 + 1.5*IQR

            names = list(pd.unique(self.df.name))

            for name in names:
                # if len(self.df[self.df['name'] == name]) > 3:
                bad_indeces = self.find_outliers(name)
                if bad_indeces:
                    self.df = self.df.drop(bad_indeces, axis=0)

        def drop_less_populated(self):
            names = list(pd.unique(self.df.name))

            for name in names:
                length = len(self.df[self.df['name'] == name])
                if length < 10 :
                    # print(name, length)
                    # drop 
                    bad_indeces = self.df[self.df['name'] == name].index
                    self.df = self.df.drop(bad_indeces, axis=0)

