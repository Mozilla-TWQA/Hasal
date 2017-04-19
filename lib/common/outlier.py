import numpy as np


class outlier(object):
    def detect(self, input_seq, method=1, drop_outlier=True):
        seq = sorted(input_seq, key=lambda k: k['run_time'])
        seq_value = [d['run_time'] for d in seq]
        outliers = []
        outliers_value = []
        if len(seq) >= 3:
            if drop_outlier:
                # Default using Moore and McCabe method to calculate quartile value
                Q_Calculation = {
                    '1': self.Q_MooreMcCabe,
                    '2': self.Q_Tukey,
                    '3': self.Q_FreundPerles,
                    '4': self.Q_Minitab
                }
                [Q1, Q3] = Q_Calculation.setdefault(str(method), self.Q_MooreMcCabe)(seq_value)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                for data in seq:
                    if data['run_time'] < lower or data['run_time'] > upper:
                        outliers.append(data)
                        outliers_value.append(data['run_time'])
                self.drop(seq, outliers)
                self.drop(seq_value, outliers_value)
        if len(seq) == 0:
            mean = 0
            median = 0
            sigma = 0
            si = 0
            psi = 0
        elif len(seq) % 2:
            median = float(seq[(len(seq) - 1) / 2]['run_time'])
            mean = np.mean(seq_value)
            sigma = np.std(seq_value)
            si = float(seq[(len(seq) - 1) / 2]['si'])
            psi = float(seq[(len(seq) - 1) / 2]['psi'])
        else:
            median = float(seq[len(seq) / 2 - 1]['run_time'] + seq[len(seq) / 2]['run_time']) / 2
            mean = np.mean(seq_value)
            sigma = np.std(seq_value)
            si = float(seq[len(seq) / 2 - 1]['si'] + seq[len(seq) / 2]['si']) / 2
            psi = float(seq[len(seq) / 2 - 1]['psi'] + seq[len(seq) / 2]['psi']) / 2
        return mean, median, sigma, seq, outliers, si, psi

    def Q_MooreMcCabe(self, seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 2) / 4] + seq[(seq_len + 2) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 2) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 2) / 4] + seq[(3 * seq_len + 2) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 2) / 4 - 1])
        return [Q1, Q3]

    def Q_Tukey(self, seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 2) / 4] + seq[(seq_len + 2) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 2) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 2) / 4] + seq[(3 * seq_len + 2) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 2) / 4 - 1])
        return [Q1, Q3]

    def Q_FreundPerles(self, seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        return [Q1, Q3]

    def Q_Minitab(self, seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        return [Q1, Q3]

    def drop(self, seq, outliers):
        for outlier in outliers:
            seq.remove(outlier)
        return seq
