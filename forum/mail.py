from email.mime.text import MIMEText
import smtplib

#for other use not for activate
#def sendMail(subject, body, html, to_addr):
def sendMail(subject, body, htmldf, to_addr):
    mime: object = MIMEText(htmldf, 'html', "utf-8")
    mime["Subject"] = subject
    mime["From"] = "PNforceStudio"
    mime["To"] = ""
    mime["Cc"] = ""
    msg = mime.as_string()
    smtpssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtpssl.login("patrick110413@gmail.com", "vbsqufevjocaxbkg")
    from_addr = "patrick110413@gmail.com"
    smtpssl.sendmail(from_addr, to_addr, msg, mail_options=(), rcpt_options=())
    smtpssl.quit()