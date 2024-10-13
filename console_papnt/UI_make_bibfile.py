import flet as ft
import configparser
import papnt

# Python code to sort a list of strings A based on the rules provided
def sort_strings(A, B):
    # Split the list into two groups: strings that start with B and others
    
    starts_with_B = []
    does_not_start_with_B = []
    for str in A:
        if str.lower().startswith(B.lower()):
            starts_with_B.append(str)
        else :
            does_not_start_with_B.append(str)
    
    # Sort both groups, starts_with_B in lexicographical order
    starts_with_B_sorted = sorted(starts_with_B)
    does_not_start_with_B_sorted = sorted(does_not_start_with_B)
    
    # Return the concatenated list, with starts_with_B_sorted first
    return starts_with_B_sorted + does_not_start_with_B_sorted

class Text_Select(ft.Row):
    def __init__(self,text_list:list):
        super().__init__()
        # anchor=ft.SearchBar()
        self.__TS_listview=ft.ListView()
        self.__text_list=text_list
        self.__TS_listview=ft.ListView(controls=[ft.ListTile(title= ft.Text(name),on_click=self.__close_anchor) for name in text_list])
        # for name in text_list:
        #     TS_listview.controls.append(ft.ListTile(ft.Text(name),on_click=close_anchor))
        # TS_update_listview(text_list)
        self.__TS_serBar=ft.SearchBar(
            view_elevation=4,
            on_tap=self.__handle_tap,
            on_change=self.__handle_change,
            bar_hint_text="Cite key",
            view_hint_text="Cite_key",
            autofocus=True,
            controls=[self.__TS_listview],
            on_submit=self.__handle_submit,
            )
        text=ft.Text()
        button=ft.FloatingActionButton(icon=ft.icons.EDIT,mini=True,on_click=self.__reset_anchor)
        self.controls=[self.__TS_serBar,text,button]
        self.controls[1].visible=False
        self.controls[2].visible=False
        # self.update()
    def __TS_update_listview(self,texts_list):
        print(self.__TS_listview.controls)
        # self.__TS_listview.clean()
        new_controls=[]
        for name in texts_list:
            new_controls.insert(0,ft.ListTile(title=ft.Text(name),on_click=self.__close_anchor))
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
        print(new_text)
        if new_text not in self.__text_list:
            self.__text_list.insert(0,new_text)
            self.__TS_listview.controls.insert(0,ft.ListTile(title=ft.Text(new_text),on_click=self.__close_anchor))
            # self.controls[0].controls=[self.__TS_listview]
        if self.__TS_serBar.data:
            print(new_text)
            # self.__TS_serBar.close_view(new_text)
            self.controls[0].close_view(new_text)
            self.__TS_serBar.data=False
            self.update()
            import time
            time.sleep(0.1)
            print("closed")
            self.__handle_submit(e)
            return
        print("after")
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

class Edit_Database(ft.Row):
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

class view_bib_maker(ft.View):
    def __init__(self):
        super().__init__()
        self.route="/make_bib_file"
        self.appbar=ft.AppBar(title=ft.Text("make_bib_file"))
        self.controls.append(Edit_Database())