import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from pyBase import config_action


# 获得收件人列表
receivers_auc_list = config_action.ConfigAction('PARAMETER.ini').get('email_receivers')
receivers_list = [i[1] for i in receivers_auc_list]
print(receivers_list)


def send_email(report_html, description):
    """ 发送邮件 """

    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "1808503589@qq.com"  # 用户名
    mail_pass = "dkqmjpusoubycbch"   # 口令

    # 设置收件人和发件人
    sender = '1808503589@qq.com'
    receivers = receivers_list                 # 接收邮件

    # 创建一个带附件的实例对象
    message = MIMEMultipart()

    # 邮件主题、收件人、发件人
    subject = '请查阅_'+description+'_测试报告'  # 邮件主题
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = Header("{}".format(sender), 'utf-8')  # 发件人
    message['To'] = Header("{}".format(';'.join(receivers)), 'utf-8')  # 收件人

    # 邮件正文内容 html 形式邮件
    send_content = report_html  # 获取测试报告
    html = MIMEText(_text=send_content, _subtype='html', _charset='utf-8')  # 第一个参数为邮件内容

    # 构造附件
    att = MIMEText(_text=send_content, _subtype='base64', _charset='utf-8')
    att["Content-Type"] = 'application/octet-stream'
    file_name = 'result.html'
    att["Content-Disposition"] = 'attachment; filename="{}"'.format(file_name)  # # filename 为邮件附件中显示什么名字
    message.attach(html)
    message.attach(att)

    try:
        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, receivers, message.as_string())
        smtp_obj.quit()
        print("邮件发送成功")

    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件")
        print(e)


if __name__ == "__main__":

    def report():
        file_path = r'F:\PycharmProjects\TD_sip\report\2020-08-20 16_13_45IM-API自动化测试报告_TestReport.html'
        f1 = open(file_path, 'r', encoding='utf-8')
        res = f1.read()
        f1.close()
        return res
    send_email(report(), '呼叫压测77')