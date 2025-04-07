import os
import shutil
import hashlib
import json
import csv
import ttkbootstrap as ttk
from ttkbootstrap import BooleanVar
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *

# meta
cn_title = "群星顾问模组小助手"
en_title = "Stellaris Advisor Advisor"
version = "v1.0.0"
_copyright = "LymoneLM"

# constant
voice_path = "./voice"
default_path = "./.default"
img_path = "./img"
backup_path = "./backup"
output_path = "./output"
hash_algorithm = "sha256"

# global variable
short_hash = ""
object_name = ""
# default_index = pd.DataFrame()
# this_index = pd.DataFrame()
# info_json = pd.DataFrame()


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


def calculate_total_hash(file_hashes):
    combined_hash = hashlib.new(hash_algorithm)
    for hash_val in sorted(file_hashes):
        combined_hash.update(hash_val.encode('utf-8'))
    return combined_hash.hexdigest()


def traverse_and_hash(root_dir=voice_path):
    file_hashes = []
    for roots, dirs, files in os.walk(root_dir):
        for file_name in files:
            file_path = os.path.join(roots, file_name)
            file_hash = get_file_hash(file_path)
            if file_hash:
                file_hashes.append(file_hash)
    total_hash = calculate_total_hash(file_hashes)
    return total_hash


# scan csv
# def get_index():   # pandas ver
#     try:
#         index_csv = pd.read_csv(default_path + "/index.csv", encoding="utf-8")
#         return index_csv
#     except Exception as e:
#         print(f"Error processing index.csv: {str(e)}")
#         return None


# file operate
# def init_dir(index):   # pandas ver
#     shutil.rmtree(voice_path, ignore_errors=True)
#     for i in range(0, index.shape[0] - 1):
#         os.makedirs(voice_path + "/{:0>2d}".format(i) + index.iat[i, 1])


def move_file_dir():
    print()
    #TODO:


def write_asset():
    if not os.path.exists(voice_path):
        os.makedirs(voice_path)


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
                file=img_path + "/icon-64.png"
            ),
            ttk.PhotoImage(
                name="home",
                file=img_path + "/home-64.png"
            ),
            ttk.PhotoImage(
                name="option",
                file=img_path + "/option-64.png"
            ),
            ttk.PhotoImage(
                name="save",
                file=img_path + "/save-64.png"
            ),
            ttk.PhotoImage(
                name="produce",
                file=img_path + "/produce-64.png"
            ),
        ]

        # menu
        def about():
            Messagebox.show_info(title="关于",
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
            "2.最后回到本程序填写信息并生成模组文件",
            "3.1415 9265 3589 7932 3846 2643",
            "4.详细说明可见根目录README.md",
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

        var_is_use_dirs = BooleanVar(value=True)
        cb_dirs = ttk.Checkbutton(lf_use_dirs, text="使用文件夹", state=NORMAL , variable=var_is_use_dirs,
                                onvalue=True, offvalue=False, bootstyle="round-toggle",
                                command=lambda : var_is_use_dirs.set(True))
        cb_csv = ttk.Checkbutton(lf_use_dirs, text="填写表格", state=NORMAL ,variable=var_is_use_dirs,
                                onvalue=False, offvalue=True, bootstyle="round-toggle",
                                command=lambda : var_is_use_dirs.set(False))
        var_is_use_dirs.set(True)
        cb_dirs.pack(side=TOP, pady=2, fill=X)
        cb_csv.pack(side=TOP, pady=2, fill=X)
        lf_init_info = ttk.Labelframe(
            master=lf_use_dirs,
            text="说明",
            padding=(20, 5)
        )
        lf_init_info.pack(side=TOP, fill=X)
        ttk.Label(
            master=lf_init_info,
            text="“使用文件夹”方式，类似于顾问语音mod创建助手，通过不同的文件夹区分不同的语音条目。\n"
            "“填写表格”方式，会生成一个表格，通过使用文件名填写表格对应条目，可以使文件管理更自由。",
            font=("Microsoft YaHei", 10),
            wraplength = 350
        ).pack(side=TOP, fill=X)

        # default page
        table_page[0].pack(fill=BOTH, expand=YES, padx=0, pady=0)

        # log
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
            variable="progress"
        )
        pb.pack(side=LEFT, fill=X, expand=YES, padx=(15, 10))
        ttk.Label(pb_frame, text='%', bootstyle=SECONDARY).pack(side=RIGHT)
        ttk.Label(pb_frame, textvariable="progress").pack(side=RIGHT)
        self.setvar("progress",100)

        # cmd-like
        cl_frame = ScrolledFrame(log_frame,padding=5, bootstyle=DARK, autohide=False, relief=SUNKEN)
        cl_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        cl_label = ttk.Label(cl_frame, bootstyle=(DARK, INVERSE), text=f">欢迎使用{cn_title} {version}", wraplength=380)
        cl_label.pack(side=TOP, fill=X)
        log_label = []
        for i in range(20):
            log_label.append(ttk.Label(cl_frame, bootstyle=(DARK, INVERSE), text="", wraplength=380))
            log_label[i].pack(side=TOP, fill=X)


if __name__ == "__main__":
    root = ttk.Window(
        title=f"{cn_title} {en_title} {version}",
        themename="yeti",
        iconphoto=img_path + "/favicon-32x32.png",
    )
    Window(root)
    root.mainloop()
