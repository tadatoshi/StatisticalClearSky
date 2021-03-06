"""
This module defines functionality unique to left matrix minimization.
"""
import cvxpy as cvx
import numpy as np
from statistical_clear_sky.solver_type import SolverType
from statistical_clear_sky.algorithm.minimization.abstract\
 import AbstractMinimization
from statistical_clear_sky.algorithm.exception import ProblemStatusError

class LeftMatrixMinimization(AbstractMinimization):
    """
    Uses minimization method in parent class with fixed Right matrix value,
    keeping Left matrix as a variable.
    """

    def __init__(self, power_signals_d, rank_k, weights, tau, mu_l,
                 solver_type=SolverType.ecos):

        super().__init__(power_signals_d, rank_k, weights, tau,
                         solver_type=solver_type)
        self._mu_l = mu_l

    def _define_parameters(self, l_cs_value, r_cs_value, beta_value):
        l_cs_param = cvx.Variable(shape=(self._power_signals_d.shape[0],
                                         self._rank_k))
        l_cs_param.value = l_cs_value
        r_cs_param = r_cs_value
        beta_param = cvx.Variable()
        beta_param.value = beta_value
        return l_cs_param, r_cs_param, beta_param

    def _term_f2(self, l_cs_param, r_cs_param):
        weights_w2 = np.eye(self._rank_k)
        term_f2 = self._mu_l * cvx.norm((l_cs_param[:-2, :] - 2
                * l_cs_param[1:-1, :] + l_cs_param[2:, :]) * weights_w2, 'fro')
        return term_f2

    def _term_f3(self, l_cs_param, r_cs_param):
        return 0

    def _constraints(self, l_cs_param, r_cs_param, beta_param, component_r0):
        ixs = self._handle_bad_night_data()
        if sum(ixs) > 0:
         return [
                l_cs_param * r_cs_param >= 0,
                l_cs_param[ixs, :] == 0,
                cvx.sum(l_cs_param[:, 1:], axis=0) == 0
            ]
        else:
            return [
                l_cs_param * r_cs_param >= 0,
                cvx.sum(l_cs_param[:, 1:], axis=0) == 0
            ]

    def _handle_exception(self, problem):
        if problem.status != 'optimal':
            raise ProblemStatusError('Minimize L status: ' + problem.status)

    def _result(self, l_cs_param, r_cs_param, beta_param):
        return l_cs_param.value, r_cs_param, beta_param.value

    def _handle_bad_night_data(self):
        '''
        Method for generating the "nighttime" index set

        This method finds the (approximate) set of time stamps that correspond with
        nighttime across all seasons in the given data.

        Old method looked for timestamps with an average power across all days that is
        smaller than 0.5% of the max power value in the data set.

        New method still looks for timestamps with values below 0.5% of the max, but
        then converts this to a sparsity by row, and returns the rows with a sparsity
        of greater than 96%. This approach is more robust than the old method because
        it is not sensitive to the magnitude of any spurious nighttime data values.
        :return:
        '''
        data = self._power_signals_d
        row_sparsity = 1 - np.sum(data > 0.005 * np.max(data), axis = 1) / data.shape[1]
        threshold = 0.96
        #ix_array = np.average(self._power_signals_d, axis=1) / np.max(
        #    np.average(self._power_signals_d, axis=1)) <= 0.005
        ix_array = row_sparsity >= threshold
        return ix_array
