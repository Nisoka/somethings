# Install the ubuntuCore 
    https://developer.ubuntu.com/core/get-started/intel-nuc
    0 create a ubuntu one account, and add a sshKey on it, 
        this account will be use to the ubuntu core system user, and the only user        
    1 just create a ubuntu core image usb media.
        https://developer.ubuntu.com/core/get-started/installation-medias
        1 umount /dev/sdb1
        2 xzcat ~/Downloads/<image file .xz> | sudo dd of=<drive address> bs=32M
        3 sync
        4 eject the usb      
    2 insert the usb to a device     
    3 first boot the device 
        The system will boot then become ready to configure
        The device will display the prompt “Press enter to configure”
        Press enter then select “Start” to begin configuring your network and an administrator account. Follow the instructions on the screen, you will be asked to configure your network and enter your Ubuntu SSO credentials
        At the end of the process, you will see your credentials to access your Ubuntu Core machine:
        This device is registered to <Ubuntu SSO email address>.
        Remote access was enabled via authentication with the SSO user <Ubuntu SSO user name>
        Public SSH keys were added to the device for remote access.
    4 user login:
        ssh <Ubuntu SSO user name>@<device IP address>
        you can use this command to add a local login passwd, then you can dorp the netline, just as a normal computer.
        sudo passwd <account name>
        
        
# Install and develop snaps
    after install the ubuntu core, this system only can be use snap, but this is not the good choice
    You can install a classic Ubuntu environment on top of Ubuntu Core to have a fully-fledged development environment and develop snaps on target ›
    then you have a classic Ubuntu environment to use. 
    https://developer.ubuntu.com/core/get-started/developer-setup
    snap install classic --edge --devmode
    sudo classic
    sudo apt update
    sudo apt install snapcraft build-essential git
    
    
    

