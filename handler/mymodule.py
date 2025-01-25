import utils

def main(input: dict, context: object) -> dict[str, any]:
    metrics = {}
    metrics['percent-memory-caching'] = round(100*((input['virtual_memory-buffers']+input['virtual_memory-cached'])/input['virtual_memory-total']), 2)
    metrics['percent-network-egress'] = round(100*(input['net_io_counters_eth0-bytes_sent']/(input['net_io_counters_eth0-bytes_sent']+input['net_io_counters_eth0-bytes_recv'])), 2)
    metrics['timestamp'] = input['timestamp']
    if not hasattr(context, 'monitoring_interval'):
        avg_window = 60/5
    else:
        avg_window = 60/context.monitoring_interval
    env = context.env
    for key in input.keys():
        if 'cpu_percent-' in key:
            cpu_number = key.split('-')[1]
            if f'cpu-window-{cpu_number}' in env:
                env[f'cpu-window-{cpu_number}'].append(input[key])
                if len(env[f'cpu-window-{cpu_number}']) == avg_window + 1:
                    env[f'cpu-window-{cpu_number}'].pop(0)
                    metrics[f'avg-util-cpu{cpu_number}-60sec'] = utils.calc_avg_cpu(env[f'cpu-window-{cpu_number}'])
                else:
                    metrics[f'avg-util-cpu{cpu_number}-60sec'] = 0
            else:
                env[f'cpu-window-{cpu_number}'] = [input[key]]
                metrics[f'avg-util-cpu{cpu_number}-60sec'] = 0
    
    context.env = env
    
    return metrics