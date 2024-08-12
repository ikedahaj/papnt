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
        self.ET_text=ft.Text()
        self.ET_text.value=value
        ET_button_edit=ft.IconButton(icon=ft.icons.EDIT,on_click=self.ET_clicked_text_edit)
        ET_button_run=ft.IconButton(icon=ft.icons.RUN_CIRCLE,on_click=self.ET_clicked_run_papnt)
        ET_button_delete=ft.IconButton(icon=ft.icons.DELETE,on_click=self.ET_clicked_text_delete)
        self.controls=[self.ET_text,ET_button_edit,ET_button_run,ET_button_delete]
    def ET_clicked_text_edit(self,e):
        control_save=self.controls
        ET_button_done_edit=ft.FloatingActionButton(icon=ft.icons.DONE,on_click=self.ET_clicked_done_edit)
        new_value=ft.TextField(value=self.value)
        new_value.on_submit=self.ET_clicked_done_edit
        ET_edit_view=[new_value,ET_button_done_edit]
        self.controls=ET_edit_view
        self.controls[0].data=control_save
        self.update()
        new_value.focus()
    def ET_clicked_text_delete(self,e):
        self.clean()

    def ET_clicked_run_papnt(self,e):
        run_papnt_doi(self)

    def ET_clicked_done_edit(self,e):
        saved=self.controls[0].data
        self.value=self.controls[0].value
        # saved[0].value=self.controls[0].value
        saved[0].value=self.controls[0].value
        self.controls=saved
        # self.controls[0].value=self.value
        self.update()
    def update_value(self,value:str):
        self.value=value
        self.controls[0].value=value
        

def run_papnt_doi(now_text:Editable_Text):
    print("now is doi",now_text.value)
    doi=now_text.value
    now_text.update_value("processing...")
    now_text.update()
    # print("now is processing")
    try:
        papnt.mainfunc.create_records_from_doi(doi)
    except:
        exc= sys.exc_info()
        now_text.update_value("Error: "+str(exc[1]))
    else:
        now_text.update_value("Done "+doi)
    now_text.update()
    # print("now is done")
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
    def add_entered(e:ft.OptionalEventCallable):
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
            serch_flag={"filter":{"property":database_info.propnames["doi"],"rich_text":{"equals":doi}}}
            serch_flag["database_id"]=par["database_id"]
            response=client.databases.query(**serch_flag)
            if len(response["results"])!=0:
                input_doi.update_value("Already added! "+doi)
                page.update()
                continue
            run_papnt_doi(input_doi)
    # page.title("Papnt Control")
    new_task = ft.TextField(hint_text="Please input DOI")
    new_task.on_submit=add_entered
    add_bottun=ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_clicked)
    run_bottun=ft.FloatingActionButton(icon=ft.icons.RUN_CIRCLE, on_click=run_clicked)
    delete_bottun=ft.FloatingActionButton(icon=ft.icons.DELETE, on_click=delete_clicked)
    page.add(new_task)
    page.add(ft.Row([add_bottun,run_bottun,delete_bottun]))
    colum=ft.Column()
    page.add(colum)

ft.app(target=main)