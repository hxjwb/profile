

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Plot latency')
    parser.add_argument('log_files', metavar='log_files', type=str, nargs='+',
                        help='log files to plot')
    parser.add_argument('--output_file', metavar='output_file', type=str, default='latency.png',
                        help='output file name')
    args = parser.parse_args()
    log_files = args.log_files

    output_file = args.output_file
    lists = []

    for log_file in log_files:
        lines = open(log_file).readlines()

        latency = []

        for line in lines:
            if 'e2e' in line:
                latency.append(float(line.split()[-1]))
                
        lists.append(latency)


    for index, latency in enumerate(lists):
        label = log_files[index]
        latency = latency[200:]
        print(label, len(latency))
        latency.sort()

        position = [i / 1000 for i in range(1000)]

        values = [latency[int(len(latency) * i)] for i in position]

        import matplotlib.pyplot as plt

        select_position = [0.5, 0.9, 0.95, 0.99, 0.999]
        values = [latency[int(len(latency) * i)] for i in select_position]
        print(values[2])
        select_position = [str(i * 100)+'%' for i in select_position]


        plt.plot(values, select_position, label=label)
    plt.xlabel('Latency (s)')
    plt.ylabel('CDF')
    plt.title('Latency CDF')
    plt.legend()
        

    plt.savefig(output_file)