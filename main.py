import sys
from PyQt6.QtWidgets import QApplication,QWidget,QFileDialog,QGridLayout,QPushButton,QLabel,QListWidget
from mainForm import Ui_MainForm
from PyQt6 import uic
import setting
from pathlib import Path
import paramiko
import os


class window(QWidget):
    def __init__(self):
        super().__init__()
        # use the Ui_login_form
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)

        # show the login window
        self.show()
        # authenticate when the login button is clicked
        self.ui.browseButton.clicked.connect(self.browse)
        self.ui.uploadButton.clicked.connect(self.upload)
        self.ui.deployButton.clicked.connect(self.deploy)
        self.ui.backupButton.clicked.connect(self.backup)
        self.ui.removeButton.clicked.connect(self.remove)
        self.ui.getlistButton.clicked.connect(self.getlist)
        self.ui.deleteButton.clicked.connect(self.deletefile)
        self.ui.downloadButton.clicked.connect(self.downloadfile)

    def upload(self):
        upload_list_path = []
        # 获取upload_list中条目数
        count = self.ui.upload_list.count()
        # 遍历upload_list中的内容
        for i in range(count):
            upload_list_path.append(self.ui.upload_list.item(i).text())
        t = paramiko.Transport(setting.host, 22)
        t.banner_timeout = setting.timeout
        t.connect(username=setting.user, password=setting.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        # 这里注意需要是两个完整的带文件名称的路径否则会报错
        for file_path in upload_list_path:
            print(os.path.join(setting.server_path,os.path.basename(file_path)))
            sftp.put(file_path,os.path.join(setting.server_path,os.path.basename(file_path)))
        t.close()

    def deploy(self):
        print('deploy')
        result = {'status': 1, 'data': None}  # 返回结果
        # 服务器上脚本
        cmd = '/opt/blog/hexoblog/autodeploy.sh'
        ssh = paramiko.SSHClient()  # 创建一个新的SSHClient实例
        ssh.banner_timeout = setting.timeout
        # 设置host key,如果在"known_hosts"中没有保存相关的信息, SSHClient 默认行为是拒绝连接, 会提示yes/no
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(setting.host, 22, setting.user, setting.password, timeout=setting.timeout)  # 连接远程服务器,超时时间1秒
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=setting.timeout)  # 执行命令
        out = stdout.readlines()  # 执行结果,readlines会返回列表
        # 执行状态,0表示成功，1表示失败
        channel = stdout.channel
        status = channel.recv_exit_status()
        ssh.close()  # 关闭ssh连接
        # 修改返回结果
        result['status'] = status
        result['data'] = out
        print(result)
        print('执行完成')

    def backup(self):
        print('backup')
        result = {'status': 1, 'data': None}  # 返回结果
        # 服务器上脚本
        cmd = '/opt/blog/hexoblog/autobackup.sh'
        ssh = paramiko.SSHClient()  # 创建一个新的SSHClient实例
        ssh.banner_timeout = setting.timeout
        # 设置host key,如果在"known_hosts"中没有保存相关的信息, SSHClient 默认行为是拒绝连接, 会提示yes/no
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(setting.host, 22, setting.user, setting.password, timeout=setting.timeout)  # 连接远程服务器,超时时间1秒
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=setting.timeout)  # 执行命令
        out = stdout.readlines()  # 执行结果,readlines会返回列表
        # 执行状态,0表示成功，1表示失败
        channel = stdout.channel
        status = channel.recv_exit_status()
        ssh.close()  # 关闭ssh连接
        # 修改返回结果
        result['status'] = status
        result['data'] = out
        print(result)
        print('执行完成')

    def browse(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要上传的md文件",r"C:\Users\SS\Desktop","Markdown (*.md)"
        )
        if filenames:
            self.ui.upload_list.addItems([str(Path(filename)) for filename in filenames])

    def remove(self):
        current_row = self.ui.upload_list.currentRow()
        if current_row >= 0:
            current_item = self.ui.upload_list.takeItem(current_row)
            del current_item



    def getlist(self):
        print('gitlist')
        cmd = 'cd /opt/blog/hexoblog/source/_posts && ls -1'
        ssh = paramiko.SSHClient()  # 创建一个新的SSHClient实例
        ssh.banner_timeout = setting.timeout
        # 设置host key,如果在"known_hosts"中没有保存相关的信息, SSHClient 默认行为是拒绝连接, 会提示yes/no
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(setting.host, 22, setting.user, setting.password, timeout=setting.timeout)  # 连接远程服务器,超时时间1秒
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=setting.timeout)  # 执行命令
        out = stdout.readlines()  # 执行结果,readlines会返回列表
        # 执行状态,0表示成功，1表示失败
        channel = stdout.channel
        status = channel.recv_exit_status()
        ssh.close()  # 关闭ssh连接
        # 修改返回结果
        sever_file_list = out
        # 除掉换行符
        i = 0
        for filename in sever_file_list:
            sever_file_list[i] = (str.strip(filename))
            i = i+1
        print('执行完成')
    #     先清空避免重复
        self.ui.server_file_list.clear()
        self.ui.label.setText('服务器上文件清单：')
    #     将获取结果填入listwidget格子server_file_list
        self.ui.server_file_list.addItems([str(filename) for filename in sever_file_list])
    #     修改文本统计数量
        num = len(sever_file_list)
        self.ui.label.setText(f'服务器上文件清单：数量为{num}')

    def deletefile(self):
        print('deletefile')
    #     获取文件名使用ssh rm删除同时移除文件
        # 获取当前行
        current_row = self.ui.server_file_list.currentRow()
        if current_row >= 0:
            # 获取当前行文本值也就是文件名
            serverfilename = self.ui.server_file_list.item(current_row).text()
            # 拼接命令路径
            cmd = 'rm -rf '+os.path.join(setting.server_path,serverfilename)
            result = {'status': 1, 'data': None}  # 返回结果
            ssh = paramiko.SSHClient()  # 创建一个新的SSHClient实例
            ssh.banner_timeout = setting.timeout
            # 设置host key,如果在"known_hosts"中没有保存相关的信息, SSHClient 默认行为是拒绝连接, 会提示yes/no
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(setting.host, 22, setting.user, setting.password, timeout=setting.timeout)  # 连接远程服务器,超时时间1秒
            stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=setting.timeout)  # 执行命令
            out = stdout.readlines()  # 执行结果,readlines会返回列表
            # 执行状态,0表示成功，1表示失败
            channel = stdout.channel
            status = channel.recv_exit_status()
            ssh.close()  # 关闭ssh连接

            # 修改返回结果
            result['status'] = status
            result['data'] = out
            print(result)
        #     同时移除listwidget清单
            current_item = self.ui.server_file_list.takeItem(current_row)
            del current_item
        else:
            self.ui.label.setText('服务器上文件清单：数量为0请先获取清单')

    def downloadfile(self):
        print('downloadfile')
        # 获取当前行
        current_row = self.ui.server_file_list.currentRow()
        if current_row >= 0:
            # 获取当前行文本值也就是文件名
            serverfilename = self.ui.server_file_list.item(current_row).text()
            print(serverfilename)
            dir_name = QFileDialog.getExistingDirectory(self, "选择下载位置")
            local_path = Path(dir_name)
            print(local_path)
        else:
            self.ui.label.setText('服务器上文件清单：数量为0请先获取清单')
        t = paramiko.Transport(setting.host,22)
        t.banner_timeout = setting.timeout
        t.connect(username=setting.user,password=setting.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        # 统一路径为/
        sftp.get(os.path.join(setting.server_path,serverfilename),os.path.join(local_path,serverfilename).replace('\\','/'))
        t.close()
        print('执行完成')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = window()
    sys.exit(app.exec())