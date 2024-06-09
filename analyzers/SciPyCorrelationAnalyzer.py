from numpy import cov
from scipy.stats import spearmanr, pearsonr, false_discovery_control

from model.Table import Table
from model.params.CorrelationInput import CorrelationInput


class SciPyCorrelationAnalyzer:

    def analyze(self, inputs: list[CorrelationInput]) -> Table:
        p_values_pearson = [pearsonr(corr_input.data_1, corr_input.data_2)[1] for corr_input in inputs]
        p_values_spearman = [spearmanr(corr_input.data_1, corr_input.data_2)[1] for corr_input in inputs]
        p_values_adjusted_pearson = list(false_discovery_control(p_values_pearson))
        p_values_adjusted_spearman = list(false_discovery_control(p_values_spearman))
        return Table(
            [
                Table.Column("Covariance",
                             list(map(lambda corr_input: cov(corr_input.data_1, corr_input.data_2)[1][1], inputs))),
                Table.Column("Pearson",
                             list(map(lambda corr_input: pearsonr(corr_input.data_1, corr_input.data_2)[0], inputs))),
                Table.Column("Pearson p-valor", p_values_pearson),
                Table.Column("Pearson p-valor adjusted", p_values_adjusted_pearson),
                Table.Column("Spearman",
                             list(map(lambda corr_input: spearmanr(corr_input.data_1, corr_input.data_2)[0], inputs))),
                Table.Column("Spearman p-valor", p_values_spearman),
                Table.Column("Spearman p-valor adjusted", p_values_adjusted_spearman)
            ],
            list(map(lambda corr_input: corr_input.label, inputs)))
