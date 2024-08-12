#TODO:いい感じに関数に切り出して整理する.

import flet as ft
from notion_client import Client
import sys
import traceback
import papnt

import papnt.misc

import papnt.database

import papnt.mainfunc

def format_doi(doi:str)->str:
    if "https://" in doi:
        doi=doi.replace("https://","")
    if "doi.org" in doi:
        doi=doi.replace("doi.org/","")
    if " " in doi:
        doi=doi.replace(" ","")
    if ("arXiv" in doi) and doi[-2]=="v":
        
        doi=doi[:-2]
    elif ("arXiv" in doi) and doi[-3]=="v":
        doi=doi[:-3]
    return doi
class Editable_Text(ft.Row):
    def __init__(self,value:str):
        super().__init__()
        self.value=value
        ET_text=ft.Text(value=value)
        ET_button_edit=ft.IconButton(icon=ft.icons.EDIT,on_click=self.ET_clicked_text_edit)
        ET_button_run=ft.IconButton(icon=ft.icons.RUN_CIRCLE,on_click=self.ET_clicked_run_papnt)
        ET_button_delete=ft.IconButton(icon=ft.icons.DELETE,on_click=self.ET_clicked_text_delete)
        self.controls=[ET_text,ET_button_edit,ET_button_run,ET_button_delete]
    def ET_clicked_text_edit(self,e):
        self.control_save=self.controls
        ET_button_done_edit=ft.FloatingActionButton(icon=ft.icons.DONE,on_click=self.ET_clicked_done_edit)
        new_value=ft.TextField(value=self.value)
        ET_edit_view=[new_value,ET_button_done_edit]
        self.controls=ET_edit_view
        self.update()
    def ET_clicked_text_delete(self,e):
        self.clean()
        pass
    def ET_clicked_run_papnt(self,e):
        papnt.mainfunc.create_records_from_doi(self.value)
        pass
    def ET_clicked_done_edit(self,e):
        self.value=self.controls[0].value
        self.controls=self.control_save
        self.controls[0].value=self.value
        self.update()
def main(page: ft.Page):
    def add_clicked(e):
        colum.controls.append(Editable_Text(value=new_task.value))
        new_task.value = ""
        page.update()
        new_task.focus()
    def delete_clicked(e):
        colum.clean()
        page.update()
    #Enterキーを押されたら文字を加える.
    def add_entered(e:ft.KeyboardEvent):
        if e.key=="Enter":
            add_clicked(e)
    def run_clicked(e):
        database_info=papnt.database.DatabaseInfo()
        client=Client(auth=database_info.tokenkey)
        database=papnt.database.Database(database_info)
        par={"database_id":database_info.database_id}
        for input_doi in colum.controls:
            #TODO:from_pdf とかもやる.
            doi=input_doi.value
            if "Already added" in doi or "Done" in doi or "processing..." in doi or "Error" in doi:
                continue
            doi=format_doi(doi)
            input_doi.value=doi
            page.update()
            # continue
            serch_flag={"filter":{"property":"DOI","rich_text":{"equals":doi}}}
            serch_flag["database_id"]=par["database_id"]
            response=client.databases.query(**serch_flag)
            if len(response["results"])!=0:
                input_doi.value="Already added! "+doi
                page.update()
                continue
            add_data={"properties":{"DOI":{'rich_text': [{'text': {'content': f'{doi}'}}]}}}
            add_data["parent"]=par
            doi_input_result= client.pages.create(**add_data)
            input_doi.value="processing..."
            page.update()
            try:
                papnt.mainfunc.create_records_from_doi(database,database_info,doi)
            except:
                client.pages.update(**{"page_id":doi_input_result["id"],"archived":True})
                exc= sys.exc_info()
                input_doi.value="Error: "+str(exc[1])
            else:
                input_doi.value="Done "+doi
            page.update()
    # page.title("Papnt Control")
    new_task = ft.TextField(hint_text="Please input DOI")
    page.on_keyboard_event=add_entered
    add_bottun=ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_clicked)
    run_bottun=ft.FloatingActionButton(icon=ft.icons.RUN_CIRCLE, on_click=run_clicked)
    delete_bottun=ft.FloatingActionButton(icon=ft.icons.DELETE, on_click=delete_clicked)
    page.add(new_task)
    page.add(ft.Row([add_bottun,run_bottun,delete_bottun]))
    colum=ft.Column()
    page.add(colum)

ft.app(target=main)