import smtplib, ssl
import requests
import time
import threading


class SiteMonitor(threading.Thread):
    """
    SENDS GET REQUEST TO URL EVERY X MINUTES BASED ON 'check_interval'
    IF CONTENT OF PAGE HAS CHANGED, SEND SMS VIA CLICKSENDS SMS API
    """
    def __init__(
        self,
        url,
        check_interval,
        clicksend_sms_username,
        clicksend_sms_api_key,
        sender_name,
        mobile_number,
        recipient_email_address,
        smtp_username,
        smtp_password,
        smtp_server,
        smtp_port):
        threading.Thread.__init__(self)
        
        """
        VALIDATE INPUTS
        """
        if type(url) != str:
            raise TypeError("url must be a string")
        elif type(check_interval) != int:
            raise TypeError("check_interval must be an integer")
        elif type(clicksend_sms_username) != str:
            raise TypeError("api_key must be a string")
        elif type(clicksend_sms_api_key) != str:
            raise TypeError("api_secret must be a string")
        elif type(mobile_number) != str:
            raise TypeError("mobile_number must be a string and formatted as: '07000000000'")
        elif type(sender_name) != str:
            raise TypeError("sender_name must be a string")
        elif type(recipient_email_address) != str:
            raise TypeError("email_address must be a string")
        elif type(smtp_username) != str:
            raise TypeError("smtp_username must be a string")
        elif type(smtp_password) != str:
            raise TypeError("smtp_password must be a string")
        elif type(smtp_server) != str:
            raise TypeError("smtp_server must be a string")
        elif type(smtp_port) != int:
            raise TypeError("smtp_port must be an integer")
        
        """
        SET ATTRIBUTES
        """
        self.url                     = url
        self.check_interval          = check_interval * 60 #Seconds to Minutes
        self.clicksend_sms_username  = clicksend_sms_username
        self.clicksend_sms_api_key   = clicksend_sms_api_key
        self.sender_name             = sender_name
        self.mobile_number           = mobile_number
        self.recipient_email_address = recipient_email_address
        self.smtp_username           = smtp_username
        self.smtp_password           = smtp_password
        self.smtp_server             = smtp_server
        self.smtp_port               = smtp_port
        
        self.clicksend_sms_url      = "https://rest.clicksend.com/v3/sms/send"
        
        print(f"[+] Monitoring {self.url} every {check_interval} minutes")
    
    def run(self):
        """
        REPEATEDLY GET THE PAGE BODY AND SEND SMS IF CONTENT HAS CHANGED
        """
        body = self.get_url_body()
        time.sleep(self.check_interval)
        while True:
            new_body = self.get_url_body()
            if body != new_body and new_body != "":
                print(f"[+] Changes detected on {self.url}")
                message = f"Changes have been detected on {self.url}"
                self.send_sms(message)
                self.send_email(message)
                time.sleep(600) #10 MINUTE COOLDOWN
            body = new_body
            time.sleep(self.check_interval)
    
    def get_url_body(self) -> str:
        """
        SENDS GET REQUEST AND RETURNS BODY IF RESPONSE IS 200
        """
        r = requests.get(self.url)
        print(f"[+] GET: {self.url}")
        if r.status_code == 200:
            return r.text
        return ""
    
    def send_sms(self, message):
        """
        SENDS SMS VIA CLICKSENDS SMS API
        INCLUDES URL AND DATETIME OF CHANGE
        """
        message = {
            "messages":[
                {
                "body": message,
                "to":   self.mobile_number,
                "from": self.sender_name
                }
            ]
        } 
        r = requests.post(self.clicksend_sms_url, auth=(self.clicksend_sms_username, self.clicksend_sms_api_key), json=message)
        if r.status_code == 200:
            print(f"[+] SMS sent to {self.mobile_number}")
        else:
            print(f"[-] SMS failed to send to {self.mobile_number}")
    
    def send_email(self, message):
        try:
            context = ssl.create_default_context()
            body = 'Subject: {}\n\n{}'.format(self.sender_name, message)
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, self.recipient_email_address, body)
                server.quit()
            print(f"[+] Email sent to {self.recipient_email_address}")
        except:
            print(f"[-] Email failed to send to {self.recipient_email_address}")


if __name__ == "__main__":
    """ASSEMBLE URL LIST TO BE CHECKED"""
    with open("urls.txt", "r") as f:
        urls = []
        [urls.append(line.strip().replace("\n", "")) for line in f.readlines()]
    
    """ASSEMBLE ALL PARAMETERS"""
    with open("config.txt", "r") as f:
        for line in f:
            if line.startswith("check_interval"):
                check_interval = int(line.split("=")[1].strip())
            elif line.startswith("clicksend_sms_username"):
                clicksend_sms_username = line.split("=")[1].strip()
            elif line.startswith("clicksend_sms_api_key"):
                clicksend_sms_api_key = line.split("=")[1].strip()
            elif line.startswith("mobile_number"):
                mobile_number = line.split("=")[1].strip()
            elif line.startswith("sender_name"):
                sender_name = line.split("=")[1].strip()
            elif line.startswith("recipient_email_address"):
                recipient_email_address = line.split("=")[1].strip()
            elif line.startswith("smtp_username"):
                smtp_username = line.split("=")[1].strip()
            elif line.startswith("smtp_password"):
                smtp_password = line.split("=")[1].strip()
            elif line.startswith("smtp_server"):
                smtp_server = line.split("=")[1].strip()
            elif line.startswith("smtp_port"):
                smtp_port = int(line.split("=")[1].strip())
    
    for url in urls:
        sm = SiteMonitor(
            url,
            check_interval,
            clicksend_sms_username,
            clicksend_sms_api_key,
            sender_name,
            mobile_number,
            recipient_email_address,
            smtp_username,
            smtp_password,
            smtp_server,
            smtp_port
        )
        sm.start()
        time.sleep(2)
    
    print("[+] All sites being monitored")