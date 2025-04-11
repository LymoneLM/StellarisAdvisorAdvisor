import os
import io
import re
import csv
import sys
import json
import enum
import shutil
import hashlib
import webbrowser

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame

# meta
cn_title = "群星顾问模组小助手"
en_title = "Stellaris Advisor Advisor"
version = "v0.1.1-beta"
_copyright = "LymoneLM"

# constant
voice_path = r".\voice"
default_path = r".\.default"
if hasattr(sys, '_MEIPASS'):
    # noinspection PyProtectedMember
    img_path = sys._MEIPASS + "\img"
else:
    img_path = r".\img"
backup_path = r".\backup"
output_path = r".\output"
hash_algorithm = "sha256"

# global variable
obj_hash_name = ""
default_index = []
this_index = []
work_index = []
default_info = {
    "internal" : {
        "is_use_dirs" : True ,
        "need_descriptor_mod" : False ,
    },
    "meta" : {
        "object_name" : None ,
        "cn_name" : None ,
        "en_name" : None ,
        "icon_path" : None ,
    }
}
info = {}


# calcu hash of file
def get_file_hash(file_path):
    hash_obj = hashlib.new(hash_algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


def traverse_and_hash(root_dir=voice_path):
    file_hashes = []
    for roots, dirs, files in os.walk(root_dir):
        for file_name in files:
            file_path = os.path.join(roots, file_name)
            file_hash = get_file_hash(file_path)
            if file_hash:
                file_hashes.append(file_hash)
    combined_hash = hashlib.new(hash_algorithm)
    for hash_val in sorted(file_hashes):
        combined_hash.update(hash_val.encode('utf-8'))
    return combined_hash.hexdigest()

# file operate
# scan csv
def get_default_index():
    global default_index
    default_index.clear()
    try:
        f = csv.reader(open(os.path.join(default_path, "index.csv"), encoding="utf-8"))
        next(f)
        for row in f:
            default_index.append([row[0], row[1]])
        return True
    except Exception as e:
        print(f"Error processing default index.csv: {str(e)}")
        return False

def get_this_index():
    global this_index
    this_index.clear()
    try:
        f = csv.reader(open("index.csv", encoding="utf-8"))
        next(f)
        for row in f:
            this_index.append(row)
        return True
    except Exception as e:
        print(f"Error processing this index.csv: {str(e)}")
        return False


def init_dirs():
    global default_index
    if not get_default_index():
        return False
    shutil.rmtree(voice_path, ignore_errors=True)
    for i in range(len(default_index)):
        os.makedirs(voice_path + "\{:0>2d}".format(i) + default_index[i][1], exist_ok=True)
    return True

def init_csv():
    try:
        if not os.path.exists(voice_path):
            os.makedirs(voice_path)
        shutil.copyfile(os.path.join(default_path, "index.csv"), "index.csv")
        return True
    except Exception as e:
        print(f"Error init index.csv: {str(e)}")
        return False

def delete_init():
    try:
        shutil.rmtree(voice_path, ignore_errors=True)
        if os.path.exists("index.csv"):
            os.remove("index.csv")
        if os.path.exists("info.json"):
            os.remove("info.json")
        return True
    except Exception as e:
        print(f"Error delete init: {str(e)}")
        return False

def init_info_json(args):
    global info
    info = default_info
    internal = info.get("internal")
    internal["is_use_dirs"] = args[0]
    internal["need_descriptor_mod"] = args[1]
    info["internal"] = internal
    try:
        with open('info.json', 'w', encoding="utf-8") as f:
            f.write(json.dumps(info))
        return True
    except Exception as e:
        print(f"Error init info.json: {str(e)}")
        return False


def load_info_json():
    global info
    try:
        with open('info.json', 'r', encoding="utf-8") as f:
            info = json.load(f)
        return True
    except Exception as e:
        print(f"Error loading info.json: {str(e)}")
        return False

def update_info_json(args):
    global info
    info["meta"] ["object_name"] = args[0]
    info["meta"] ["cn_name"] = args[1]
    info["meta"] ["en_name"] = args[2]
    info["meta"] ["icon_path"] = args[3]
    try:
        with open('info.json', 'w', encoding="utf-8") as f:
            x = json.dumps(info)
            f.write(x)
        return True
    except Exception as e:
        print(f"Error update info.json: {str(e)}")
        return False

def copy_default_icon():
    try:
        shutil.copy2(os.path.join(img_path, "favicon.dds"),"favicon.dds")
        return True
    except Exception as e:
        print(f"Error copy favicon.dds: {str(e)}")
        return False


# produce
def produce_from_dirs(move = False):
    if not get_default_index():
        return False
    global default_index , work_index
    error_set = []
    noval_key = []
    work_index= [0 for _  in range(len(default_index))]
    this_output_path = os.path.join(output_path, obj_hash_name, r"sound\vo", obj_hash_name)
    if move and not os.path.exists(this_output_path):
        os.makedirs(this_output_path)
    try:
        for entry in os.scandir(voice_path):
            if entry.is_dir() and len(entry.name) >= 2 and entry.name[:2].isdigit():
                folder_index = int(entry.name[:2])
                count = 0
                for file in os.scandir(entry.path):
                    if file.is_file() and file.name.lower().endswith('.wav'):
                        count += 1
                        if move:
                            new_name = f"{default_index[folder_index][0]}_{count}.wav"
                            target_path = os.path.join(this_output_path, new_name)
                            shutil.copy2(file.path, target_path)
                    elif not move:
                        error_set.append(f"{file.path}不是.wav音频文件")
                work_index[folder_index] = count
            elif not move:
                error_set.append(f"{entry.path}是预期之外的文件")
        if not move:
            for i in range(len(default_index)):
                if work_index[i] == 0:
                    noval_key.append(default_index[i][1])
        return True, error_set, noval_key

    except Exception as e:
        print(f"Error producing mod from dirs: {str(e)}")
        return False, error_set, noval_key


def produce_from_csv(move = False):
    if not get_this_index():
        return False
    global default_index , work_index , this_index
    work_index.clear()
    error_set = []
    noval_key = []
    if not move:
        if not get_default_index():
            return False
        if len(this_index) != len(default_index):
            error_set.append(f"索引文件行数与默认索引存在差异，将按照索引文件处理")
        else:
            text = ""
            for i in range(len(this_index)):
                if this_index[i][0] != default_index[i][0]:
                    text += f" {i+1}"
            if len(error_set) > 0:
                error_set.append(f"索引文件{text} 行Key值与默认索引存在差异，将按照索引文件处理")
        if len(error_set) > 0:  # this index not as same as default one
            pattern = r'^[A-Za-z0-9_]+$'
            for i in range(len(this_index)):
                if not re.match(pattern, str(this_index[i][0])):
                    error_set[0] = "fatal"
                    return False, error_set, noval_key
    work_index = [0 for _ in range(len(this_index))]
    this_output_path = os.path.join(output_path, obj_hash_name, r"sound\vo", obj_hash_name)
    if move and not os.path.exists(this_output_path):
        os.makedirs(this_output_path)
    try:
        for i in range(len(this_index)):
            if len(this_index[i]) > 2:
                count = 0
                if move:
                    # temp fix for custom csv index write asset
                    default_index[i][0] = this_index[i][0]
                for col in range(2,len(this_index[i])):
                    if this_index[i][col] == "":
                        continue
                    file_path = os.path.join(voice_path, this_index[i][col])
                    if not file_path.lower().endswith('.wav'):
                        file_path += '.wav'
                    if not os.path.exists(file_path):
                        if not move:
                            error_set.append(f"找不到位于索引{i+2}{chr(ord('A')+col)}处名为{this_index[i][col]}的音频文件")
                    else:
                        count += 1
                        if move:
                            new_name = f"{this_index[i][0]}_{count}.wav"
                            target_path = os.path.join(this_output_path, new_name)
                            shutil.copy2(file_path, target_path)
                work_index[i] = count
        for i in range(len(this_index)):
            if work_index[i] == 0:
                noval_key.append(this_index[i][1])
        return True, error_set, noval_key
    except Exception as e:
        print(f"Error producing mod from csv: {str(e)}")
        return False, error_set, noval_key


# noinspection SpellCheckingInspection
def write_asset_from_work_index(volume = 1):
    global default_index , work_index , this_index , info
    path = os.path.join(output_path, obj_hash_name, "sound")
    if not os.path.exists(path):
        os.makedirs(path)
    if not info["internal"]["is_use_dirs"]:
        if not get_this_index():
            return False
        default_index.clear()
        this_index = default_index
    else:
        if not get_default_index():
            return False
    try:
        with open(os.path.join(path, f"{obj_hash_name}.asset"), "w") as f:
            f.write(f"### Reduced by {en_title}\n")

            f.write("### Reg effect\n")
            f.write("category = {\n"
                    "\tname = \"Voice\"\n"
                    "\tsoundeffects = {\n")
            for i in range(len(default_index)):
                if work_index[i] == 0:
                    continue
                f.write(f"\t\t{obj_hash_name}_{default_index[i][0]}\n")
            f.write("\t}\n"
                    "}\n")

            f.write("\n\n### Reg sound file\n")
            for i in range(len(default_index)):
                if work_index[i] == 0:
                    continue
                for t in range(work_index[i]):
                    f.write("sound = {\n")
                    f.write(f"\tname = \"{obj_hash_name}_{default_index[i][0]}_{t+1}\"\n")
                    f.write(f"\tfile = \"vo/{obj_hash_name}/{default_index[i][0]}_{t+1}.wav\"\n")
                    f.write("}\n")
                f.write("\n")

            f.write("\n### bind sound to effect\n")
            for i in range(len(default_index)):
                if work_index[i] == 0:
                    continue
                f.write("soundeffect = {\n")
                f.write(f"\tname = {obj_hash_name}_{default_index[i][0]}\n")
                f.write("\tsounds = {\n")
                for t in range(work_index[i]):
                    f.write("\t\tweighted_sound = { sound = "
                            +f"{obj_hash_name}_{default_index[i][0]}_{t+1} "
                            +"weight = 1000 }\n")
                f.write("\t}\n"
                        +f"\tvolume = {volume}\n"
                        +"\tmax_audible = 1\n"
                        +"\tmax_audible_behavior = fail\n"
                        +"}\n\n")

            f.write("\n### sound group\n")
            f.write("soundgroup = {\n")
            f.write(f"\tname = {obj_hash_name}\n\tsoundeffectoverrides ="+" {\n")
            for i in range(len(default_index)):
                if work_index[i] == 0:
                    continue
                f.write(f"\t\t{default_index[i][0]} = {obj_hash_name}_{default_index[i][0]}\n")
            f.write("\t}\n}\n")
        return True
    except Exception as e:
        print(f"Error writing asset: {str(e)}")
        return False


def write_i18n_yml():
    global info
    en_name = info["meta"]["en_name"]
    cn_name = info["meta"]["cn_name"]
    i18n_path = os.path.join(output_path, obj_hash_name, "localisation")
    if not os.path.exists(i18n_path):
        os.makedirs(i18n_path)
    shutil.rmtree(i18n_path, ignore_errors=True)
    try:
        os.makedirs(os.path.join(i18n_path, "english"))
        with io.open(os.path.join(i18n_path, "english", f"{obj_hash_name}_l_english.yml"), "w", encoding="utf-8-sig") as f:
            f.write(f"l_english:\n {obj_hash_name}: \"{en_name}\"")
        os.makedirs(os.path.join(i18n_path, "simp_chinese"))
        with io.open(os.path.join(i18n_path, "simp_chinese", f"{obj_hash_name}_l_simp_chinese.yml"), "w", encoding="utf-8-sig") as f:
            f.write(f"l_simp_chinese:\n {obj_hash_name}: \"{cn_name}\"")
        return True
    except Exception as e:
        print(f"Error writing i18n yml: {str(e)}")
        return False


def write_others():
    global info
    icon_path = os.path.join(output_path, obj_hash_name, r"gfx\interface\icons")
    txt_path = os.path.join(output_path, obj_hash_name, r"sound\advisor_voice_types")
    if not os.path.exists(icon_path):
        os.makedirs(icon_path)
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)
    try:
        shutil.copy2(info["meta"]["icon_path"], os.path.join(icon_path, f"{obj_hash_name}.dds"))
        with open(os.path.join(txt_path, f"advisor_voice_types_{obj_hash_name}.txt"), "w") as f:
            f.write(f"{obj_hash_name} = "+"{\n"
                    +f"\tname = \"{obj_hash_name}\"\n"
                    +f"\ticon = \""+r"gfx/interface/icons/"+f"{obj_hash_name}.dds\"\n"
                    +"\tplayable = {\n"
                    +"\t\talways = yes\n"
                    +"\t}\n"
                    +"\tweight = {\n"
                    +"\t\tbase = 0\n"
                    +"\t}\n}\n")
        return True
    except Exception as e:
        print(f"Error writing other file: {str(e)}")
        return False


# ui
# noinspection PyArgumentList
class Window(ttk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=BOTH, expand=YES)

        # img
        self.img = [
            ttk.PhotoImage(
                name="icon",
                file=img_path + r"\icon-64.png"
            ),
            ttk.PhotoImage(
                name="home",
                file=img_path + r"\home-64.png"
            ),
            ttk.PhotoImage(
                name="option",
                file=img_path + r"\option-64.png"
            ),
            ttk.PhotoImage(
                name="save",
                file=img_path + r"\save-64.png"
            ),
            ttk.PhotoImage(
                name="produce",
                file=img_path + r"\produce-64.png"
            ),
        ]

        # menu
        def about():
            Messagebox.show_info(
                title="关于",
                parent=root,
                message=f"{cn_title} {version}\n{en_title}\nby: {_copyright}\n"
                        + "遵循MIT许可证开源\n"
                        + "Icons by Icons8.com"
            )

        menubar = ttk.Menu(root)
        feedback = ttk.Menu(menubar, tearoff=False)
        url_steam = "https://steamcommunity.com/sharedfiles/filedetails/?id=3461135342"
        feedback.add_command(label="Steam社区", command=lambda: webbrowser.open(url_steam))
        # noinspection SpellCheckingInspection
        url_qq_group = ("http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=JjKgF6Qshvuuuze9JiaCm6xPVCKaHNLT&"
                        "authKey=pe64fotfEHDgrDbBPk9M9sG5oAaMqp4n%2F%2FCLBvOf7yJOn8r5i3MGZGdLHdYdlnuG&"
                        "noverify=0&group_code=658109215")
        feedback.add_command(label="QQ社群", command=lambda: webbrowser.open(url_qq_group))
        menubar.add_cascade(label="反馈", menu=feedback)

        tools = ttk.Menu(menubar, tearoff=False)
        url_blplab = "https://www.hiveworkshop.com/threads/blp-lab-v0-5-0.137599/"
        tools.add_command(label=".dds图片转换", command=lambda: webbrowser.open(url_blplab))
        url_ffmpeg = "https://ffmpeg.org/"
        tools.add_command(label=".wav音频转换", command=lambda: webbrowser.open(url_ffmpeg))
        url_gpt_sovtis = "https://github.com/RVC-Boss/GPT-SoVITS"
        tools.add_command(label="GPT-SoVITS", command=lambda: webbrowser.open(url_gpt_sovtis))
        menubar.add_cascade(label="工具", menu=tools)

        help_menu = ttk.Menu(menubar, tearoff=False)
        url_github = "https://github.com/LymoneLM/StellarisAdvisorAdvisor"
        help_menu.add_command(label="GitHub", command=lambda: webbrowser.open(url_github))
        help_menu.add_command(label="关于", command=about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        menubar.add_command(label="退出", command=root.quit)
        root.config(menu=menubar)

        # header
        hdr_frame = ttk.Frame(self, padding=20, bootstyle=SECONDARY)
        hdr_frame.grid(row=0, column=0, columnspan=3, sticky=EW)

        hdr_label = ttk.Label(
            master=hdr_frame,
            image="icon",
            bootstyle=(INVERSE, SECONDARY)
        )
        hdr_label.pack(side=LEFT)

        logo_text = ttk.Label(
            master=hdr_frame,
            text=f"{cn_title}",
            font=("Microsoft YaHei Mono", 28),
            bootstyle=(INVERSE, SECONDARY)
        )
        logo_text.pack(side=LEFT, padx=10)

        # action
        def sw_tag(button_no):
            for no in range(4):
                action_button[no].configure(bootstyle=INFO)
                table_page[no].pack_forget()
            action_button[button_no].configure(bootstyle=PRIMARY)
            table_page[button_no].pack(side=TOP, fill=BOTH, expand=YES, padx=0, pady=0)
            # page produce
            if button_no == 2 and var_object_name.get() == "":
                if os.path.exists("info.json"):
                    load_info_json()
                    var_object_name.set(info["meta"]["object_name"] if info["meta"]["object_name"] else "")
                    var_cn_name.set(info["meta"]["cn_name"] if info["meta"]["cn_name"] else "")
                    var_en_name.set(info["meta"]["en_name"] if info["meta"]["en_name"] else "")
                    var_icon_path.set(info["meta"]["icon_path"] if info["meta"]["icon_path"] else "")
                else:
                    sw_tag(1)
                    Messagebox.show_info(
                        parent=root,
                        title="提示",
                        message="未初始化，请先进行初始化"
                    )
                    append_log("未初始化，请先进行初始化")

        action_frame = ttk.Frame(self)
        action_frame.grid(row=1, column=0, sticky=NSEW)

        action_button = [
            ttk.Button(
                master=action_frame,
                image="home",
                text="主页",
                compound=TOP,
                bootstyle=PRIMARY,
                takefocus=False,
                command=lambda : sw_tag(0)
            ),
            ttk.Button(
                master=action_frame,
                image="save",
                text="初始化",
                compound=TOP,
                bootstyle=INFO,
                takefocus=False,
                command=lambda : sw_tag(1)
            ),
            ttk.Button(
                master=action_frame,
                image="produce",
                text="生成",
                compound=TOP,
                bootstyle=INFO,
                takefocus=False,
                command=lambda : sw_tag(2)
            ),
            ttk.Button(
                master=action_frame,
                image="option",
                text="选项",
                compound=TOP,
                bootstyle=INFO,
                takefocus=False,
                command=lambda : sw_tag(3)
            )
        ]

        for button in action_button:
            button.pack(side=TOP, fill=BOTH, ipadx=15, ipady=10)

        # function table
        table_frame = ttk.Frame(self,borderwidth=2, relief=SUNKEN, width=300)
        table_frame.grid(row=1, column=1, sticky=NSEW, pady=(0, 0))

        # make frame width unchangeable
        ttk.Label(table_frame,width=500,font=("Microsoft YaHei", 1)).pack(side=TOP, fill=X)

        table_page = [
            ttk.Frame(table_frame, padding=10),
            ttk.Frame(table_frame, padding=10),
            ttk.Frame(table_frame, padding=10),
            ttk.Frame(table_frame, padding=10)
        ]

        # page home
        home_readme = ttk.LabelFrame(
            master=table_page[0],
            text="简要使用说明",
            padding=(20, 5)
        )
        home_readme.pack(side=TOP, fill=X, padx=20, pady=10)

        readme = [
            "0.创意工坊下载请复制到其他文件夹再操作以免损失",
            "1.先进行初始化，然后按所选方式组织音频文件",
            "2.最后回到小助手填写信息并生成模组文件",
            "3.1415 9265 3589 7932 3846 2643",
            "4.详细说明可见根目录README",
            "5.其实这页是为了好看凑数的",
            "6.佬！请务必多做顾问模组",
            "7.如有问题，欢迎反馈",
        ]
        for i in readme:
            ttk.Label(home_readme, text=i, font=("Microsoft YaHei", 12), wraplength=400).pack(side=TOP, fill=X)

        # page init
        lf_use_dirs = ttk.Labelframe(
            master=table_page[1],
            text="音频文件组织方式",
            padding=(20, 5)
        )
        lf_use_dirs.pack(side=TOP, fill=X, padx=20, pady=10)

        var_is_use_dirs = ttk.BooleanVar(value=True)
        ttk.Checkbutton(lf_use_dirs, text="使用文件夹", state=NORMAL , variable=var_is_use_dirs,
                        onvalue=True, offvalue=False, bootstyle="round-toggle",
                        command=lambda : var_is_use_dirs.set(True)).pack(side=TOP, pady=2, fill=X)
        ttk.Checkbutton(lf_use_dirs, text="填写表格", state=NORMAL ,variable=var_is_use_dirs,
                        onvalue=False, offvalue=True, bootstyle="round-toggle",
                        command=lambda : var_is_use_dirs.set(False)).pack(side=TOP, pady=2, fill=X)
        var_is_use_dirs.set(True)

        lf_init_info = ttk.Labelframe(
            master=lf_use_dirs,
            text="说明",
            padding=(20, 5)
        )
        lf_init_info.pack(side=TOP, fill=X)
        ttk.Label(
            master=lf_init_info,
            text="“使用文件夹”方式，类似于顾问语音mod创建助手，通过不同的文件夹区分不同的语音条目。\n"
                 "“填写表格”方式，会生成一个表格，通过使用文件名填写表格对应语音条目，可以使文件管理更自由。",
            font=("Microsoft YaHei", 10),
            wraplength = 350
        ).pack(side=TOP, fill=X)

        lf_other_option = ttk.Labelframe(
            master=table_page[1],
            text="其他可选项",
            padding=(20, 5)
        )
        lf_other_option.pack(side=TOP, fill=X, padx=20, pady=10)

        var_need_descriptor_mod = ttk.BooleanVar(value=False)
        ttk.Checkbutton(lf_other_option,text="生成descriptor.mod描述文件(beta版未实装功能)",state=NORMAL,variable=var_need_descriptor_mod,
                        bootstyle="round-toggle").pack(side=TOP, pady=2, fill=X)

        def touch_init(flag):
            if os.path.exists(voice_path):
                f = Messagebox.okcancel(
                    parent=root,
                    title="警告",
                    message="该操作将会彻底清空根目录音频文件夹，丢失的文件可能彻底无法找回",
                    button = ["取消:secondary","确定:primary"],
                    alert=True
                )
                if f == "取消":
                    append_log("初始化操作取消")
                    return
            progress_step(start=True,length=3)
            if not delete_init():
                append_log("删除初始化文件时遇到错误，请重试",LogLvl.ERROR)
                return
            append_log("删除初始化文件",step=True)
            if flag:
                init_info_json([
                    var_is_use_dirs.get(),
                    var_need_descriptor_mod.get(),
                ])
                append_log("生成info.json",step=True)
                if var_is_use_dirs.get():
                    if not init_dirs():
                        append_log(f"生成{voice_path}目录时遇到错误，请重试",LogLvl.ERROR)
                        return
                    append_log(f"生成{voice_path}目录",step=True)
                else:
                    if not init_csv():
                        append_log("生成index.csv时遇到错误，请重试",LogLvl.ERROR)
                        return
                    append_log("生成index.csv",step=True)
                append_log("初始化完成，现在关闭小助手也不会丢失进度")
            progress_step(done=True)

        init_button_frame = ttk.Frame(table_page[1],padding=10)
        init_button_frame.pack(side=BOTTOM, fill=X, padx=20, pady=20, )

        delete_init_button_frame = ttk.Frame(init_button_frame,padding=0)
        delete_init_button_frame.pack(side=LEFT, fill=Y, padx=20, pady=20, expand=True)
        delete_init_button = ttk.Button(delete_init_button_frame, text="删除初始化", bootstyle=DANGER, takefocus=False,
                                        command=lambda: touch_init(False))
        ToolTip(delete_init_button, text="删除所有初始化产生的文件，使小助手回到最初状态\n（不会删除备份文件和已有输出）")
        delete_init_button.pack(side=BOTTOM, fill=X, expand=True)

        _init_button_frame = ttk.Frame(init_button_frame,padding=0)
        _init_button_frame.pack(side=RIGHT, fill=Y, padx=20, pady=20,expand=True)
        init_button =  ttk.Button(_init_button_frame,text="开始初始化",bootstyle=SUCCESS,takefocus=False,
                                  command=lambda : touch_init(True))
        init_button.pack(side=BOTTOM, fill=X, expand=True)

        #page product
        info_table_frame = ttk.Frame(table_page[2],padding=20)
        info_table_frame.pack(side=TOP, fill=X)

        def validate_input(s):
            if s=="":
                return True
            pattern = r'^[A-Za-z0-9_]+$'
            return bool(re.fullmatch(pattern, str(s)))

        var_object_name = ttk.StringVar()
        var_cn_name = ttk.StringVar()
        var_en_name = ttk.StringVar()
        var_icon_path = ttk.StringVar()

        ttk.Label(info_table_frame,text="内置项目名(支持大小写英文、数字和下划线)：").pack(side=TOP, fill=X)
        ttk.Entry(info_table_frame,textvariable=var_object_name,validate="focus",
                  validatecommand=lambda :validate_input(var_object_name.get())).pack(side=TOP, fill=X)

        ttk.Label(info_table_frame, text="顾问中文名(留空将使用内置项目名)：").pack(side=TOP, fill=X)
        ttk.Entry(info_table_frame, textvariable=var_cn_name).pack(side=TOP, fill=X)

        ttk.Label(info_table_frame, text="顾问英文名(留空将使用内置项目名)：").pack(side=TOP, fill=X)
        ttk.Entry(info_table_frame, textvariable=var_en_name).pack(side=TOP, fill=X)

        ttk.Label(info_table_frame, text="顾问图标文件名(方形.dds图片或者.png图片，留空将使用默认图标)：").pack(side=TOP, fill=X)
        ttk.Entry(info_table_frame, textvariable=var_icon_path).pack(side=TOP, fill=X)


        def touch_produce():
            # basic confirm
            def check_meta() -> bool:
                f = Messagebox.okcancel(
                    parent=root,
                    message="该操作将会开始生成模组，请确认音频文件已经组织完毕",
                    button=["取消:secondary", "确定:primary"],
                )
                if f == "取消":
                    append_log("模组生成操作取消")
                    return False
                if not validate_input(var_object_name.get()):
                    Messagebox.show_info(
                        parent=root,
                        title="非法输入",
                        message="内置项目名仅支持大小写英文、数字和下划线\n"
                                + "内置项目名允许留空，将使用默认项目名SAAProduct"
                    )
                    append_log("内置项目名输入非法，生成操作取消")
                    return False
                if var_object_name.get() == "":
                    append_log("内置项目名留空，将使用默认项目名SAAProduct")
                    var_object_name.set("SAAProduct")
                if var_cn_name.get() == "":
                    append_log(f"顾问中文名留空,将使用内置项目名{var_object_name.get()}")
                    var_cn_name.set(var_object_name.get())
                if var_en_name.get() == "":
                    append_log(f"顾问英文名留空，将使用内置项目名{var_object_name.get()}")
                    var_en_name.set(var_object_name.get())
                if var_icon_path.get() == "":
                    append_log(f"顾问图标文件名留空，将使用默认图标")
                    if not copy_default_icon():
                        append_log(f"拷贝默认图标文件是出现错误")
                        return False
                    var_icon_path.set(r"favicon.dds")
                if not os.path.exists(var_icon_path.get()):
                    append_log("顾问图标文件不存在，生成操作取消")
                    Messagebox.show_info(
                        parent=root,
                        title="顾问图标文件不存在",
                        message="无法访问顾问图标文件，请确认路径填写正确\n"
                                + "顾问图标文件名允许留空，将使用默认图标"
                    )
                    return False
                _, ext = os.path.splitext(var_icon_path.get())
                is_png = ext == ".png"
                if is_png:
                    append_log("检测到顾问图标为.png图片，更推荐使用.dds图片，但本次模组生成将继续进行",
                               log_lvl=LogLvl.WARN)
                elif ext == ".dds":
                    append_log("成功访问到顾问图标文件")
                else:
                    append_log("顾问图标文件为不支持的格式", log_lvl=LogLvl.WARN)
                    Messagebox.show_info(
                        parent=root,
                        title="顾问图标文件不存在",
                        message="顾问图标文件为不支持的格式\n"
                                + "请使用方形.dds图片或者.png图片\n"
                                + "顾问图标文件名允许留空，将使用默认图标"
                    )
                    return False
                return True

            if not check_meta():
                return
            # start produce

            # get hash
            global obj_hash_name
            obj_hash_name = f"{var_object_name.get()}_" + traverse_and_hash()[:8]

            progress_step(start=True,length=8)
            append_log(f"开始生成模组{obj_hash_name}")
            if not update_info_json([
                var_object_name.get(),
                var_cn_name.get(),
                var_en_name.get(),
                var_icon_path.get(),
            ]):
                append_log("info.json更新失败",log_lvl=LogLvl.ERROR)
            append_log("更新info.json",step=True)

            this_output_path = os.path.join(output_path, obj_hash_name)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            elif os.path.exists(this_output_path):
                append_log(fr"输出文件夹{this_output_path}已存在，新模组将清空覆盖")
                shutil.rmtree(this_output_path ,ignore_errors=True)

            # index
            def handle_error_set(_set) -> bool:
                count = len(error_set)
                append_log(f"索引存在{count}个错误", log_lvl=LogLvl.ERROR)
                text = ""
                for t in range(min(count, 20)):
                    text += text + error_set[t] + "\n"
                if count > 20:
                    text += "……"
                f = Messagebox.okcancel(
                    parent=root,
                    title=f"索引存在{count}个错误",
                    message=text+"\n点击确定将无视错误继续生成",
                    button=["取消:secondary", "确定:primary"],
                    alert=True
                )
                if f == "取消":
                    append_log("取消生成模组")
                    return False
                return True

            def handle_noval_key(_set) -> bool:
                count = len(noval_key)
                if count == len(default_index):
                    append_log(f"目录中未找到音频，生成任务取消", log_lvl=LogLvl.ERROR)
                    Messagebox.show_info(
                        parent=root,
                        title="无法找到音频，生成任务取消",
                        message=f"请检查音频文件是否正确放入{voice_path}对应文件夹\n"
                                + "音频文件必须是.wav音频文件\n"
                                + "请尝试备份文件后重新初始化小助手"
                    )
                    return False
                append_log(f"存在{count}个语音条目没有合法音频", log_lvl=LogLvl.WARN)
                text = ""
                for t in range(min(count, 20)):
                    text = text + noval_key[t] + "\n"
                if count > 20:
                    text += "……"
                f = Messagebox.okcancel(
                    parent=root,
                    title=f"存在{count}个语音条目没有合法音频",
                    message=text+"\n点击确定将无视错误继续生成",
                    button=["取消:secondary", "确定:primary"],
                    alert=True
                )
                if f == "取消":
                    append_log("取消生成模组")
                    return False
                return True

            append_log("开始索引文件",step=True)
            is_use_dirs = info["internal"]["is_use_dirs"]
            if is_use_dirs:
                append_log("本次将根据文件夹索引生成模组")
                x, error_set, noval_key= produce_from_dirs()
            else:
                append_log("本次将根据index.csv索引生成模组")
                x, error_set, noval_key = produce_from_csv()
                if not x and error_set[0] == "fatal":
                    append_log("索引文件存在错误，请检查索引文件",log_lvl=LogLvl.ERROR)
                    Messagebox.show_info(
                        parent=root,
                        title="索引文件错误",
                        message="索引文件存在错误，请检查索引文件"
                    )
                    return
            if not x:
                append_log("索引出错，请重试",log_lvl=LogLvl.ERROR)
            append_log("文件索引完成",step=True)
            if len(error_set) != 0 and not handle_error_set(error_set):
                return
            if len(noval_key) != 0 and not handle_noval_key(noval_key):
                return
            x = produce_from_dirs(move=True) if is_use_dirs else produce_from_csv(move=True)
            if not x:
                append_log("文件转移出错，请重试", log_lvl=LogLvl.ERROR)
            append_log("文件转移完成",step=True)

            # write asset
            if not write_asset_from_work_index():
                append_log("生成效果注册文件时出错，请重试",log_lvl=LogLvl.ERROR)
                return
            append_log("生成效果注册文件",step=True)
            if not write_i18n_yml():
                append_log("生成i18n文件时出错，请重试",log_lvl=LogLvl.ERROR)
                return
            append_log("生成i18n文件",step=True)
            if not write_others():
                append_log("生成其他配置文件时出错，请重试",log_lvl=LogLvl.ERROR)
                return
            append_log("生成其他配置文件",step=True)

            # produce done
            append_log(f"模组生成完成，位于{output_path}\\{obj_hash_name}",log_lvl=LogLvl.SUCCESS)
            Messagebox.show_info(
                parent=root,
                title="成功",
                message=f"模组生成完成，位于{output_path}\\{obj_hash_name}\n"
                        +f"感谢您使用{cn_title}，请在充分测试后发布模组，如有疑问烦请移步反馈"
            )
            append_log(f"感谢您使用{cn_title}，请在充分测试后发布模组，如有疑问烦请移步反馈")
            progress_step(done=True)



        product_button_frame = ttk.Frame(table_page[2],padding=40)
        product_button_frame.pack(side=BOTTOM, fill=X)
        product_button = ttk.Button(product_button_frame,text="生成顾问模组",takefocus=False,
                                    command=lambda : touch_produce())
        product_button.pack(side=BOTTOM, fill=X)


        # default page
        table_page[0].pack(fill=BOTH, expand=YES, padx=0, pady=0)

        # log
        class LogLvl(enum.Enum):
            DEBUG = 0,  # we should have debug mode, don't we?
            INFO = 1,
            WARN = 2,
            ERROR = 3,
            SUCCESS = 4,

        log_frame = ttk.Frame(self, bootstyle=SECONDARY)
        log_frame.grid(row=1, column=2, sticky=NSEW)

        # make frame width unchangeable
        ttk.Label(log_frame, width=400, font=("Microsoft YaHei", 1), bootstyle=SECONDARY).pack(side=TOP, fill=X)

        # progressbar
        pb_frame = ttk.Frame(log_frame, padding=(0, 0, 5, 5))
        pb_frame.pack(side=TOP, fill=X)
        pb = ttk.Progressbar(
            master=pb_frame,
            bootstyle=(SUCCESS, STRIPED),
            variable="var_progress"
        )
        pb.pack(side=LEFT, fill=X, expand=YES, padx=(15, 10))
        ttk.Label(pb_frame, text='%', bootstyle=SECONDARY).pack(side=RIGHT)
        # noinspection PyTypeChecker
        ttk.Label(pb_frame, textvariable="var_progress").pack(side=RIGHT)
        self.setvar("var_progress","100")

        progress_this = ttk.IntVar(value=0)
        progress_length = ttk.IntVar(value=10)
        def progress_step(start=False, done=False, **args):
            if start:
                pb.configure(bootstyle=(SUCCESS, STRIPED))
                self.setvar("var_progress", "0")
                progress_this.set(0)
                if "length" in args:
                    progress_length.set(args.get("length"))
                else:
                    progress_length.set(10)
            elif done:
                pb.configure(bootstyle=(SUCCESS, STRIPED))
                self.setvar("var_progress", "100")
            else:
                progress_this.set(progress_this.get()+1)
                self.setvar("var_progress", f"{int((progress_this.get()/progress_length.get())*100)}")


        log_count = ttk.IntVar(value=0)
        def append_log(log:str, log_lvl:LogLvl=LogLvl.INFO, step=False):
            if log_count.get() >= 20:
                log_label.append(ttk.Label(cl_frame, bootstyle=(DARK, INVERSE), text="", wraplength=380))
                log_label[log_count.get()].pack(side=TOP, fill=X)
            log_label[log_count.get()].configure(text=f"[{log_lvl.name}]{log}")
            if log_lvl != LogLvl.INFO:
                match log_lvl:
                    case LogLvl.WARN:
                        log_label[log_count.get()].configure(bootstyle=(WARNING, INVERSE))
                        pb.config(bootstyle=(WARNING, STRIPED))
                    case LogLvl.ERROR:
                        log_label[log_count.get()].configure(bootstyle=(DANGER, INVERSE))
                        pb.config(bootstyle=(DANGER, STRIPED))
                    case LogLvl.SUCCESS:
                        log_label[log_count.get()].configure(bootstyle=(SUCCESS, INVERSE))
                        pb.config(bootstyle=(SUCCESS, STRIPED))
            log_count.set(log_count.get() + 1)
            if step:
                progress_step()
            # roll frame to bottom
            cl_frame.yview_moveto(1.0)


        # cmd-like
        cl_frame = ScrolledFrame(log_frame,padding=5, bootstyle=DARK, autohide=False, relief=SUNKEN)
        cl_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        cl_label = ttk.Label(cl_frame, bootstyle=(DARK, INVERSE), text=f"[{LogLvl.INFO.name}]欢迎使用{cn_title} {version}", wraplength=380)
        cl_label.pack(side=TOP, fill=X)
        log_label = []
        for i in range(20):
            log_label.append(ttk.Label(cl_frame, bootstyle=(DARK, INVERSE), text="", wraplength=380))
            log_label[i].pack(side=TOP, fill=X)


if __name__ == "__main__":
    root = ttk.Window(
        title=f"{cn_title} {en_title} {version}",
        themename="yeti",
        iconphoto=img_path + r"\favicon-32.png",
        size=(1030,580),
        resizable=(False, False)
    )
    Window(root)
    root.mainloop()
