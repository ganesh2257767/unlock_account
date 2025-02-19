import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from pprint import pprint
import gooeypie as gp
import json

version = 0.2

urls = {
    0: "http://cdapix-int.lab.cscqa.com:80/cdxservices/ws",
    1: "http://cdapix-q2.lab.cscqa.com:80/cdxservices/ws",
    2: "http://cdapix-q3.lab.cscqa.com:80/cdxservices/ws"
}


HEADERS = {"Content-Type": "text/xml"}
AUTHENTICATION = HTTPBasicAuth('cdxservicesusr', 'cdxservicesusr_qa')


# After account is locked in IDA
# 1: Query lock to get Operator and lock PID
# 2: Once Operator and Lock PID is retreived, unlock the account using these details
# 3: Now lock with the provisioning party (ESC/DHG or ODO)
# 4: Complete IDA submission and check message
 
body_query_lock = """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:cab="http://www.cablevision.com/"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <soapenv:Header/>
        <soapenv:Body>
            <cab:sendxml soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <application xsi:type="xsd:string">CLAWS</application>
                <xmlReq xsi:type="xsd:string">
                    <![CDATA[<?xml version="1.0"?> <transaction>
                        <apiname>QueryLock</apiname>
                        <comcorp>{}</comcorp>
                        <house>{}</house>
                        <opr>{}</opr>
                        </transaction>]]>
                </xmlReq>
            </cab:sendxml>
        </soapenv:Body>
    </soapenv:Envelope>
"""

body_unlock = """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:cab="http://www.cablevision.com/"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <soapenv:Header/>
        <soapenv:Body>
            <cab:sendxml soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <application xsi:type="xsd:string">CLAWS</application>
                <xmlReq xsi:type="xsd:string">
                    <![CDATA[<?xml version="1.0"?> <transaction>
                        <apiname>UnLockAcct</apiname>
                        <comcorp>{}</comcorp>
                        <house>{}</house>
                        <opr>{}</opr>
                        <lockacct_pid>{}</lockacct_pid>
                        </transaction>]]>
                </xmlReq>
            </cab:sendxml>
        </soapenv:Body>
    </soapenv:Envelope>
    """
    
body_lock = """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:cab="http://www.cablevision.com/"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <soapenv:Header/>
        <soapenv:Body>
            <cab:sendxml soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <application xsi:type="xsd:string">CLAWS</application>
                <xmlReq xsi:type="xsd:string">
                    <![CDATA[<?xml version="1.0"?> <transaction>
                    <apiname size="40">LockAcct</apiname>
                    <comcorp size="5">{}</comcorp>
                    <house size="6">{}</house>
                    <opr size="3">{}</opr>
                    </transaction>]]>
                </xmlReq>
            </cab:sendxml>
        </soapenv:Body>
    </soapenv:Envelope>
    """



def query_lock(url, corp, house, operator):
    res = requests.post(url, body_query_lock.format(corp, house, operator), headers=HEADERS, auth=AUTHENTICATION)    
    print(res.status_code)
    response = xmltodict.parse(res.content)
    response_inner = xmltodict.parse(response["env:Envelope"]["env:Body"]["m:sendxmlResponse"]["result"]["#text"])["transaction"]
    return response_inner


def unlock_account(url, corp, house, operator, pid):
    res = requests.post(url, body_unlock.format(corp, house, operator, pid), headers=HEADERS, auth=AUTHENTICATION)    
    print(res.status_code)
    response = xmltodict.parse(res.content)
    response_inner = xmltodict.parse(response["env:Envelope"]["env:Body"]["m:sendxmlResponse"]["result"]["#text"])["transaction"]
    return response_inner

def lock_account(url, corp, house, operator):
    res = requests.post(url, body_lock.format(corp, house, operator), headers=HEADERS, auth=AUTHENTICATION)    
    print(res.status_code)
    response = xmltodict.parse(res.content)
    return json.dumps(response, indent=4)
    

def submit_request(event):
    url = urls[dropdown_env.selected_index]
    query_lock_response = query_lock(url, input_corp.text, input_house.text, "SM2")
    print("Response:", query_lock_response)
    
    if not query_lock_response["errordescription"]:
        operator = query_lock_response["opr"]
        pid = query_lock_response["lockacct_pid"]
    else:
        app.alert("Error", query_lock_response["errordescription"]["#text"], "error")
        return
    
    unlock_account_response = unlock_account(url, input_corp.text, input_house.text, operator, pid)
    result = unlock_account_response["lockacct_result"]
    if result == "0":
        title = "Success"
        result = "Account unlocked successfully!"
        icon = "info"
    else:
        title = "Failure"
        icon = "error"
    
    app.alert(title, result, icon)
        

def process_response(response):
        # Converting the full XML response to Dictionary
        full_response_dict = xmltodict.parse(response.content)

        # Getting the inner XML from the Dictionary
        inner_xml = full_response_dict["env:Envelope"]["env:Body"]["m:sendxmlResponse"]["result"]["#text"]

        # Converting that inner XML to 
        inner_dict = xmltodict.parse(inner_xml)
        
        # Getting the required sub dictionary
        final_dict = inner_dict['transaction']
        output_final = ''
        for k, v in final_dict.items():
            output_final += f'{k}: {v}\n'
        output.text = output_final
        result.show()
   

functions = {
    0: body_query_lock,
    1: body_unlock,
    2: body_lock
}



app = gp.GooeyPieApp(f"Unlock Account v{version}")
app.width = 300

app.set_resizable(False)

try:
    app.set_icon('.//unlocked.png')
except FileNotFoundError:
    pass


label_env = gp.Label(app, 'Select ENV')
dropdown_env = gp.Dropdown(app, ['QA INT', 'QA2', 'QA3'])


label_corp = gp.Label(app, 'Corp')
input_corp = gp.Input(app)
label_house = gp.Label(app, 'House')
input_house = gp.Input(app)


submit = gp.Button(app, 'Unlock', submit_request)

result = gp.Window(app, "Result")
output = gp.Textbox(result)
output.width = 50
output.height = 10


app.set_grid(4, 2)
app.add(label_env, 1, 1)
app.add(dropdown_env, 1, 2)
app.add(label_corp, 2, 1)
app.add(input_corp, 2, 2)
app.add(label_house, 3, 1)
app.add(input_house, 3, 2)

app.add(submit, 4, 1, column_span=2)

result.set_grid(1, 1)
result.add(output, 1, 1, fill=True, stretch=True)

app.run()