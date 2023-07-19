import os
import json
import random
import subprocess
from PIL import Image

random.seed()

CONFIG_NAME = "config.json"
ROOT_DIR = os.path.dirname(__file__)

TEST_CONFIG_KEY = "tests"
GENERAL_CONFIG_KEY = "general"

TASK_DIRS_KEY = "folder_list"
FILE_SUFFIX_KEY = "solution_file_suffix"
FOLDER_SUFFIX_KEY = "solution_folder_suffix"
IMG_PROGRAM_KEY = "img_program"

config = []

tasks = []
done_tasks = []
history = []


def read_config():
    config_file = os.path.join(ROOT_DIR, CONFIG_NAME)

    if not os.path.isfile(config_file):
        print(f"Config file missing, please add {CONFIG_NAME} to {ROOT_DIR}!")
        exit()

    with open(config_file, "r") as f:
        config = json.load(f)

    # TODO: add checks for keys in config

    return config


def load_tasks(config):
    global tasks
    task_dirs = config[TEST_CONFIG_KEY][TASK_DIRS_KEY]
    folder_suffix = config[GENERAL_CONFIG_KEY][FOLDER_SUFFIX_KEY]
    file_suffix = config[GENERAL_CONFIG_KEY][FILE_SUFFIX_KEY]

    for task_dir in task_dirs:
        task_dir = task_dir[:-1] if task_dir[-1] == "/" else task_dir

        task_names = os.listdir(task_dir)

        task_count = 0
        for task_name in task_names:
            task_count += 1
            solution_dir = task_dir + folder_suffix

            # check if solution folder exists
            if not os.path.isdir(solution_dir):
                print(f"Solution folder for {task_dir} missing!")
                print(f"Please add {solution_dir}!")
                exit()

            task_location = os.path.join(task_dir, task_name)
            task_split = os.path.splitext(task_name)
            solution_location = os.path.join(solution_dir, task_split[0] + file_suffix + task_split[1])

            if not os.path.isfile(solution_location):
                print(f"Solution for {task_name} missing!")
                print(f"Please add {solution_location}!")
                exit()

            tasks.append((task_location, solution_location))
        print(f"{task_count} tasks found in {os.path.basename(task_dir)}")


def show_file(file):
    img_program = config[GENERAL_CONFIG_KEY][IMG_PROGRAM_KEY]
    #file = file.replace(' ', '\ ')


    #print(img_program, file)
    #proc = subprocess.Popen([img_program, file], shell=True)
    proc = Image.new(file)
    proc.show()

    return proc


def switch_task(index=None, task_process=None, solution_process=None):
    # close current tasks
    if task_process:
        #task_process.kill()
        task_process.close()

    # close current solutions
    if solution_process:
        #solution_process.kill()
        solution_process.close()

    if index != None:
        interactive_menu(index)
    else:
        exit()


def interactive_menu(index=0):
    """
    e -> exit
    n -> next
    p -> previous
    s -> show solution
    """
    global tasks
    global history
    global done_tasks

    task_process, solution_process = None, None

    if index > len(history) - 1:
        # recycle tasks
        if len(tasks) == 0:
            tasks = done_tasks
            done_tasks = []

        # pick new task
        new_task = random.choice(tasks)
        history.append(new_task)
        done_tasks.append(new_task)
        tasks.remove(new_task)

    # display task
    print(f"Question number {index + 1}")
    task_file = history[index][0]
    # print("Task" + task_file)
    task_process = show_file(task_file)

    command = input("Command: ")

    if command in ["e", "exit"]:
        print("Bye!")
        switch_task(task_process=task_process, solution_process=solution_process) # exits without index
    if command in ["n", "next"]:
        switch_task(index=index + 1, task_process=task_process, solution_process=solution_process)
    if command in ["p", "previous"]:
        if index - 1 < 0:
            print("No previous task!")

        switch_task(index=index - 1, task_process=task_process, solution_process=solution_process)

    if command in ["s", "solution"]:
        solution_file = history[index][1]
        # close current solution
        if solution_process:
            #solution_process.kill()
            solution_process.close()

        # open new solution
        solution_process = show_file(solution_file)
        # print("Solution: " + solution_file)

    # chase with no matching command
    print("No matching command!")
    switch_task(index=index, task_process=task_process, solution_process=solution_process)


def main():
    global config
    config = read_config()
    load_tasks(config)

    print()
    print("Control handed over to user now:")
    interactive_menu()


if __name__ == "__main__":
    main()
