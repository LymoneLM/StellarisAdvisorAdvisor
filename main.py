import os
import csv
import json
import enum
import re
import shutil
import hashlib

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame

# meta
cn_title = "群星顾问模组小助手"
en_title = "Stellaris Advisor Advisor"
version = "v1.0.0"
_copyright = "LymoneLM"

# constant
voice_path = r".\voice"
default_path = r".\.default"
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
    try:
        f = csv.reader(open("index.csv", encoding="utf-8"))
        next(f)
        for row in f:
            this_index.append(row)
        return True
    except Exception as e:
        print(f"Error processing index.csv: {str(e)}")
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
    except Exception as e:
        print(f"Error create {voice_path}: {str(e)}")
        return False
    try:
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
        f = open('info.json', 'w', encoding="utf-8")
        f.write(json.dumps(info))
        return True
    except Exception as e:
        print(f"Error init info.json: {str(e)}")
        return False


def load_info_json():
    global info
    try:
        info = json.load(open("info.json", encoding="utf-8"))
        return True
    except Exception as e:
        print(f"Error loading info.json: {str(e)}")
        return False

def update_info_json(args):
    global info
    meta = info.get("meta")
    meta["object_name"] = args[0]
    meta["cn_name"] = args[1]
    meta["en_name"] = args[2]
    meta["icon_path"] = args[3]
    info["meta"] = meta
    try:
        f = open('info.json', 'w', encoding="utf-8")
        f.write(json.dumps(info))
        return True
    except Exception as e:
        print(f"Error update info.json: {str(e)}")
        return False

# produce
def from_dirs_produce(move = False):
    global default_index , work_index
    work_index.clear()
    error_set = []
    noval_key = []
    work_index= [[0]]* len(default_index)   # no Value Key
    this_output_path = os.path.join(output_path, obj_hash_name, r"sound\vo", obj_hash_name)
    if not os.path.exists(this_output_path):
        os.makedirs(this_output_path)
    if not get_default_index():
        return False
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
                            work_index[folder_index].append(new_name)
                            target_path = os.path.join(this_output_path, new_name)
                            shutil.copy2(file.path, target_path)
                    elif not move:
                        error_set.append(f"{file.path}不是.wav音频文件")
                work_index[folder_index][0] = count
            elif not move:
                error_set.append(f"{entry.path}是预期之外的文件")
        noval_key.clear()
        for i in range(len(work_index)):
            if work_index[i][0] == 0:
                noval_key.append(default_index[i][1])
        # print(work_index)
        return True, error_set, noval_key

    except Exception as e:
        print(f"Error producing mod from dirs: {str(e)}")
        return False, error_set, noval_key


def from_csv_produce():
    print()
    # TODO:


def write_asset():
    print()
    # TODO:


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
        feedback.add_command(label="Steam社区", )
        feedback.add_command(label="QQ社群", )
        menubar.add_cascade(label="反馈", menu=feedback)
        help_menu = ttk.Menu(menubar, tearoff=False)
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
        ttk.Checkbutton(lf_other_option,text="生成descriptor.mod描述文件",state=NORMAL,variable=var_need_descriptor_mod,
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

        def touch_product():
            # basic confirm
            f = Messagebox.okcancel(
                parent=root,
                message="该操作将会开始生成模组，请确认音频文件已经组织完毕",
                button=["取消:secondary", "确定:primary"],
            )
            if f == "取消":
                append_log("模组生成操作取消")
                return
            if not validate_input(var_object_name.get()):
                Messagebox.show_info(
                    parent=root,
                    title="非法输入",
                    message="内置项目名仅支持大小写英文、数字和下划线\n"
                            +"内置项目名允许留空，将使用默认项目名SAAProduct"
                )
                append_log("内置项目名输入非法，生成操作取消")
                return
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
                var_icon_path.set(img_path+r"\favicon.dds")
            if not os.path.exists(var_icon_path.get()):
                append_log("顾问图标文件不存在，生成操作取消")
                Messagebox.show_info(
                    parent=root,
                    title="顾问图标文件不存在",
                    message="无法访问顾问图标文件，请确认路径填写正确\n"
                            + "顾问图标文件名允许留空，将使用默认图标"
                )
                return
            _,ext = os.path.splitext(var_icon_path.get())
            is_png = ext == ".png"
            if is_png:
                append_log("检测到顾问图标为.png图片，更推荐使用.dds图片，但本次模组生成将继续进行",log_lvl=LogLvl.WARN)
            elif ext == ".dds":
                append_log("成功访问到顾问图标文件")
            else:
                append_log("顾问图标文件为不支持的格式",log_lvl=LogLvl.WARN)
                Messagebox.show_info(
                    parent=root,
                    title="顾问图标文件不存在",
                    message="顾问图标文件为不支持的格式\n"
                            + "请使用方形.dds图片或者.png图片\n"
                            + "顾问图标文件名允许留空，将使用默认图标"
                )
                return

            # start produce

            # get hash
            global obj_hash_name
            obj_hash_name = f"{var_object_name.get()}_" + traverse_and_hash()[:8]

            append_log(f"开始生成模组{obj_hash_name}")
            if not update_info_json([
                var_object_name.get(),
                var_cn_name.get(),
                var_en_name.get(),
                var_icon_path.get(),
            ]):
                append_log("info.json更新失败",log_lvl=LogLvl.ERROR)
            append_log("更新info.json")


            this_output_path = os.path.join(output_path, obj_hash_name)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            elif os.path.exists(this_output_path):
                append_log(fr"输出文件夹{this_output_path}已存在，新模组将清空覆盖")
                shutil.rmtree(this_output_path ,ignore_errors=True)


            is_use_dirs = info["internal"]["is_use_dirs"]
            if is_use_dirs:
                append_log("本次将根据文件夹索引生成模组")
                append_log("开始索引文件")
                x,error_set, noval_key= from_dirs_produce()
                if not x:
                    append_log("索引出错，请重试",log_lvl=LogLvl.ERROR)

                if len(error_set) != 0:
                    count = len(error_set)
                    append_log(f"存在{count}个无效文件", log_lvl=LogLvl.WARN)
                    text = ""
                    for i in range(min(count,20)):
                        text += text + error_set[i] + "\n"
                    if count > 20:
                        text += "……"
                    f = Messagebox.okcancel(
                        parent=root,
                        title=f"存在{count}个无效文件",
                        message=text,
                        button=["取消:secondary", "继续生成:primary"],
                        alert=True
                    )
                    if f == "取消":
                        append_log("取消生成模组")
                        return

                if len(noval_key) != 0:
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
                        return
                    append_log(f"存在{count}个语音条目没有合法音频", log_lvl=LogLvl.WARN)
                    text = ""
                    for i in range(min(count, 20)):
                        text = text + noval_key[i] + "\n"
                    if count > 20:
                        text += "……"
                    f = Messagebox.okcancel(
                        parent=root,
                        title=f"存在{count}个语音条目没有合法音频",
                        message=text,
                        button=["取消:secondary", "继续生成:primary"],
                        alert=True
                    )
                    if f == "取消":
                        append_log("取消生成模组")
                        return
                x = from_dirs_produce(True)
                if not x:
                    append_log("文件转移出错，请重试", log_lvl=LogLvl.ERROR)

            else:
                append_log("本次将根据index.csv索引生成模组")
                append_log("开始索引文件")





        product_button_frame = ttk.Frame(table_page[2],padding=40)
        product_button_frame.pack(side=BOTTOM, fill=X)
        product_button = ttk.Button(product_button_frame,text="生成顾问模组",takefocus=False,
                                    command=lambda : touch_product())
        product_button.pack(side=BOTTOM, fill=X)


        # default page
        table_page[0].pack(fill=BOTH, expand=YES, padx=0, pady=0)

        # log
        class LogLvl(enum.Enum):
            DEBUG = 0,  # we should have debug mode, don't we?
            INFO = 1,
            WARN = 2,
            ERROR = 3,
            FATAL = 4,  # in fact, no use at all

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
        ttk.Label(pb_frame, textvariable="var_progress").pack(side=RIGHT)
        self.setvar("var_progress","100")

        progress_this = ttk.IntVar(value=0)
        progress_length = ttk.IntVar(value=10)
        def progress_step(start=False, done=False, **args):
            if start:
                pb.configure(bootstyle=(SUCCESS, STRIPED))
                self.setvar("var_progress", "0")
                if "length" in args:
                    progress_length.set(args.get("length"))
                else:
                    progress_length.set(10)
            elif done:
                pb.configure(bootstyle=(SUCCESS, STRIPED))
                self.setvar("var_progress", "100")
            else:
                progress_this.set(progress_this.get()+1)
                self.setvar("var_progress", f"{(progress_this.get()//progress_length.get())*100}")


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
            log_count.set(log_count.get() + 1)
            if step:
                progress_step()


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
    get_default_index()
    print(default_index)

    root = ttk.Window(
        title=f"{cn_title} {en_title} {version}",
        themename="yeti",
        iconphoto=img_path + r"\favicon-32.png",
        size=(1030,580),
        resizable=(False, False)
    )
    Window(root)
    root.mainloop()
