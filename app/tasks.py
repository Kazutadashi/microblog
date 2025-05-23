import time

def example(seconds):
    print('starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('task completed')
