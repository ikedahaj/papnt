import typing
import time
import flet as ft
import configparser
import papnt

import papnt.database

import papnt.misc

# Python code to sort a list of strings A based on the rules provided
def _access_notion_prop(value_props):
    mode=value_props["type"]
    match mode:
        case "title":
            return value_props["title"][0]["text"]["content"]
        case "select":
            return value_props["select"]["name"]
        case "multi_select":
            connected_lists=""
            for name in value_props["multi_select"]:
                connected_lists+=name["name"]
                connected_lists+=","
            return connected_lists
        case "rich_text":
            return value_props["rich_text"][0]["plain_text"]
        case "number":
            return value_props["number"]
        case "url":
            return value_props["url"]
        case _:
            raise ValueError('Invalid mode')

def _access_notion_prop_value(prop_page,prop):
    page_prop=prop_page["properties"]
    return _access_notion_prop(page_prop[prop])

class _Papers_List(ft.SearchBar):
    def __init__(self,input_list:list,add_list):
        """bibに追加する論文を選択するための入力フォーム

        Args:
            input_list (list): 未選択の要素。notionの"results"をそのまま入れる
            add_list (function): 要素を下に追加する関数。第一引数に表示するテキスト、第二引数にnotionのresultをとる
        """
        super().__init__()
        # anchor=ft.SearchBar()
        self.__PL_init_list=input_list
        self.__PL_select_flag="Name"
        self.__PL_listview=ft.ListView(controls=[ft.ListTile(title= ft.Text(_access_notion_prop_value(name,self.__PL_select_flag)),data=name,on_click=self.__close_anchor) for name in input_list])
        self.view_elevation=4
        self.controls=[self.__PL_listview]
        self.bar_hint_text="bibファイルに加える論文を選択"
        self.view_hint_text=self.bar_hint_text
        self.autofocus=True
        self.on_tap=self.__handle_tap
        self.on_change=self.__PL_handle_change
        self.__PL_add_list_to_out=add_list
    def __PL_sort_strings(self, B):
        starts_with_B = []
        includes_B=[]
        does_not_start_with_B = []
        for str in self.__PL_listview.controls:
            if str.title.value.lower().startswith(B.lower()):
                starts_with_B.append(str)
            elif B.lower() in str.title.value.lower():
                includes_B.append(str)
            else :
                does_not_start_with_B.append(str)
        self.__PL_listview.controls= starts_with_B+includes_B + does_not_start_with_B
    def __PL_update_listview(self,texts_list):
        self.__PL_listview.clean()
        new_controls=[]
        for name in texts_list:
            new_controls.append(ft.ListTile(title=ft.Text(_access_notion_prop_value(name,self.__PL_select_flag)),on_click=self.__close_anchor,data=name))
        self.__PL_listview.controls=new_controls
    def __close_anchor(self,e):
        text=e.control.title.value
        self.close_view(text)
        time.sleep(0.05)
        datas=e.control.data
        print(datas)
        self.__PL_add_list_to_out(text,datas)
        self.__PL_listview.controls.remove(e.control)
        self.__PL_init_list.remove(datas)
        self.value=None
        self.update()
    def __handle_tap(self,e):
        self.open_view()
    def __PL_handle_change(self,e):
        self.__PL_sort_strings(e.data)
        if e.data=="":
            self.__PL_update_listview(self.__PL_init_list)
        self.update()
    def PL_change_prop_name(self,propname):
        self.__PL_select_flag=propname
        for name in self.__PL_listview.controls:
            name.title.value=_access_notion_prop_value(name.data,propname)
        self.update()
    def add_new_props(self,new_prop):
        self.__PL_init_list.insert(0,new_prop)
        self.__PL_listview.controls.insert(0,ft.ListTile(title=ft.Text(_access_notion_prop_value(new_prop,self.__PL_select_flag)),on_click=self.__close_anchor,data=new_prop))
class _Text_Select(ft.Row):
    def __init__(self,text_list:list):
        super().__init__()
        # anchor=ft.SearchBar()
        self.__TS_listview=ft.ListView()
        self.__text_list=text_list
        self.__TS_listview=ft.ListView(controls=[ft.ListTile(title= ft.Text(name),on_click=self.__close_anchor) for name in text_list])
        text=ft.Text()
        button=ft.FloatingActionButton(icon=ft.icons.EDIT,mini=True,on_click=self.__reset_anchor)
        self.controls=[self.__TS_serBar,text,button]
        self.controls[1].visible=False
        self.controls[2].visible=False
        # self.update()
    def __TS_update_listview(self,texts_list):
        # self.__TS_listview.clean()
        new_controls=[]
        for name in texts_list:
            new_controls.append(ft.ListTile(title=ft.Text(name),on_click=self.__close_anchor))
        self.__TS_listview.controls=new_controls
        print(self.__TS_listview.controls)
    def __close_anchor(self,e):
        text=e.control.title.value
        self.__TS_serBar.close_view(text)
        self.__TS_serBar.data=False
        import time
        time.sleep(0.1)
        self.__handle_submit(e)
    def __handle_tap(self,e):
        self.__TS_serBar.open_view()
        self.__TS_serBar.data=True
    def __handle_change(self,e):
        strings2=sort_strings(self.__text_list,e.data)
        if e.data=="":
            strings2=self.__text_list
        self.__TS_update_listview(strings2)
        self.update()
    def __handle_submit(self,e):
        new_text=self.controls[0].value
        if new_text not in self.__text_list:
            self.__text_list.insert(0,new_text)
            self.__TS_listview.controls.insert(0,ft.ListTile(title=ft.Text(new_text),on_click=self.__close_anchor))
            # self.controls[0].controls=[self.__TS_listview]
        if self.__TS_serBar.data:
            # self.__TS_serBar.close_view(new_text)
            self.controls[0].close_view(new_text)
            self.__TS_serBar.data=False
            self.update()
            import time
            time.sleep(0.1)
            self.__handle_submit(e)
            return
        self.controls[0].visible=False
        self.controls[1].visible=True
        self.controls[2].visible=True
        self.controls[1].value=new_text
        self.update()
    def __reset_anchor(self,e):
        # self.__TS_serBar.controls=[self.__TS_listview]
        self.controls[0].visible=True
        self.controls[1].visible=False
        self.controls[2].visible=False
        self.update()
        # self.__TS_update_listview(self.__text_list)
        self.__TS_serBar.open_view()
        self.__TS_serBar.data=True

class _Edit_Database(ft.Row):
    def __init__(self):
        super().__init__()
        self.ED_path_config=papnt.__path__[0]+"/config.ini"
        self.config=configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.config.read(self.ED_path_config)
        ED_text_dir_save_bibfile_decided=ft.Text(value=self.config["misc"]["dir_save_bib"])
        ED_button_edit=ft.FloatingActionButton(icon=ft.icons.EDIT,on_click=self.ED_clicked_text_edit,mini=True)
        ED_text_dir_save_bibfile_input=ft.TextField(value=ED_text_dir_save_bibfile_decided.value,hint_text="dirname of bib file",visible=False)
        ED_button_done_edit=ft.FloatingActionButton(icon=ft.icons.DONE,on_click=self.ED_clicked_done_edit,mini=True,visible=False)
        self.controls=[ED_text_dir_save_bibfile_decided, ED_button_edit,ED_text_dir_save_bibfile_input,ED_button_done_edit]
    def ED_clicked_text_edit(self,e):
        self.controls[0].visible=False
        self.controls[1].visible=False
        self.controls[2].visible=True
        self.controls[3].visible=True
        self.controls[2].value=self.controls[0].value
        self.update()

    def ED_clicked_done_edit(self,e):
        self.controls[0].visible=True
        self.controls[1].visible=True
        self.controls[2].visible=False
        self.controls[3].visible=False
        new_text=self.controls[2].value
        self.controls[0].value=new_text
        self.config["misc"]["dir_save_bib"]=new_text
        with open(self.ED_path_config, "w") as configfile:
            self.config.write(configfile, True)
        self.update()
class _Text_Bib_List(ft.Row):
    def __init__(self,text_value,notion_page,delete_clicked):
        super().__init__()
        self.data=notion_page
        self.controls=[ft.Text(value=text_value),ft.FloatingActionButton(icon=ft.icons.DELETE,on_click=delete_clicked)]



class view_bib_maker(ft.View):
    def __init__(self):
        super().__init__()
        self.route="/make_bib_file"
        self.appbar=ft.AppBar(title=ft.Text("make_bib_file"))
        self.controls.append(_Edit_Database())

        path_config=papnt.__path__[0]+"/config.ini"
        notion_configs=papnt.misc.load_config(path_config)
        self.select_prop_flag=ft.Dropdown(value="Name",width=150)

        self.database=papnt.database.Database(papnt.database.DatabaseInfo())
        response=self.database.notion.databases.query(self.database.database_id)
        self.results=response["results"]

        self.Paper_list=ft.Column()

        self._input_Paper_List=_Papers_List(self.results,self._add_Paper_list)
        self.select_prop_flag.on_change=self._dropdown_changed
        self.select_prop_flag.options=[ft.dropdown.Option(key=propname) for propname in notion_configs["propnames"].values()]
        self.select_prop_flag.options.insert(0,ft.dropdown.Option(key="Name"))
        self._input_Paper_List.bar_leading=self.select_prop_flag

        self.controls.append(self._input_Paper_List)
        self.controls.append(self.Paper_list)
    def _change_prop_name(self,propname):
        for item in self.Paper_list.controls:
            item.controls[0].value=_access_notion_prop_value(item.controls[0].data,propname)
        self.Paper_list.update()
        self._input_Paper_List.PL_change_prop_name(propname)
    def _delete_text(self,text_row:ft.Row):
        text=text_row.controls[0]
        self._input_Paper_List.add_new_props(text.data)
        text_row.clean()
        self.Paper_list.update()

    def _add_Paper_list(self,text_value,notion_result):
        text=ft.Text(text_value,data=notion_result)
        del_button=ft.FloatingActionButton(icon=ft.icons.DELETE)
        add_text_list=ft.Row(controls=[text,del_button])
        def delete_clicked(e):
            self._delete_text(add_text_list)
        add_text_list.controls[1].on_click=delete_clicked
        self.Paper_list.controls.insert(0,add_text_list)
        self.Paper_list.update()
    def _dropdown_changed(self,e):
        self._change_prop_name(e.data)