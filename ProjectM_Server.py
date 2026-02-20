from box_sdk_gen import BoxClient, BoxJWTAuth, JWTConfig, BoxAPIError
from pyairtable import Api
from pyairtable.orm import Model, fields as F
from datetime import date
import json
import requests
import yaml

with open(r"A:\YAML Files\info.yml", "r") as i:
    data = yaml.safe_load(i)

# This class is for Airtable api to work.
class Attach(Model):
    Attachments = F.AttachmentsField(field_name="Attachments", validate_type=True, readonly=False)
    Name = F.TextField(field_name="Name")
    Notes = F.TextField(field_name="Notes")
    
    class Meta:
        base_id="appewgZOkOaBVYDrN"
        table_name="Table 1"
        api_key = data["api_keys"][6]



def monday_key():
    key = data["api_keys"][0]
    url = "https://api.monday.com/v2"
    headers = {"Authorization" : key}
    return url, headers

# This function returns the value for these specific keys. I made this to clear some clutter from mon_columns
def rep(item):
    if not isinstance(item, dict):
        return None
    return item.get("name") or item.get("text")

# Getting monday column info
def mon_columns(project, sub_item):
    acc = monday_key()
    url, headers = acc

    query2 = """query getItemsAndSubitems {
                boards(ids: 3066531206) {
                items_page {
                items {
                name
                subitems {
                name
                column_values (ids: ["text", "link0"]) {
                text
                }
                }
                }
                }
                }
                }"""
    data2 = {'query' : query2}
    r2 = requests.post(url=url, json=data2, headers=headers)
    items = r2.json()

def air_table(file_name, path):
    # with open(f"{path}", 'rb') as f:
    #     j = f.read()
    a = Attach()
    a.Name = "Test"
    a.Notes = "Uploaded via script"
    a.save()
    
    for paths in path:
        file_name = paths.split("/")[-1].split("\\")[-1]
        with open(path, "rb") as f:
            j = f.read()
    a.Attachments.upload(f"{file_name}",content=j, content_type="application/pdf")