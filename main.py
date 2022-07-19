#   -*- coding = utf8 -*-
"""
    @ created on : 2022/7/18
"""
import re
import time

import ddddocr
import requests

Headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.141 Safari/537.36 '
}
PostData = {
    1: {'cxIf': 'ok', 'ksh': '12345678912345', 'brithday': '123456', 'data_sjm': '1234'},
    2: {'projectCode': '20100101', 'ksh': '12345678912345', 'sfzh': '123456', 'randCode': '1234', 'do': 'search'}
}  # 这里的birthday不是我拼错了，是前端程序员的锅，不能改

Cookie = {'PHPSESSID': ''}

Baseurl = {1: "https://zsxx.e21.cn/m/h/dataSearch.html", 2: "http://cx.e21.cn/"}

yzmurl = {1: "https://zsxx.e21.cn/global/gd.php", 2: "http://cx.e21.cn/global/gd_check.php"}

cxurl = {1: "https://zsxx.e21.cn/m/w/dataSearchPost.php", 2: "http://cx.e21.cn/statusSearch.php"}

encode = {1: "utf-8", 2: "GB2312"}

info = {'录取状态数据更新时间': '2022年07月18日18时', }

'''（１）“自由可投”：表示该考生所填报的批次还没开始投档，或者是考生的档案不符合投档条件未被投出，或者是投出去后又被学校退档，如是被学校退档，考生可以看到最近一次院校退档的理由。
（２）“已经投档”：表示省招办已将档案投给了院校，但院校还未下载投档信息。
（３）“院校在阅”：表示院校已下载了投档信息，正在审阅考生的电子档案。
（４）“院校预退”：表示该考生因种种原因院校不予录取，院校向省招办提出退档，对每一个预退档的考生，院校都会注明退档的理由。
（５）“院校预录”：表示院校准备拟录取该考生，已通过网络将拟录取名单提交给省招办，等待省招办网上录检审核。
（６）“录取”：表示考生网上录取信息经省招办录检通过。'''


def update():
    r = requests.get(url=Baseurl[2], headers=Headers)
    r.encoding = encode[2]
    t = r.text
    # print(t)
    rex1 = re.search(r">.*?录取状态数据最新上传时间:.*?(\d{4}年\d{2}月\d{2}日\d{2}时).*?<", t)  # 获取录取状态数据最新上传时间
    if rex1 is not None:
        info['录取状态数据更新时间'] = rex1.group(1)  # 更新info
    # print(info)


def Initialize(postId, postBirthday, line=1):
    # 获取cookie
    Cookie['PHPSESSID'] = requests.get(url=yzmurl[line]).cookies['PHPSESSID']
    # 完善postdata
    if line == 1:
        PostData[1]['ksh'] = postId
        PostData[1]['brithday'] = postBirthday
    else:
        PostData[2]['ksh'] = postId
        PostData[2]['sfzh'] = postBirthday


def identify_yzm(line=1):
    _jpg = requests.get(url=yzmurl[line], headers=Headers, cookies=Cookie).content
    _ocr = ddddocr.DdddOcr()
    result = _ocr.classification(_jpg)
    # print(result)
    return result


def inspect(value):
    if value is not None:
        print("有值")
    else:
        print("没有值")


def build_data_yzm(_yzm, line=1):
    if line == 1:
        PostData[1]['data_sjm'] = _yzm
    else:
        PostData[2]['randCode'] = _yzm


def cx(line=1):
    # 查询和验证码错误处理
    _a = 0
    while True:
        if _a >= 10:
            return None  # Todo 验证码一直错误
        # 验证码获取和构造data
        yzm = identify_yzm(line)
        build_data_yzm(yzm, line)
        # print(PostData[1])

        # 查询
        r = requests.post(url=cxurl[line], data=PostData[line], cookies=Cookie)
        dt = time.strftime("%Y-%m-%d %X")
        r.encoding = encode[line]
        t = r.text
        # 返回校验之验证码
        rex0 = re.search("随机码不正确", t)
        if rex0 is None:
            _a += 1
            break
    # 返回校验之输入信息
    rex1 = re.search("(您输入的报名号或出生年月日错误)", t)
    if rex1 is not None:
        return None  # Todo 报名号或出生年月日错误

    # 返回信息处理
    rex = {}
    if rex2 := re.search("<li>姓名:(.*?)</li>", t): rex['姓名'] = rex2.group(1)
    if rex3 := re.search("<li>报名号:(.*?)</li>", t): rex['报名号'] = rex3.group(1)
    if rex4 := re.search("<li>院校名称:(.*?)</li>", t): rex['院校名称'] = rex4.group(1)
    if rex5 := re.search("<li>专业名称:(.*?)</li>", t): rex['专业名称'] = rex5.group(1)
    if rex6 := re.search("<li>院校专业组或类别(.*?)</li>", t): rex['院校专业组或类别'] = rex6.group(1)
    if rex7 := re.search("<li>层次名称:(.*?)</li>", t): rex['层次名称'] = rex7.group(1)
    if rex8 := re.search("<li>考生状态:(.*?)</li>", t): rex['考生状态'] = rex8.group(1)
    return rex


if __name__ == '__main__':
    update()
    print("简介")  # todo 写简介
    print(f"录取状态数据更新时间: {info['录取状态数据更新时间']}")
    # i = os.system("pause")
    # i = os.system("cls")

    confirm = 'n'
    while confirm in ("n", "N"):
        Id = input("请输入14位高考准考证号(回车下一步): ")
        Birthday = input("请输入6位生日(回车下一步): ")

        print(F"准考证号:{Id}")
        print(F"生日:{Birthday}")
        confirm = input("请确认以上信息(y(回车)/n)：")

        while confirm not in ("y", "Y", "", "n", "N"):
            print("请确认无误!")
            print(F"准考证号:{Id}")
            print(F"生日:{Birthday}")
            confirm = input("请确认以上信息(y(回车)/n)：")

    Initialize(Id, Birthday, line=1)

    a = cx(line=1)
    print(a)

    # duration = 500  # millisecond
    # freq = 2440  # Hz
    # winsound.Beep(freq, duration)
    # time.sleep(600)
