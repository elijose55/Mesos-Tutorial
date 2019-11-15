#!/usr/bin/env python

from pymesos import MesosSchedulerDriver, Scheduler, encode_data
import uuid
from addict import Dict
import socket
import getpass
from threading import Thread
import signal
import time
import enum
import os

MESOS_MASTER_IP = os.environ["MESOS_MASTER_IP"]
#MESOS_MASTER_IP = "139.59.11.188"

class Task:
    def __init__(self, taskId, command, cpu, mem):
        self.taskId = taskId
        self.command = command
        self.cpu = cpu
        self.mem = mem

    def __getResource(self, res, name):
        for r in res:
            if r.name == name:
                return r.scalar.value
        return 0.0

    def __updateResource(self, res, name, value):
        if value <= 0:
            return
        for r in res:
            if r.name == name:
                r.scalar.value -= value
        return

    def acceptOffer(self, offer):
        accept = True
        if self.cpu != 0:
            cpu = self.__getResource(offer.resources, "cpus")
            if self.cpu > cpu:
                accept =  False
        if self.mem != 0:
            mem = self.__getResource(offer.resources, "mem")
            if self.mem > mem:
                accept = False
        if(accept == True):
            self.__updateResource(offer.resources, "cpus", self.cpu)
            self.__updateResource(offer.resources, "mem", self.mem)
            return True
        else:
            return False

class PythonScheduler(Scheduler):
    def __init__(self):
        self.idleTaskList = []
        self.startingTaskList = {}
        self.runningTaskList = {}
        self.terminatingTaskList = {}

        self.idleTaskList.append(Task("taskHelloWorld", "echo HelloWORLD", .1, 100))
        self.idleTaskList.append(Task("taskDIR", "mkdir /home/ubuntu//HelloMesos", .1, 100))

    def resourceOffers(self, driver, offers):
        logging.debug("Received new offers")
        logging.info("Recieved resource offers: {}".format([o.id.value for o in offers]))

        if(len(self.idleTaskList) == 0):
            driver.suppressOffers()
            logging.info("Idle Tasks List Empty, Suppressing Offers")
            return

        filters = {'refuse_seconds': 1}

        for offer in offers:
            taskList = []
            pendingTaksList = []
            while True:
                if len(self.idleTaskList) == 0:
                    break
                Task = self.idleTaskList.pop(0)
                if Task.acceptOffer(offer):
                    task = Dict()
                    task_id = Task.taskId
                    task.task_id.value = task_id
                    task.agent_id.value = offer.agent_id.value
                    task.name = 'task {}'.format(task_id)
                    task.command.value = Task.command
                    task.resources = [
                        dict(name='cpus', type='SCALAR', scalar={'value': Task.cpu}),
                        dict(name='mem', type='SCALAR', scalar={'value': Task.mem}),
                    ]
                    self.startingTaskList[task_id] = Task
                    taskList.append(task)
                    logging.info("Starting task: %s, in node: %s" % (Task.taskId, offer.hostname))
                else:
                    pendingTaksList.append(Task)

            if(len(taskList)):
                    driver.launchTasks(offer.id, taskList, filters)

            self.idleTaskList = pendingTaksList

    def statusUpdate(self, driver, update):
        if update.state == "TASK_STARTING":
            Task = self.startingTaskList[update.task_id.value]
            logging.debug("Task %s is starting." % update.task_id.value)
        elif update.state == "TASK_RUNNING":
            if update.task_id.value in self.startingTaskList:
                Task = self.startingTaskList[update.task_id.value]
                logging.info("Task %s running in %s. Moving to running list" %
                (update.task_id.value, update.container_status.network_infos[0].ip_addresses[0].ip_address))
                self.runningTaskList[update.task_id.value] = Task
                del self.startingTaskList[update.task_id.value]
        elif update.state == "TASK_FAILED":
            Task = None
            if update.task_id.value in self.startingTaskList:
                Task = self.startingTaskList[update.task_id.value]
                del self.startingTaskList[update.task_id.value]
            elif update.task_id.value in self.runningTaskList:
                Task = self.runningTaskList[update.task_id.value]
                del self.runningTaskList[update.task_id.value]
            if Task:
                logging.info("Uni task: %s failed." % Task.taskId)
                self.idleTaskList.append(Task)
                driver.reviveOffers()
            else:
                logging.error("Received task failed for unknown task: %s" % update.task_id.value )
        else:
            logging.info("Received status %s for task id: %s" % (update.state, update.task_id.value))

def main():
    framework = Dict()
    framework.user = getpass.getuser()
    framework.id.value = str(uuid.uuid4())
    framework.name = "InsperMesos"
    framework.hostname = socket.gethostname()
    framework.failover_timeout = 75

    driver = MesosSchedulerDriver(
        PythonScheduler(),
        framework,
        MESOS_MASTER_IP,
        use_addict=True,
    )

    def signal_handler(signal, frame):
        driver.stop()

    def run_driver_thread():
        driver.run()

    driver_thread = Thread(target=run_driver_thread, args=())
    driver_thread.start()

    print('Scheduler running, Ctrl+C to quit.')
    signal.signal(signal.SIGINT, signal_handler)

    while driver_thread.is_alive():
        time.sleep(1)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    main()