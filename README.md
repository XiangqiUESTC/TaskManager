# TaskManager介绍
当你有大量AI实验要跑时，为了节约时间，你会希望一组实验跑完之后立马跑下一组，但是没有人愿意起早贪黑地一直用nvidia-smi和看日志输出来时刻盯着所有进程，
TaskManager提供了一个轻量的python脚本和简易的yaml配置，你可以通过
# 一、使用方法
1. 配置一个yaml文件，参考MMM2.yaml中的格式，假设你配置的yaml文件是xxx.yaml
2. 将task_manager.py和xxx.yaml放到项目根目录中，例如pymarl/task_manager.py和pymarl/xxx.yaml
3. 运行nohup python task_manager.py \[线程数\] \[显卡卡号\] \[任务yaml文件名\]


