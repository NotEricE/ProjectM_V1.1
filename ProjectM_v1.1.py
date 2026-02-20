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
    for items_page in items['data']["boards"]:
        for name in items_page['items_page']['items']:
            name2 = rep(name)
            for subitems in name['subitems']:
                sub2 = rep(subitems)
                for txt in subitems['column_values']:
                    txt2 = rep(txt)
                    if name2 == project and sub2 == sub_item:
                        all_items = {"name" : name2, "subitems" : sub2, "links" : txt2}
                        return all_items

def b_link(t):
    link = t['links']
    return link

# Authentication for box
def box_auth():
    jwt_config = JWTConfig.from_config_file(config_file_path=r"A:\Json\ProjectM_config.json")
    auth = BoxJWTAuth(config=jwt_config)
    client = BoxClient(auth=auth)
    return client

# Gets the file id from box to prepare for a download
def box_f_id(url_link, client):
    url = f"{url_link}"
    try:
        folder_info = client.folders.get_folder_items(folder_id=f"{url[33:]}")
        mini_folder = folder_info.entries
        for folder in mini_folder:
            name = folder.name
            file_id = folder.id
            box_file = {"name": name, "id": file_id}
            if not box_file["name"].endswith(".ai"):
                box_download(box_file, client)
    except BoxAPIError:
        print(f"Not a valid folder link")
    try:
        i = client.shared_links_folders.find_folder_for_shared_link("".join([ f"shared_link={url}" ]))
        ito = i.id
        folder_info2 = client.folders.get_folder_items(folder_id=ito)
        mini_folder2 = folder_info2.entries
        for folder2 in mini_folder2:
            box_file = {"name": folder2.name, "id": folder2.id}
            if not box_file["name"].endswith(".ai"):
                box_download(box_file, client)
    except BoxAPIError as d:
        print(f"Not s valid shared link \n{d}")

# Downloads the box file and saves it to the donwload folder
def box_download(url, client):
    file_name = url["name"]
    file_id = url["id"]
    try:
        file = client.downloads.download_file(file_id=file_id)
        dwn_pt = "C:/Users/Public/Downloads/"
        full_pt = dwn_pt + file_name
        convert = file.read()
        with open(f"{full_pt}", "wb") as f:
            f.write(convert)
        return file_name, file_id, full_pt
    except BoxAPIError as e:
        print(f"not found {e}")


def air_table():
    with open("output.pdf", 'rb') as f:
        j = f.read()
    a = Attach()
    a.Name = "Test"
    a.Notes = "Uploaded via script"
    a.save()
    a.Attachments.upload("out.pdf",content=j, content_type="application/pdf")
    
def mon_2(project):
    acc = monday_key()
    url, headers = acc

    query2 = """query getItemsAndSubitems {
                boards(ids: 3066531206) {
                items_page {
                items {
                column_values (ids: ["text", "text2"]) {
                text
                }
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
    for t in items["data"]["boards"]:
        for j in t["items_page"]["items"]:
            for l in j["column_values"]:
                desc = l.get("text")
                if desc in project:
                    print(desc)

def main():
    while True:
        first = input("Project Name? ")
        while first:
            second = input("subitem? ")
            if second == "q":
                break
            t = mon_columns(first, second)
            client = box_auth()
            url = b_link(t)
            box_f_id(url, client)
        # air_table()
                

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nexited")
