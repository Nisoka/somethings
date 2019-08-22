

1 直接pyinstaller project.py 很简单的情况下用这个

2   1 pyi-makespec   project.py  生成 project.spec
    2 pyinstaller   project.spec 
    Note:
    1 project.spec 是 pyi 配置文件, 会引用所需的基本库等等, 
    1 不会自动引用 动态环境变量(sys.path 增加的python模块)
    需要在 project.spec 的 pathex = ['path1', 'path2'] 中增加 sys.path.append 的引用
    2 有些模块没有引用 No that module
    需要在 project.spec 的 hiddenimports=['module1', ''module2'] 中进行增加
