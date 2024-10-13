# doiを入力する画面;

import flet as ft
import sys
import configparser
import papnt

# doiからnotionに論文情報を追加する;
def create_records_from_doi(doi:str):
    dbinfo=papnt.database.DatabaseInfo()
    database=papnt.database.Database(dbinfo)
    prop = papnt.notionprop.NotionPropMaker().from_doi(doi,dbinfo.propnames)
    prop |= {'info': {'checkbox': True}}
    try:
        database.create(prop)
    except Exception as e:
        print(str(e))
        name = prop['Name']['title'][0]['text']['content']
        raise ValueError(f'Error while updating record: {name}')

# doiをフォーマットして、notion内の形式と合わせる;
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

# データベースにトークンキーとデータベースIDを追加するところ;
class Edit_Database(ft.Row):
    def __init__(self):
        super().__init__()
        self.ED_path_config=papnt.__path__[0]+"/config.ini"
        self.config=configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.config.read(self.ED_path_config)
        self.ED_text_tokenkey=ft.Text(value=self.config["database"]["tokenkey"])
        self.ED_text_database_id=ft.Text(value=self.config["database"]["database_id"])
        ED_buttun_edit=ft.FloatingActionButton(icon=ft.icons.EDIT,on_click=self.ED_clicked_text_edit)
        ED_buttun_edit.mini=True
        self.controls=[ED_buttun_edit,self.ED_text_tokenkey,self.ED_text_database_id]
    def ED_clicked_text_edit(self,e):
        self.ED_text_database_id=ft.TextField(value=self.config["database"]["database_id"],hint_text="database_id")
        self.ED_text_tokenkey=ft.TextField(value=self.config["database"]["tokenkey"],hint_text="tokenkey")
        self.controls=[ft.FloatingActionButton(icon=ft.icons.DONE,on_click=self.ED_clicked_done_edit),self.ED_text_tokenkey,self.ED_text_database_id]
        self.update()

    def ED_clicked_done_edit(self,e):
        self.controls[0]=ft.FloatingActionButton(icon=ft.icons.EDIT,on_click=self.ED_clicked_text_edit,mini=True)
        self.config["database"]["database_id"]=self.ED_text_database_id.value
        self.config["database"]["tokenkey"]=self.ED_text_tokenkey.value
        with open(self.ED_path_config, "w") as configfile:
            self.config.write(configfile, True)
        self.ED_text_tokenkey=ft.Text(value=self.config["database"]["tokenkey"])
        self.ED_text_database_id=ft.Text(value=self.config["database"]["database_id"])
        self.update()

# 編集可能なテキスト。
# ボタンには、
#       1.編集するためのボタン
#       2.テキストを消すボタン
#       3.１行だけ実行するボタン　がある;
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
        self.data=control_save
        self.update()
        new_value.focus()
    def ET_clicked_text_delete(self,e):
        self.clean()

    def ET_clicked_run_papnt(self,e):
        run_papnt_doi(self)

    def ET_clicked_done_edit(self,e):
        saved=self.data
        self.value=self.controls[0].value
        # saved[0].value=self.controls[0].value
        saved[0].value=self.controls[0].value
        self.controls=saved
        # self.controls[0].value=self.value
        self.update()
    def update_value(self,value:str):
        self.value=value
        self.controls[0].value=value
    def change_bgcolor(self,color):
        self.controls[0].bgcolor=color

# テキスト１行のdoiからnotionに情報を追加する;
def run_papnt_doi(now_text:Editable_Text):
    doi=now_text.value
    if "Already added" in doi or "Done" in doi or "processing..." in doi or "Error" in doi:
        return
    doi=format_doi(doi)
    now_text.value=doi
    now_text.update()
    now_text.update_value("processing...")
    now_text.update()
    database=papnt.database.Database(papnt.database.DatabaseInfo())
    serch_flag={"filter":{"property":"DOI","rich_text":{"equals":doi}}}
    serch_flag["database_id"]=database.database_id
    response=database.notion.databases.query(**serch_flag)
    if len(response["results"])!=0:
        now_text.update_value("Already added! "+doi)
        now_text.change_bgcolor(ft.colors.YELLOW)
        now_text.update()
        return
    try:
        create_records_from_doi(doi)
    except:
        exc= sys.exc_info()
        now_text.update_value("Error: "+str(exc[1]))
        now_text.change_bgcolor(ft.colors.RED)
    else:
        now_text.update_value("Done "+doi)
        now_text.change_bgcolor(ft.colors.GREEN)
    now_text.update()
    # print("now is done")

#このページの内容;
class View_input_doi(ft.View):
    def __init__(self):
        super().__init__()
        def add_clicked(e):
            list_doi.controls.insert(0,Editable_Text(value=input_text_doi.value))
            input_text_doi.value = ""
            self.update()
            input_text_doi.focus()
        def delete_clicked(e):
            list_doi.clean()
            self.update()
            input_text_doi.focus()
        #Enterキーを押されたら文字を加える.
        def add_entered(e:ft.OptionalEventCallable):
            add_clicked(e)
        def run_clicked(e):
            for input_doi in list_doi.controls:
                run_papnt_doi(input_doi)

        self.route="/"
        self.auto_scroll=True
        input_text_doi=ft.TextField(hint_text="Please input DOI",on_submit=add_entered,autofocus=True,expand=True)
        add_button=ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_clicked)
        run_button=ft.FloatingActionButton(icon=ft.icons.RUN_CIRCLE, on_click=run_clicked)
        delete_button=ft.FloatingActionButton(icon=ft.icons.DELETE, on_click=delete_clicked)
        list_doi=ft.Column()
        # 画面に追加する;
        self.controls.append(ft.Row([ft.Text("　論文追加",theme_style=ft.TextThemeStyle.HEADLINE_LARGE,weight=ft.FontWeight.W_900)],alignment=ft.MainAxisAlignment.SPACE_BETWEEN,height=50))
        self.controls.append(Edit_Database())
        self.controls.append(ft.Row([input_text_doi,add_button],alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        self.controls.append(ft.Row([run_button,delete_button]))
        self.controls.append(list_doi)
    def set_button_to_appbar(self,button):
        self.controls[0].controls.append(button)

