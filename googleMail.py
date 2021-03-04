import email, smtplib, ssl
import os
import imaplib
import webbrowser
from email.header import decode_header
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def send_email():
    conn = sqlite3.connect('Un_objet/database.db')
    cursor = conn.cursor()
    address = cursor.execute("SELECT address from email_address")
    a = 0
    allAddress = []
    for addr in address:
        allAddress.append(addr[0])
        print(str(a) + ": " + addr[0])
        a += 1

    num = int(input("Quelle addresse voulez-vous utilisez ? "))
    my_email = allAddress[num]
    print(my_email)
    domain = my_email.split('@')
    domain = domain[1].split('.')
    print(domain[0])
    server = cursor.execute("SELECT smtp, port FROM server WHERE name = '" + domain[0] + "'")
    port = 0
    smtp_server = ""
    for smtp, port in server:
        port = port
        smtp_server = smtp
    subject = input("Entrez le sujet de votre mail : \n")
    body = input("Entrez le contenu de votre mail \n")
    receiver_email = input("A quelle adresse voulez-vous envoyer un mail ?")

    message = MIMEMultipart()  # Creation du mail
    message["From"] = my_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    a = input("Voulez vous envoyer des pieces jointes ? (OUI/NON)\n")
    a = a.lower()
    if (a == "oui"):
        filenames = input(
            "Mettez le file dans le meme dossier que le script \n Entrez le nom de fichier sans oublier les extensions ,\ns'il y en à plusieurs séparez les par des virgules\n")
        filenames = filenames.split(",")
        list_file = []
        for i in filenames:
            if (i.split() != ""):
                list_file.append(i)
        for file in list_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(file, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                            % os.path.basename(file))
            message.attach(part)

    text = message.as_string()

    password = input("Type your password and press enter:\n")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(my_email, password)
        server.sendmail(my_email, receiver_email, text)
    print("Merci d'avoir utilisé notre service le S")


def lire_email():
    print("Bienvenue dans la lecture de mail")
    conn = sqlite3.connect('Un_objet/database.db')
    cursor = conn.cursor()
    address = cursor.execute("SELECT address from email_address")
    a = 0
    allAddress = []
    for addr in address:
        allAddress.append(addr[0])
        print(str(a) + ": " + addr[0])
        a += 1

    num = int(input("Quelle addresse voulez-vous utilisez ? "))
    my_email = allAddress[num]
    print(my_email)
    domain = my_email.split('@')
    domain = domain[1].split('.')
    print(domain[0])
    server = cursor.execute("SELECT imap, port FROM server WHERE name = '" + domain[0] + "'")
    port = 0
    imap_server = ""
    for imap, port in server:
        port = port
        imap_server = imap
    password = input("Type your password and press enter:\n")
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(my_email, password)
    # we choose the inbox but you can select others
    status, messages = mail.select('inbox')
    messages = int(messages[0])
    print("Vous avez :" + str(messages) + " messages danbs votre boite mail ")
    N = int(input("Entrez le nombre de mail que vous voulez voir :\n"))

    if (N > messages):
        print("Vous ne pouvez pas lire autant de mails")


    else:
        for i in range(messages, messages - N, -1):
            # fetch the email message by ID
            res, msg = mail.fetch(str(i), "(RFC822)")

            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)

                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                                body = "From : " + From + "\n" + "Object : " + subject + "\n" + body
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                print(body)
                                save = input("Voulez vous enregistrer le mail ? (OUI/NON)")
                                save = save.lower()
                                if (save == "oui"):
                                    if content_type == "text/plain":
                                        # print only text email parts
                                        print("Enregistement\n")
                                        folder_name = clean(subject)
                                        if not os.path.isdir(folder_name):
                                            # make a folder for this email (named after the subject)
                                            os.mkdir(folder_name)
                                        filename = "mail.txt"
                                        filepath = os.path.join(folder_name, filename)
                                        # write the file
                                        open(filepath, "w").write(body)
                                        print("Enregistrement réussi\n")


                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    folder_name = clean(subject)
                                    if not os.path.isdir(folder_name):
                                        # make a folder for this email (named after the subject)
                                        os.mkdir(folder_name)
                                    filepath = os.path.join(folder_name, filename)
                                    # download attachment and save it
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                                    filename = "mail.txt"
                                    filepath = os.path.join(folder_name, filename)
                                    # write the file
                                    open(filepath, "w").write(body)
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        save = input("Voulez vous enregistrer le mail ? (OUI/NON)")
                        save = save.lower()
                        if (save == "oui"):
                            if content_type == "text/plain":
                                # print only text email parts
                                print("Enregistement")
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filename = "mail.pdf"
                                filepath = os.path.join(folder_name, filename)
                                # write the file
                                open(filepath, "w").write(body)
                                # open in the default browser
                                webbrowser.open(filepath)
                            print("=" * 100)

        # close the connection and logout
        mail.close()
        mail.logout()


def save_email():
    mail = input("Taper la nouvelle adresse email a enregistrer\n")
    conn = sqlite3.connect('Un_objet/database.db')
    cursor = conn.cursor()
    print(mail)
    cursor.execute("INSERT INTO email_address(address) VALUES('" + mail + "')")
    print("Adresse email enregistrée dans la base de donnée \n\n\n")
    conn.commit()


def enregistre_mail():
    oui = 0


if __name__ == '__main__':
    choix = "0"
    while (choix != "4"):
        choix = input(
            "Que souhaitez-vous faire ? \n1) Envoyer un email \n2) Lire Les x derniers mails \n3) Enregistrez un email \n4)Enregistrer un mail recu \n5) Quittez \n")
        if choix == "1":
            send_email()
        if choix == "2":
            lire_email()
        if choix == "3":
            save_email()
        if choix == "4":
            enregistre_mail()
