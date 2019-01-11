# 系统构建过程
1 写入系统镜像
    dd if=NUC_UBUNTU_SERVER.image of=/dev/sdn
2 系统镜像恢复(可能通过dd 命令写入的镜像有些问题)
    1 sudo fsck /dev/sda1 (一路yes)
    2 sudo reboot
    3 fsck /dev/sda1 (出现恢复不成功, 需要在重启的initframs 中继续恢复)
    4 reboot 
    5 git clone Innovem@192.169.18.100:liujunnan.git git-nan
    6 cp src.tar tools.tar --> git-nan/code/kaldi-master , tar xvf ..
    7 sudo pip3 install numpy, numexpr, pandas, scipy, scikit-learn
    8 sudo apt-get install scipy

# 识别系统运行(手动)
1 cd ~/git-nan/code/langRecSys/
2 ./runSystem.sh

# 自启动脚本配置
1 sudo vim /etc/rc.local
2 write:
    1 ifconfig eno1 192.168.44.2n (.44 网段, 是固定的 完整识别系统是.44网段)
    2 sleep 1
    3 /home/liujunnan/git-nan/code/langRecSys/runSystem.sh &
