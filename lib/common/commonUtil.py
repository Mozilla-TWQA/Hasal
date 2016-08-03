import re
import matplotlib.pyplot as plt


class CommonUtil(object):
    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split('(\d+)', text)]

    @staticmethod
    def plot_waveform(waveform):
        plt.plot(waveform)
        plt.axis([-100, len(waveform) + 100, min(waveform) * 1.2, max(waveform) * 1.2])
        #plt.savefig("waveform.png")
        plt.show()
