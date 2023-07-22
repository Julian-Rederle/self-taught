import os
import json
import random
import subprocess
from termcolor import colored, cprint
import keyboard

random.seed()

CONFIG_NAME = "config.json"
ROOT_DIR = os.path.dirname(__file__)

TEST_CONFIG_KEY = "tests"
GENERAL_CONFIG_KEY = "general"

TASK_DIRS_KEY = "folder_list"
FILE_SUFFIX_KEY = "solution_file_suffix"
FOLDER_SUFFIX_KEY = "solution_folder_suffix"
IMG_PROGRAM_KEY = "img_program"
PROGRESS_FILE_KEY = "progress_file"

config = []

tasks = []
done_tasks = []
history = []

progress_file = ""


def read_config():
    config_file = os.path.join(ROOT_DIR, CONFIG_NAME)

    if not os.path.isfile(config_file):
        # print(f"Config file missing, please add {CONFIG_NAME} to {ROOT_DIR}!")
        cprint(f"Config file missing, please add {CONFIG_NAME} to {ROOT_DIR}!", "red")
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
                # print(f"Solution folder for {task_dir} missing!")
                # print(f"Please add {solution_dir}!")
                cprint(f"Solution folder for {task_dir} missing!", "red")
                cprint(f"Please add {solution_dir}!", "red")
                exit()

            task_location = os.path.join(task_dir, task_name)
            task_split = os.path.splitext(task_name)
            solution_location = os.path.join(solution_dir, task_split[0] + file_suffix + task_split[1])

            if not os.path.isfile(solution_location):
                # print(f"Solution for {task_name} missing!")
                # print(f"Please add {solution_location}!")
                cprint(f"Solution for {task_name} missing!", "red")
                cprint(f"Please add {solution_location}!", "red")
                exit()

            tasks.append((task_location, solution_location))
        # print(f"{task_count} tasks found in {os.path.basename(task_dir)}")
        cprint(f"{task_count} tasks found in {os.path.basename(task_dir)}", "green")


def load_progress(p_file):
    global tasks
    global done_tasks
    global history

    with open(p_file, "r") as f:
        progress = json.load(f)

    index = progress["index"]
    tasks = progress["tasks"]
    done_tasks = progress["done_tasks"]
    history = progress["history"]

    cprint(f"Loaded Progress successfully!", "green")
    cprint(f"{len(tasks)} Tasks to do", "green")
    cprint(f"{len(done_tasks)} Tasks done", "green")
    cprint(f"{len(history)} entries in history", "green")
    cprint(f"Index is {index}", "green")

    return index


def save_progress(index):
    global tasks
    global done_tasks
    global progress_file
    global history

    progress = {
        "index": index,
        "tasks": tasks,
        "done_tasks": done_tasks,
        "history": history
    }

    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=1)


def show_file(file):
    img_program = config[GENERAL_CONFIG_KEY][IMG_PROGRAM_KEY]
    # file = file.replace(' ', '\ ')

    # print(img_program, file)
    # TODO: Fix command injection vulnerability
    proc = subprocess.Popen(f'{img_program} "{file}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return proc


def close_file(process):
    process.kill()


def switch_task(index=None, task_process=None, solution_process=None, keyboard_mode=False):
    # close current tasks
    if task_process:
        close_file(task_process)

    # close current solutions
    if solution_process:
        close_file(solution_process)

    if index != None:
        interactive_menu(index, keyboard_mode)
    else:
        exit()


def interactive_menu(index=0, keyboard_mode = False):
    """
    e -> exit
    n -> next
    p -> previous
    s -> show solution
    c -> jump to current
    k -> keyboard mode
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

    # save progress
    save_progress(index)

    # display task
    total_task_count = len(tasks) + len(done_tasks)
    progress = int((len(done_tasks) / total_task_count) * 100)
    progress = " " * (3 - len(str(progress))) + str(progress)
    current_task = " " * (len(str(total_task_count)) - len(str(index + 1))) + str(index + 1)
    cprint(f"Question number {current_task} of {total_task_count} | {progress}% done", "black", "on_white")
    task_file = history[index][0]
    # print("Task" + task_file)
    task_process = show_file(task_file)

    while True:
        if keyboard_mode:
            keyboard.wait("alt gr")
            keys = keyboard.record("alt gr", trigger_on_release=True)
            command = list(filter(lambda x: x != "alt gr", [key.name for key in keys]))[0]
        else:
            command = input(colored("Command: ", "blue", attrs=["bold"]))

        if command in ["e", "exit"]:
            if keyboard_mode:
                keyboard_mode = False
                print("Exiting keyboard mode!")
            else:
                print("Bye!")
                index = None
            break
        if command in ["n", "next"]:
            index += 1
            break
        if command in ["p", "previous"]:
            if index - 1 < 0:
                print("No previous task!")
            else:
                index -= 1
                break
        if command in ["c", "current"]:
            index = len(history) - 1
            break

        if command in ["k", "keyboard"]:
            print("Entering keyboard mode!")
            keyboard_mode = True

        if command in ["s", "solution"]:
            solution_file = history[index][1]
            # close current solution
            if solution_process:
                close_file(solution_process)

            # open new solution
            solution_process = show_file(solution_file)
            # print("Solution: " + solution_file)

        # chase with no matching command
        print("No matching command!")
    switch_task(index=index, task_process=task_process, solution_process=solution_process, keyboard_mode=keyboard_mode)


def main():
    global config
    global progress_file

    config = read_config()
    progress_file = config[GENERAL_CONFIG_KEY][PROGRESS_FILE_KEY]

    index = 0

    if os.path.isfile(progress_file):
        index = load_progress(progress_file)
    else:
        load_tasks(config)

    print()
    print("Control handed over to user now:")
    interactive_menu(index)


if __name__ == "__main__":
    main()
