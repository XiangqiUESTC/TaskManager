import yaml
import subprocess
import sys
import time
import logging
import os

################################################################ 配置日志
logger = logging.getLogger("task_manage")
logger.handlers = []
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(name)s %(message)s', '%H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel('INFO')
################################################################ 配置日志

def run_task(task, gpu_id=None):
    logger = logging.getLogger("task_manage")
    # 获取任务的命令
    command = task["command"]
    logger.info(f"启动任务: {command}")
    # 获取任务标准输出的重定向文件
    output = task["output"]
    logger.info(f"任务日志将保存在:{output}")
    # 执行任务
    command = command.split()
    command = [sys.executable, "-W", "ignore"] + command[1:]

    env = os.environ.copy()  # 复制当前环境
    env["CUDA_VISIBLE_DEVICES"] = gpu_id  # 只修改需要的环境变量

    # 返回任务控制
    return subprocess.Popen(command
                   , stdout=open(output, "w")
                   , env=env
                   , bufsize=0
                   , stderr=subprocess.STDOUT  # 将 stderr 也重定向到 stdout
                   )


def print_current_tasks(task_threads):
    logger = logging.getLogger("task_manage")
    task_infos = ""
    for i,thread in enumerate(task_threads):
        task_infos += f"\t任务{i} [{thread['popen'].pid}]: {thread['task']['command']} &> {thread['task']['output']}\n"

    logger.info(f"当前进程池任务状态:\n{task_infos}")


if __name__ == "__main__":
    logger = logging.getLogger("task_manage")
    ################################################################ 检查是否需要等待其他进程
    # 检查是否有第四个参数，如果有则表示需要等待的PID列表
    if len(sys.argv) > 4:
        pid_to_wait_str = sys.argv[4]
        if pid_to_wait_str.strip():  # 如果不是空字符串
            pid_list = [pid.strip() for pid in pid_to_wait_str.split(',') if pid.strip()]

            if pid_list:
                logger.info(f"开始等待以下PID进程完成: {pid_list}")

                # 简单轮询检查进程是否结束
                all_done = False
                while not all_done:
                    all_done = True
                    remaining_pids = []

                    for pid in pid_list:
                        try:
                            # 检查进程是否存在
                            os.kill(int(pid), 0)
                            # 如果没抛出异常，说明进程还在运行
                            remaining_pids.append(pid)
                            all_done = False
                        except (OSError, ValueError) as e:
                            # 进程不存在或无效PID
                            if isinstance(e, OSError) and e.errno == 3:  # ESRCH: No such process
                                logger.info(f"PID {pid} 已结束")
                            # 其他情况（如权限问题）也认为进程不存在
                            continue

                    pid_list = remaining_pids

                    if not all_done:
                        time.sleep(10)  # 等待10秒再检查
                    else:
                        logger.info("所有等待的进程都已结束，开始执行新任务")
    ################################################################ 检查是否需要等待其他进程

    ################################################################ 读取命令行参数和yaml
    # 获取yaml配置文件路径
    yaml_path = sys.argv[1]
    # 获取命令行参数——线程数
    threads_num = sys.argv[2]
    # 获取GPU id
    gpu_id = sys.argv[3]
    # 获取任务配置文件
    with open(yaml_path, "r") as f:
        tasks = yaml.safe_load(f)
    ################################################################ 读取命令行参数和yaml

    ################################################################ 初始化进程池
    logger.info(f"启动任务中！总线程数:{threads_num}", )
    # 默认未运行完
    flag = True
    # 先默认启动 threads_num 个任务
    task_threads = []
    task_idx = 0
    for _ in range(int(threads_num)):
        if task_idx < len(tasks):
            popen = run_task(tasks[task_idx], gpu_id)

            thread = {
                "popen": popen,
                "task": tasks[task_idx]
            }

            task_threads.append(thread)
            time.sleep(1)
        task_idx += 1
    ################################################################ 初始化进程池

    ################################################################ 轮询所有任务，直到所有任务都提交
    done_num = 0
    while True:
        time.sleep(1)
        # 如果所有任务都提交了，跳出循环
        if task_idx < len(tasks):
            # 轮询进程池，检查是否有运行完的任务，如果有就启动新的任务
            for i in range(int(threads_num)):
                popen = task_threads[i]["popen"]
                command = task_threads[i]["task"]["command"]
                output = task_threads[i]["task"]["output"]
                # 进程是否结束的条件判断
                if popen.poll() is not None:
                    logger.info(f"任务{command} &> {output}完成!将启动新任务!")
                    done_num += 1
                    logger.info(f"已经完成{done_num}个任务！")
                    popen = run_task(tasks[task_idx], gpu_id)

                    task_threads[i] = {
                        "popen": popen,
                        "task": tasks[task_idx]
                    }
                    task_idx += 1
                    print_current_tasks(task_threads)
                    # break掉，继续下一轮轮询，防止task_idx越界
                    break
                else:
                    continue
        else:
            break
    ################################################################ 轮询所有任务，直到所有任务都提交

    ################################################################ 等待所有任务运行完
    for task in task_threads:
        task["popen"].wait()
        done_num += 1
        logger.info(f"已经完成{done_num}个任务！")
    logger.info("所有任务运行完毕！")
    ################################################################ 等待所有任务运行完