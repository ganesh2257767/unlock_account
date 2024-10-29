import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from pprint import pprint
import gooeypie as gp
import json

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
    return json.dumps(response, indent=4)


def unlock_account(url, corp, house, operator, pid):
    res = requests.post(url, body_unlock.format(corp, house, operator, pid), headers=HEADERS, auth=AUTHENTICATION)    
    print(res.status_code)
    response = xmltodict.parse(res.content)
    return json.dumps(response, indent=4)

def lock_account(url, corp, house, operator):
    res = requests.post(url, body_lock.format(corp, house, operator), headers=HEADERS, auth=AUTHENTICATION)    
    print(res.status_code)
    response = xmltodict.parse(res.content)
    return json.dumps(response, indent=4)
    

def submit_request(event):
    url = urls[dropdown_env.selected_index]
    body = functions[dropdown_action.selected_index]
    if all((dropdown_env.selected, input_corp.text, input_house.text, input_operator.text, input_pid.disabled or input_pid.text)):
        if input_pid.text and not input_pid.disabled:
            full_response = requests.post(url, body.format(input_corp.text, input_house.text, input_operator.text, input_pid.text), headers=HEADERS, auth=AUTHENTICATION)    
        else:
            full_response = requests.post(url, body.format(input_corp.text, input_house.text, input_operator.text), headers=HEADERS, auth=AUTHENTICATION)    
        
        process_response(full_response)
    else:
        app.alert("Enter all values")
        return

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
   
        
def enable_disable_pid(event):
    if event.widget.selected_index == 1:
        input_pid.disabled = False
    else:
        input_pid.disabled = True
    

# query_lock()
functions = {
    0: body_query_lock,
    1: body_unlock,
    2: body_lock
}


app = gp.GooeyPieApp("WR-642")
# app.width = 600
# app.height = 600


label_env = gp.Label(app, 'Select ENV')
dropdown_env = gp.Dropdown(app, ['QA INT', 'QA2', 'QA3'])

label_action = gp.Label(app, 'Select API')
dropdown_action = gp.Dropdown(app, ['Query Lock', 'Unlock Account', 'Lock Account'])
    
dropdown_action.add_event_listener('select', enable_disable_pid)

label_corp = gp.Label(app, 'Corp')
input_corp = gp.Input(app)
label_house = gp.Label(app, 'House')
input_house = gp.Input(app)
label_operator = gp.Label(app, 'Operator')
input_operator = gp.Input(app)
label_pid = gp.Label(app, 'PID')
input_pid = gp.Input(app)

submit = gp.Button(app, 'Submit', submit_request)

result = gp.Window(app, "Result")
output = gp.Textbox(result)
output.width = 50
output.height = 10


app.set_grid(7, 2)
app.add(label_env, 1, 1)
app.add(dropdown_env, 1, 2)
app.add(label_action, 2, 1)
app.add(dropdown_action, 2, 2)
app.add(label_corp, 3, 1)
app.add(input_corp, 3, 2)
app.add(label_house, 4, 1)
app.add(input_house, 4, 2)
app.add(label_operator, 5, 1)
app.add(input_operator, 5, 2)
app.add(label_pid, 6, 1)
app.add(input_pid, 6, 2)
app.add(submit, 7, 1, column_span=2)

result.set_grid(1, 1)
result.add(output, 1, 1, fill=True, stretch=True)

app.run()