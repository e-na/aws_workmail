import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from exchangelib import Credentials,Account,Configuration,DELEGATE,BASIC,FileAttachment,errors,Folder
from request import exceptions

def get_secret(secret_name):
    region_name="eu-west-1"
    session=boto3.session.Session()
    config=Config(proxies={})
    client=session.client(service_name='secretsmanager',region_name=region_name,config=config)
    
def create_subfolder(account,folder_name):
    try:
        f=Folder(parent=account.inbox,name=folder_name)
        f.save()
        print(f"subfolder {folder_name} created successfully!!")
        return True
    except Exception as e:
        print(f"Error during creating subfolder {folder_name}")
        
def get_subfolder(account,folder_name):
    try:
        f=account.inbox / f'{folder_name}'
        return f
    except errors.ErrorFolderNotFound as e:
        print(f"folder not found.. creating sub_folder {folder_name} in inbox..")
        if create_subfolder(account,folder_name):
             f=Folder(parent=account.inbox,name=folder_name)
             return f
    except Exception as e:
        print(f"Error during creating folder: {e}")
        raise e
    
def lambda_handler(event,context):
    print(event)
    try:
        username,password=get_secret("secret-name-stored-in-secret-manager")
        credentials=Credentials(username,password)
        connect=False
        #using autodiscover=True
        try:
            account=Account(username,credentials=credentials,autodiscover=True)
            connect=True
            print("connected via autodiscover=True")
        except Exception as e:
            print(e)
        if not connect:
            #using ews endpoint
            try:
                #server name can be seen from the event passed
                config=Configuration(server='ews.mail.eu-west-1.awsapps.com',credentials=credentials)
                account=Account(primary_smtp_address=username,config=config,autodiscover=False,access_type=DELEGATE)
                print("connected via ews endpoints")
            except errors.UnauthorisedError as e:
                print(f"Invalid credentials {e}")
            except error.ErrorPasswordExpired as e:
                print(f"Password expired.Please change the password and try again {e}")
            except Exception as e:
                print(f"Error in mailbox login : {e}")
                
                folder_name="sub-folder 1"
                for item in account.inbox.all().order_by('-datetime_received')[:5]:
                    subfolder=get_subfolder(account,folder_name)
                    item.move(subfolder)
                    print(f"email moved to {folder_name} folder ....")
                
                
        
        
        
