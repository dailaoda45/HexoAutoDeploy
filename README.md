# HexoAutoDeploy
这是使用python+pyqt6简单实现的一个自动一键上传.md文件到服务器并部署hexo博客并备份到github私人仓库的简单图形界面。

![](demo.png)

使用方式，

！！！！首先配置好setting文件中的md文件路径。主机账号密码。例如：

```
# 主机账号密码
host = '8.8.8.8'
user = 'root'
password = 'xxxxxx'
# 超时响应时间
timeout = 10

# 服务器目标路径
server_path = r'/opt/blog/hexoblog/source/_posts/'
```

1.点击浏览本地文件选择需要上传的md文件

2.第一步选错文件了。可点击按钮移除

3.点击一键上传，等待上传完成

4.点击一键部署会自动在目标文件夹下运行liunx脚本autodeploy需要提前在setting中配置好博客路径

5.点击一键备份一键运行liunx脚本autobackup。同样需要在settingpy中配置好博客路径ssh主机账号密码端口等。

6.点击获取可以获取hexo存放md文件的路径下的所有文件名称。

7.点击下载可以下载md文件

8.点击删除可以删除服务器中的md文件。重新点击一键部署后可以生成新的页面。

使用pyqt6的QTdesigner生成UI然后转换成py文件作为GUI，具体情况参考PyQt6教程

[](https://www.pythontutorial.net/pyqt/pyqt-hello-world/)

然后使用paramiko模块使用ssh命令获取文档列表。以及删除文档操作。

在目标位置有使用liunx命令建立脚本结合python的paramiko模块使用ssh命令以实现一键部署，一键备份。这个备份我是将服务器上的hexo博客文件上传到是有仓库实现。



2024年7月13日搞了一个通宵，才搞定多线程怎么弄。

完成备份任务，部署任务多线程运行。

完成部署，备份，删除交互提醒窗口。

接下来准备完成菜单命令自由配置化。


2024年7月14日

更新设置界面，并对配置好的服务器内容进行存储。

使用cryptography包aes对配置文件进行加密。

优化了下载没有选择文件夹的提示。

---

基本这个样子可以用了。
