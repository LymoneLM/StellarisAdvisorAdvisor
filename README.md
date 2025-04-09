# Stellaris Advisor Advisor 群星顾问模组小助手

基于Python编写的GUI交互开放式群星顾问语音模组制作工具

A Python-based open-ended GUI interactive tool for creating Stellaris advisor voice mods.

在群星顾问模组小助手诞生之前，社区内已存在同类工具，但是已长时间未更新，缺少对部分新版本语音条目的支持，并且存在不少硬编码错误。但由于该软件并未开源，错误无法修正，遂制作本工具。群星顾问模组小助手的设计有两大理念：

1.**简便**：在功能丰富的情况下尽可能使得程序文件和交互最简，由程序完成大部分工作；使得即使完全没有编程基础，或者不想理解蠢驴语的玩家也能很方便的制作顾问模组。

2.**开放**：极有可能修改的部分外置（key表），较有可能修改的部分公开（开源），使得即使出现问题使用者也可以很轻松的修补本工具不致产生太多麻烦。

求你了，把你最爱的声音（如果权利方同意的话）变成顾问模组吧！我想玩！至于机械重复的部分工作请交给群星顾问模组小助手吧！

## 详细使用说明 Help

### 省流：基本操作流程

初始化->填充文件夹/填写表格->填写模组信息->生成模组->复制生成的文件并上传

### 运行

两种启动方式可选，任选其一即可

#### [首选]通过可执行文件运行

双击`StellarisAdvisorAdvisor.exe`运行小助手，如无意外，这是本文件夹内唯一的.exe程序文件

可能在您的电脑中会显示为`StellarisAdvisorAdvisor`不含`.exe`，这是正常的

#### 通过Python源代码运行

//TODO:巨无敌详细的使用说明

## 其他 Others

### 关于索引

1. index.csv文件索引

   - 实际上csv索引支持填写路径，只不过需要相对目录.\voice填写
   - 如果在csv中填写的文件不以.wav结尾，小助手会尝试添加`.wav`后缀进行查找，因此填写时你可以省略后缀名（事实上由于`.WAV`和`.wav`都是合法后缀名，如果省略，请确保后缀名为小写）（同理如果报错`xxx.wav`文件找不到时，文件名后缀多了个`.wav`，可能就要考虑文件名是否填写规范了）
2. 目录文件索引
   - 尽管发现多余的文件被定义为一种`[ERROR]`,事实上这只是出于一种程序上的便利，实际上是提醒你去确认文件是否放错了目录
   - 实际上目录索引只依赖文件目录的前两位，因此你可以根据便利随意修改之后的文字；同时，如果自定义条目超过两位数，也会导致无法处理的错误（那大概会是有生之年系列）

### **如果群星添加了新的顾问语音条目**

打开根目录`.\.default\index.csv`在第一列的最后加上新条目的key值，对应第二列填上对应提示词（非必须）即可正常使用

### TODO

- [ ] 命令行运行模式   
- 尽管花了大时间写这个破UI，我可能还是会在之后更新，使得这个程序可以通过仅命令行的方式运行
- [ ] 在小助手内集成音频格式的转换（感觉是比较必要而且常见的需求）
- 引入或者调用设备上安装的FFmpeg吧，可能
- [ ] 根据输入的设定自动生成匹配的台词
- 如果引入生成式大语言模型API（例如DeepSeek），可能只需要开发一套引导词汇（听起来不错
- [ ] TTS自动生成语音
- 例如引入GPT-SoVITS，实现对其的批量调用，如何

## 注意 Attention

1. 创意工坊下载本工具请务必先移动到其他文件再操作，以免更新导致进度和文件丢失
2. 目前仍为测试版本，测试并不充分，基本功能可能仍存在重大问题，遇到**一切问题**都可以尝试提交反馈
3. 为保证兼容性，涉及到游戏的文件和路径尽可能采用纯英文字符，但是我英文不咋地，所以可能存语言层面的错误
4. 因为本意是同时直接发布源码进行运行，所以使用单文件编写，若因此产生的理解灾难我负全责（不是
5. UI文本为硬编码，如有本地化需求可以联系我催我升级i18n（这烂软件真的会有人用吗XD **The UI text is currently hard-coded. For localization requirements, feel free to contact me to request prioritization of i18n support upgrades.**
6. 本项目基于 [MIT License](./LICENSE) 许可证开源
7. 本项目遵守并建议用户使用时遵守[Paradox EULA](https://legal.paradoxplaza.com/eula)

## 致谢 Acknowledgments

*排名不分先后*

1. 感谢[汐斯特艾弗-Histerlife](https://space.bilibili.com/274423248)大佬制作的[【Stellaris模组制作】从入门到入门（附全语音素材）……](https://www.bilibili.com/opus/1019287282293669904)教程
2. 感谢[Ossanoda](https://steamcommunity.com/id/Ossanoda)佬提供的[顾问语音mod创建助手](https://steamcommunity.com/sharedfiles/filedetails/?id=2210919407)提供的灵感
3. 感谢[LianComder](https://space.bilibili.com/1781079400)提供的[语音顾问教程](https://www.bilibili.com/video/BV1XW4y1C7ZV)

