import matplotlib.pyplot as plt


class MatPlot(object):
    @staticmethod
    def plot_waveform(waveform):
        plt.plot(waveform)
        plt.axis([-100, len(waveform) + 100, min(waveform) * 1.2, max(waveform) * 1.2])
        plt.show()
