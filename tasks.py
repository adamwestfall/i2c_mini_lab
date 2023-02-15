"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import mma845x


def task1_fun(my_queue):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    # my_share, my_queue = shares

    state = 0
    while True:
        if state == 0:
            #init state
            i2c = pyb.I2C(1,pyb.I2C.CONTROLLER)
            accel_addr = 29
            accelerometer = mma845x.MMA845x(i2c,accel_addr)
            accelerometer.active()
            state = 1
        if state == 1:
            # getting the data from the accelerometer and putting it in a queue
            x_accel = accelerometer.get_ax()
            my_queue.put(x_accel)

        # my_share.put(counter)
        # my_queue.put(counter)
        # counter += 1

        yield 0


def task2_fun(the_queue):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    # the_share, the_queue = shares

    while True:
        # Show everything currently in the queue and the value in the share
        # print(f"Share: {the_share.get ()}, Queue: ", end='')
        while q0.any():
            print(f"Xval: {the_queue.get ()} ", end='')
        print('')

        yield 0


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    # share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('f', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=500,
                        profile=True, trace=False, shares=(q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=500,
                        profile=True, trace=False, shares=(q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')