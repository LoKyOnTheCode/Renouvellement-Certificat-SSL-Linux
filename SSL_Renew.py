import paramiko, datetime, yaml



############## logs ################
now = datetime.datetime.now()
date_log = now.strftime("%d/%m/%Y %H:%M:%S")

############# host ###############
vm_host = 'ip_vm_hote'

########### year capture ###########
today = datetime.date.today()
year = int(today.strftime("%Y"))

##### colors #####
red = '\033[31m'
blue = '\033[34m'
yellow = '\033[33m'
green = '\033[92m'
purple = '\033[95m'
cyan = '\033[96m'
bold = '\033[1m'
end = '\033[0m'

bred = bold+red
byellow = bold+yellow
bblue = bold+blue
bcyan = bold+cyan
bgreen = bold+green
byellow = bold+yellow
bpurple = bold+purple

list_success = []
list_fail_timeout = []
list_fail_authentication = []
list_usernames = []
list_passwords = []
list_ips = []

#Se connecte à la VM host via scp pour prendre les fichiers et les mettre dans le répertoire (override de l'ancien)
list_cmd = [f'DIR=/etc/apache2/certificats_ssl/; scp <user>@{vm_host}:/root/{year}/* $DIR && echo "Fichiers copier dans $DIR"',
            'apache2ctl -t; VAR=$(printf "%d\n" $?) && if [[ $VAR -eq 0 ]]; then service apache2 reload && echo "apache2ctl -t return code 0. Reloaded"; else echo "An error occured."; fi;', ]


class new_vm :

    def __init__(self, ip, user, password, os) :
        self.ip = ip
        self.user = user
        self.password = password
        self.os = os

    #__str__ a permis dans ce code, d'écrire les bonnes valeurs au lieu de donner l'adresse 
    # mémoire de l'objet 
    # utile pour de la prez
    def __str__(self):
        return f"\nUsername : {self.user}\nPassword : {self.password}\nIP : {self.ip}\n"
    
    
def take_conf():
        
    with open('config.yml') as conf :
        data = yaml.load(conf, Loader=yaml.FullLoader)
        end_data = (len(data)) +1
        for i in range (1, end_data):

            list_usernames.append(data[f'vm{i}']['user'])
            list_passwords.append(data[f'vm{i}']['password'])
            list_ips.append(data[f'vm{i}']['ip'])


def connect_and_process(client):
    
    timeout = 5
    with open(f"logs {client.ip} {year}.txt", "w", encoding="utf-8") as log:
        connected = False
        try :
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(client.ip, username=client.user, password=client.password, timeout=timeout)
                print (f'\n##############################\n Connected to {bcyan}%s.{end}\n##############################\n' % client.ip)
                connected = True
        except TimeoutError:
            print (f"{bred}[!] Failed to connect to %s. TimeOut{end}\n" % client.ip)
            log.write("[!] Failed to connect to %s. TimeOut\n" % client.ip)
            list_fail_timeout.append(client)          
        except paramiko.AuthenticationException :
            print (f"{bred}[!] Failed to connect to %s.{end}\n" % client.ip)
            log.write("[!] Failed to connect to %s.\n" % client.ip)
            list_fail_authentication.append(client)
        except Exception as e :
                print (e)
                

        if connected :
            for x in range (len(list_cmd)):
                try :
                    stdin, stdout, stderr = ssh.exec_command(list_cmd[x])
                except Exception as e :
                        print (e)
                err = ''.join(stderr.readlines())
                out = ''.join(stdout.readlines())
                final_output = str(out)+str(err)
                print (f'{bcyan}{client.ip}{end} : {final_output}', end="")
                log.write(f'{date_log} - {client.ip} : {final_output}')
                        
                if x == (len(list_cmd)-1) : #OK !
                    ssh.close()
                    print (f'[{bgreen}+{end}] Connection to {bcyan}%s{end} closed.\n' % client.ip)
                    list_success.append(client)

if __name__ == '__main__' :
    
    take_conf()
    for i in range(len(list_usernames)):
        client = new_vm(ip=list_ips[i], user=list_usernames[i], password=list_passwords[i], os=None)
        connect_and_process(client)
        # print(client.__str__())
    print(f'Success : {len(list_success)}/{len(list_usernames)}\nFail TimeOut : {len(list_fail_timeout)}/{len(list_usernames)}\nFail Authentication : {len(list_fail_authentication)}/{len(list_usernames)}\n')