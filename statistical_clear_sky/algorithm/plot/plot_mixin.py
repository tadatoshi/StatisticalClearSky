"""
This module defines Mixin for plot for IterativeClearSky.
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class PlotMixin(object):

    def plot_lr(self, figsize=(14, 10), show_days=False):
        fig, ax = plt.subplots(nrows=2, ncols=2, figsize=figsize)
        ax[0, 1].plot(self._r_cs_value[0])
        ax[1, 1].plot(self._r_cs_value[1:].T)
        ax[0, 0].plot(self._l_cs_value[:, 0])
        ax[1, 0].plot(self._l_cs_value[:, 1:])
        ax[0, 0].legend(['$\\ell_1$'])
        ax[1, 0].legend(['$\\ell_{}$'.format(ix) for ix in range(2,
            self._r_cs_value.shape[0] + 1)])
        ax[0, 1].legend(['$r_{1}$'])
        ax[1, 1].legend(['$r_{}$'.format(ix) for ix in range(2,
            self._r_cs_value.shape[0] + 1)])
        if show_days:
            use_day = self._obtain_weights_for_plotting() > 1e-1
            days = np.arange(self._power_signals_d.shape[1])
            ax[0, 1].scatter(days[use_day], self._r_cs_value[0][use_day],
                color='orange', alpha=0.7)
        plt.tight_layout()
        return fig

    def plot_energy(self, figsize=(12, 6), show_days=True, show_clear=False):
        plt.figure(figsize=figsize)
        plt.plot(np.sum(self._power_signals_d, axis=0) * 24 / self._power_signals_d.shape[0], linewidth=1)
        if show_clear:
            plt.plot((self._r_cs_value[0] * np.sum(self._l_cs_value[:, 0])) *
                24 / self._power_signals_d.shape[0], linewidth=1)
        if show_days:
            use_day = self._obtain_weights_for_plotting() > 1e-1
            days = np.arange(self._power_signals_d.shape[1])
            plt.scatter(days[use_day], np.sum(self._power_signals_d,
                axis=0)[use_day] * 24 / self._power_signals_d.shape[0],
                color='orange', alpha=0.7)
        fig = plt.gcf()
        return fig

    def plot_singular_vectors(self, k=4, figsize=(10, 4), show_days=False):
        fig, ax = plt.subplots(nrows=k, ncols=2, figsize=(figsize[0], 2*figsize[1]))
        for i in range(k):
            ax[i][0].plot(self._matrix_l0.T[i], linewidth=1)
            ax[i][0].set_xlim(0, self._power_signals_d.shape[0])
            ax[i][0].set_ylabel('$\\ell_{}$'.format(i + 1))
            ax[i][1].plot(self._matrix_r0[i], linewidth=1)
            ax[i][1].set_xlim(0, self._power_signals_d.shape[1])
            ax[i][1].set_ylabel('$r_{}$'.format(i + 1))
        ax[-1][0].set_xlabel('$i \\in 1, \\ldots, m$ (5-minute periods in one day)')
        ax[-1][1].set_xlabel('$j \\in 1, \\ldots, n$ (days)')
        if show_days:
            use_day = self._obtain_weights_for_plotting() > 1e-1
            days = np.arange(self._power_signals_d.shape[1])
            for i in range(k):
                ax[i, 1].scatter(days[use_day], self._matrix_r0[i][use_day], color='orange', alpha=0.7)
        plt.tight_layout()
        return fig

    def plot_power_signals_d(self, figsize=(12, 6), show_days=False):
        with sns.axes_style("white"):
            fig, ax = plt.subplots(nrows=1, figsize=figsize, sharex=True)
            foo = ax.imshow(self._power_signals_d, cmap='hot', interpolation='none', aspect='auto')
            ax.set_title('Measured power')
            plt.colorbar(foo, ax=ax, label='kW')
            ax.set_xlabel('Day number')
            ax.set_yticks([])
            ax.set_ylabel('Time of day')
            if show_days:
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                use_day = self._obtain_weights_for_plotting() > 1e-1
                days = np.arange(self._power_signals_d.shape[1])
                y1 = np.ones_like(days[use_day]) * self._power_signals_d.shape[0] * .99
                ax.scatter(days[use_day], y1, marker='|', color='yellow', s=2)
                ax.scatter(days[use_day], .995*y1, marker='|', color='yellow', s=2)
                ax.set_xlim(*xlim)
                ax.set_ylim(*ylim)
        return fig

    def plot_measured_clear(self, figsize=(12, 10), show_days=False):
        with sns.axes_style("white"):
            fig, ax = plt.subplots(nrows=2, figsize=figsize, sharex=True)
            foo = ax[0].imshow(self._power_signals_d, cmap='hot', interpolation='none', aspect='auto')
            ax[0].set_title('Measured power')
            bar = ax[1].imshow(self.clear_sky_signals(), cmap='hot',
                               vmin=0, vmax=np.max(self._power_signals_d), interpolation='none', aspect='auto')
            ax[1].set_title('Estimated clear sky power')
            plt.colorbar(foo, ax=ax[0], label='kW')
            plt.colorbar(bar, ax=ax[1], label='kW')
            ax[1].set_xlabel('Day number')
            ax[0].set_yticks([])
            ax[0].set_ylabel('Time of day')
            ax[1].set_yticks([])
            ax[1].set_ylabel('Time of day')
            if show_days:
                xlim = ax[0].get_xlim()
                ylim = ax[0].get_ylim()
                use_day = self._obtain_weights_for_plotting() > 1e-1
                days = np.arange(self._power_signals_d.shape[1])
                y1 = np.ones_like(days[use_day]) * self._power_signals_d.shape[0] * .99
                ax[0].scatter(days[use_day], y1, marker='|', color='yellow', s=2)
                ax[0].scatter(days[use_day], .995 * y1, marker='|', color='yellow', s=2)
                ax[0].set_xlim(*xlim)
                ax[0].set_ylim(*ylim)
            plt.tight_layout()
        return fig

    def ts_plot(self, start_day=0, num_days=2, figsize=(8, 4), loc=(.35, .7)):
        d1 = start_day
        d2 = d1 + num_days
        actual = self._power_signals_d[:, d1:d2].ravel(order='F')
        clearsky = ((self.clear_sky_signals()))[:, d1:d2].ravel(order='F')
        fig, ax = plt.subplots(nrows=1, figsize=figsize)
        ax.plot(actual, linewidth=1, label='measured power')
        ax.plot(clearsky, linewidth=1, color='red', label='clear sky signal')
        plt.legend(loc=loc)
        n = self._power_signals_d.shape[0]
        ax.set_xlim(0, n * (d2 - d1))
        ax.set_ylabel('kW')
        ax.set_xticks(np.arange(0, n * num_days, 4 * 12))
        ax.set_xticklabels(np.tile(np.arange(0, 24, 4), num_days))
        ax.set_xlabel('Hour of Day')
        plt.show()

    def ts_plot_with_weights(self, fig_title=None, start_day=0, num_days=5,
                             figsize=(16, 8)):
        n = self._power_signals_d.shape[0]
        d1 = start_day
        d2 = d1 + num_days
        actual = self._power_signals_d[:, d1:d2].ravel(order='F')
        clearsky = ((self.clear_sky_signals()))[:, d1:d2].ravel(order='F')
        fig, ax = plt.subplots(num=fig_title, nrows=2, figsize=figsize, sharex=True,
                               gridspec_kw={'height_ratios': [3, 1]})
        xs = np.linspace(d1, d2, len(actual))
        ax[0].plot(xs, actual, alpha=0.4, label='measured power')
        ax[0].plot(xs, clearsky, linewidth=1, label='clear sky estimate')
        ax[1].plot(xs, np.repeat(self._obtain_weights_for_plotting()[d1:d2],
            n), linewidth=1, label='day weight')
        ax[0].legend()
        ax[1].legend()
        # ax[0].set_ylim(0, np.max(actual) * 1.3)
        ax[1].set_xlim(d1, d2)
        ax[1].set_ylim(0, 1)
        ax[1].set_xlabel('day number')
        ax[0].set_ylabel('power')
        plt.tight_layout()
        return fig

    def _obtain_weights_for_plotting(self):
        '''
        Workaround not to perform long-running weight setting optimization code
        in constructor.
        '''
        if (not hasattr(self, '_weights')) or (self._weights is None):
            self._weights = self._obtain_weights()
        return self._weights
