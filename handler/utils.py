import statistics

def calc_avg_cpu(cpu_list: list):
    return round(statistics.mean(cpu_list), 2)