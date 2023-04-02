FROM python:3.9 
# python是官方鏡像的名稱,:後面是版本號,可以按ctrl點擊python轉到docker hub 的鏡像頁面，可以找到所有支持的標籤

WORKDIR /app
# workdir 指定了所有docker命令的工作路徑(working directory),注意是這個命令後的所有docker命令,如果這個命令不存在，docker會自動創建，這樣可以避免使用絕對路徑，或是手動cd切換路徑增加程式的可讀性

COPY . .
#將所有程序拷貝到docker鏡像中,copy<本地路徑> <目標路徑>,第一個 . 代表程序根目錄下的所有文件,第二個 . 代表當前的工作路徑,也就是之前指定的app目錄

RUN pip3 install -r requirements.txt
# 允許我們在創建鏡像時運行任意的 SHELL 命令 (例如:echo pwd cp rm ),這邊用pip install 來安裝 python 程序所有關聯

# 通過以上所有命令就可以完成一個docker鏡像的建立

CMD ["python3","app.py"]
# 用 CMD 來指定當 DOCKER 容器運行起來時要執行的命令, RUN是創建鏡像時使用的 , 而 CMD 是運行容器時使用的


# command line
# docker build -t my-finance . ---- 這邊的 -t 制定鏡創建鏡像的名稱為 "my-finance" ,  . 是告訴docker在當前目錄下尋找這個dockerfile 