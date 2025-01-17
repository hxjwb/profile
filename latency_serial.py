




# log_files = ['try_bbr_pace.log' , 'try_bbr_nopace.log']
# log_files = ['gcc_ace.log' , 'gcc_rtc.log']
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
        
    import matplotlib.pyplot as plt

    for index, latency in enumerate(lists):
        plt.plot(latency, label=log_files[index])

    plt.legend()

    plt.savefig(output_file)