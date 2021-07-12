import time

timer = {}


def start_timer(method_name):
    global timer
    timer[method_name] = time.time()
    return


def end_timer(method_name):
    global timer
    end = time.time()
    time_elapsed = round((end - timer.pop(method_name)) * 1000, 2)
    print('Execution time for {method} is {time} ms'.format(method=method_name, time=time_elapsed))
    return
