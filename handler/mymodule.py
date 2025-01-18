import utils

def main(input: dict, context: object) -> dict[str, any]:
    metrics = {}
    metrics['percent-network-egress'] = round(input['virtual_memory-buffers']/input['virtual_memory-total'], 2)
    metrics['percent-memory-caching'] = round(input['virtual_memory-cached']/input['virtual_memory-total'], 2)
    if not hasattr(context, 'monitoring_interval'):
        avg_window = 60/5
    else:
        context.monitoring_interval = 10
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