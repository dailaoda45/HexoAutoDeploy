import sys
from PyQt6.QtWidgets import QApplication,QWidget,QFileDialog,QGridLayout,QPushButton,QLabel,QListWidget,QMessageBox,QVBoxLayout
from mainForm import Ui_MainForm
from PyQt6 import uic
import setting
from PyQt6.QtCore import QTimer,QThread, QWaitCondition, QMutex, QMutexLocker,QObject,pyqtSignal,Qt
from pathlib import Path
import paramiko
import os
# 部署线程
class deployThread(QObject):
    finish_signal=pyqtSignal()
    def __init__(self):
        super(deployThread, self).__init__()
        self.status = True

    def run(self):
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
        self.finish_signal.emit()

    # 备份线程
class backupThread(QObject):
    finish_signal = pyqtSignal()

    def __init__(self):
        super(backupThread, self).__init__()
        self.status = True
    def run(self):
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
        self.finish_signal.emit()

class info(QWidget):
    def __init__(self,  labeltext,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(50, 50, 50, 50)
        self.labeltext=labeltext
        self.setWindowTitle('提示信息')
        # create a QLabel widget
        label = QLabel(f'{self.labeltext}')
        # place the widget on the window
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        # 禁用按钮
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)
        # 居中显示
        self.center()
        # show the window
        self.show()
    def center(self):  # 将窗口居中的代码写入自定义的center方法中
        qr = self.frameGeometry()  # 得到一个指定主窗口几何形状的矩形
        cp = self.screen().availableGeometry().center()  # 计算出显示器的分辨率，通过分辨率得出中心点
        qr.moveCenter(cp)  # 设置为屏幕的中心，矩形大小不变
        self.move(qr.topLeft())

class window(QWidget):
    def __init__(self):
        super().__init__()
        # use the Ui_login_form
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)
        # 设置备份、变量
        self.backup_status = False
        self.deploy_status = False

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
        # 多线程
        # 部署线程
        self.thread = QThread()
        # 实例化线程类
        self.deploy_Thread = deployThread()
        #moveToThread方法把实例化线程移到Thread管理
        self.deploy_Thread.moveToThread(self.thread)
        # 线程开始执行之前，从相关线程发射信号
        self.thread.started.connect(self.deploy_Thread.run)
        #接收子线程信号发来的数据
        # self.deploy_Thread.to_show_img_signal.connect(self.show_img_in_labelme)
        # 线程执行完成关闭线程
        # self.thread.finished.connect(self.threadStop)
        # 消息线程
        self.threadinfo = QThread()
        # 备份线程
        self.backupthread = QThread()
        # 实例化线程类
        self.backup_Thread = backupThread()
        #moveToThread方法把实例化线程移到Thread管理
        self.backup_Thread.moveToThread(self.backupthread)
        # 线程开始执行之前，从相关线程发射信号
        self.backupthread.started.connect(self.backup_Thread.run)




    def upload(self):
        upload_list_path = []
        list_text=''
        # 获取upload_list中条目数
        count = self.ui.upload_list.count()
        if count > 0:
        # 遍历upload_list中的内容放入列表
            for i in range(count):
                upload_list_path.append(self.ui.upload_list.item(i).text())
        # 条目内容放到文本中
                list_text=list_text+os.path.basename(self.ui.upload_list.item(i).text())+'\n'
        # 提示窗确认是否上传
            answer = QMessageBox.question(self,'确认上传内容',f'确认上传以下文档吗？\n{list_text}',QMessageBox.StandardButton.Yes |QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                # 使用sftp上传文件
                t = paramiko.Transport(setting.host, 22)
                t.banner_timeout = setting.timeout
                t.connect(username=setting.user, password=setting.password)
                sftp = paramiko.SFTPClient.from_transport(t)
                # 这里注意需要是两个完整的带文件名称的路径否则会报错
                for file_path in upload_list_path:
                    print(os.path.join(setting.server_path,os.path.basename(file_path)))
                    sftp.put(file_path,os.path.join(setting.server_path,os.path.basename(file_path)))
                t.close()
                QMessageBox.information(self, '信息', '上传完成！', QMessageBox.StandardButton.Ok)
            # 获取清单
                self.getlist()
            # else:
            #     QMessageBox.information(self,'信息','你取消了上传！',QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(self,'警告！','请先选择需要上传的文件。')

    def deploy(self):
        print('deploy')
        if self.deploy_status == True:
            QMessageBox.warning(self, '警告！', '上一次的部署任务还没有执行完成，请等待上分任务执行完成了再进行下次部署。')
        else:
            answer = QMessageBox.question(self, '确认是否部署', '确认开始部署吗？',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.deploy_status = True
                # 开启子线程
                self.thread.start()
                # 实例化info线程类
                self.deployinfo = info('正在部署中！请稍等…………')
                # moveToThread方法把实例化线程移到Thread管理
                self.deployinfo.moveToThread(self.threadinfo)
                self.threadinfo.start()
                # QMessageBox.information(self, '信息', '正在部署中！请稍等…………', QMessageBox.StandardButton.NoButton)
                # 退出子线程
                self.deploy_Thread.finish_signal.connect(self.deploy_Thread_finished)

    # 执行完成
    def deploy_Thread_finished(self):
        self.thread.quit()
        self.deployinfo.close()
        self.threadinfo.quit()
        QMessageBox.information(self, '信息', '部署完成！', QMessageBox.StandardButton.Ok)
        self.deploy_status = False


    def backup(self):
        # print('backup')
        if self.backup_status == True:
            QMessageBox.warning(self, '警告！', '上一次的备份任务还没有执行完成，请等待上分任务执行完成了再进行下次备份。')
        else:
            answer = QMessageBox.question(self, '确认是否备份', '确认开始备份吗？',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                # 开启子线程
                self.backup_status = True
                self.backupthread.start()
                # 实例化info线程类
                self.backupinfo = info('正在备份中！请稍等…………')
                # moveToThread方法把实例化线程移到Thread管理
                self.deployinfo.moveToThread(self.threadinfo)
                self.threadinfo.start()
                # QMessageBox.information(self, '信息', '正在部署中！请稍等…………', QMessageBox.StandardButton.NoButton)
                # 退出子线程
                self.backup_Thread.finish_signal.connect(self.backup_Thread_finished)


    def backup_Thread_finished(self):
        self.backupthread.quit()
        self.backupinfo.close()
        self.threadinfo.quit()
        QMessageBox.information(self, '信息', '备份完成！', QMessageBox.StandardButton.Ok)
        self.backup_status = False

    def browse(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "请选择要上传的md文件",r"C:\Users\SS\Desktop","Markdown (*.md)"
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
        # print('deletefile')
    #     获取文件名使用ssh rm删除同时移除文件
        # 获取当前行
        current_row = self.ui.server_file_list.currentRow()
        if current_row >= 0:
            # 获取当前行文本值也就是文件名
            serverfilename = self.ui.server_file_list.item(current_row).text()
            answer = QMessageBox.question(self, '确认是否删除', f'确认删除{serverfilename}吗？',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
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
            #     current_item = self.ui.server_file_list.takeItem(current_row)
                # del current_item
                # 更新清单内容
                self.getlist()
                QMessageBox.information(self, '信息', f'成功删除文件《{serverfilename}》！')

        else:
            # self.ui.label.setText('服务器上文件清单：数量为0请先获取清单')
            QMessageBox.warning(self, '警告！', '请先获取清单！')

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
        QMessageBox.information(self, '信息', '下载完成！')


# 生成配置文件

# 加密配置文件

# 读取配置文件



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = window()
    sys.exit(app.exec())