# TaskManager介绍
当你有大量AI实验要跑时，为了节约时间，你会希望一组实验跑完之后立马跑下一组，但是没有人愿意起早贪黑地一直用nvidia-smi和看日志输出来时刻盯着所有进程，
TaskManager提供了一个轻量的python脚本和简易的yaml配置，你可以通过配置yaml并运行脚本来自动管理你的实验
# 一、使用方法
1. 配置一个yaml文件，参考MMM2-tasks.yaml中的格式，假设你配置的yaml文件就是MMM2-tasks.yaml
2. 将task_manager.py和MMM2-tasks.yaml放到项目根目录中，例如pymarl/task_manager.py和pymarl/MMM2-tasks.yaml
3. 假设你希望一次在显卡0上跑5组实验，直到跑完MMM2-tasks.yaml里面的所有命令，那么你可以运行：  
 **nohup python task_manager.py 5 0 MMM2-tasks.yaml &> MMM2-tasks_task.out&**  
4. 总结来说，使用命令    
**nohup python task_manager.py \[任务yaml文件名\] \[线程数\] \[显卡卡号\] \[要等待的进程PID1,\] &> \[日志文件\]&**
# 二、更新日志
1. TaskManger横空出世，帮助你自动化管理任务
2. 当你在一年的最后一天想下班过年之前，想要添加一组新任务，但是现在GPU跑满了另外一组任务，你不得不坐在实验室等任务结束，但是当前这组任务可能要等到半夜才结束，怎么高效地续跑任务呢，此次更新添加了第四个参数，即要等待的进程序列，你可以使用  
 **python task_manager.py task.yaml 3 0 32141,31891**  
来让程序在PID为32141和31891的程序结束之后再执行0卡上的由task.yaml指定的任务