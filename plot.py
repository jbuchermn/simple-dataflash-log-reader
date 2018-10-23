import matplotlib.pyplot as plt


class Plot:
    def __init__(self, description, x_axis="TimeUS", x_scale=1.e6):
        self.desired_values = []
        self.x_axis = x_axis
        self.x_scale = x_scale
        self.desired_values = []
        self.parse(description)

        self.data_sets = []
        for i in range(len(self.desired_values)):
            self.data_sets += [[]]

    def parse(self, description):
        for val in description.split(","):
            tmp = val.split(".")
            self.desired_values += [(tmp[0].strip(), tmp[1].strip())]

    def feed(self, data_point):
        for i, v in enumerate(self.desired_values):
            if data_point.name == v[0]:
                self.data_sets[i] += [(data_point.values[self.x_axis],
                                      data_point.values[v[1]])]

    def plot(self):
        t_start = min([v[0][0] for v in self.data_sets])
        fig = plt.figure()
        for i, d in enumerate(self.data_sets):
            plt.plot([(v[0]-t_start)/self.x_scale for v in d],
                     [v[1] for v in d],
                     label=".".join(self.desired_values[i]))

        plt.legend()
        plt.show(block=False)
        input("Done? ")
        plt.close(fig)


if __name__ == '__main__':
    import sys
    from log_file import LogFile

    logf = LogFile(sys.argv[1])

    if len(sys.argv) > 2:
        plot = Plot(" ".join(sys.argv[2:]))
        for v in logf.read():
            plot.feed(v)

        plot.plot()
    else:
        all_formats = {}
        for v in logf.read():
            if v.name not in all_formats:
                all_formats[v.name] = [k for k in v.values]

        for fmt in sorted(all_formats.keys()):
            print("%4s: %s" % (fmt, ", ".join(all_formats[fmt])))
