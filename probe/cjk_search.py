#!/usr/bin/env python3
"""在二进制里搜常用 UI 词（GBK/UTF-8/UTF-16LE），判断汉化是否落在文本层。
用法: python probe/cjk_search.py <file> [file...]"""
import sys

WORDS = ["开始", "退出", "设置", "帮助", "继续", "关卡", "得分", "音乐", "音效", "确定", "取消",
         "游戏", "磁力", "大冒险", "中文", "版本", "暂停", "重玩", "下一关", "菜单", "提示", "分数", "时间"]


def main(paths):
    for p in paths:
        d = open(p, 'rb').read()
        print(f'== {p} ({len(d)} B)')
        for enc in ('gbk', 'utf-8', 'utf-16le'):
            nz = {w: d.count(w.encode(enc)) for w in WORDS}
            nz = {w: c for w, c in nz.items() if c}
            print(f'   {enc:9s} total={sum(nz.values()):4d} {nz if nz else ""}')


if __name__ == '__main__':
    main(sys.argv[1:])
