# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI
from shiboken2 import wrapInstance
import maya.cmds as cmds


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("MainWindow")
        self.set_UI()

    # UI構成
    def set_UI(self):
        self.setWindowTitle("Object List")
        self.setGeometry(1100, 500, 500, 200)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    # ウィジェットを作成
    def create_widgets(self):
        # Base_Button
        self.addButton = QtWidgets.QPushButton("Add")
        self.removeButton = QtWidgets.QPushButton("Remove")
        self.infoButton = QtWidgets.QPushButton("Info")
        self.refreshButton = QtWidgets.QPushButton("Refresh")
        self.select_enable_CheckBox = QtWidgets.QCheckBox("Enable Select ", self)

        # Info Editorのウィジェット
        self.infoeditor = ClickableFrame(self)
        self.infoeditor.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.infoeditor.setLayout(QVBoxLayout())
        self.infoeditor.layout().addWidget(QLabel("Information Editor"))
        self.infoeditor.setVisible(True)  # Info Editorを最初から表示

        # テキストエディター
        self.text_editor = QPlainTextEdit(self)
        self.text_editor.setReadOnly(True)
        self.text_editor.setVisible(False)  # 最初は非表示

        # ClickableFrame にテキストエディターを渡す
        self.infoeditor.set_text_edit(self.text_editor)

    # レイアウトの作成
    def create_layout(self):
        # whole_layoutの中にすべて入れる
        self.whole_layout = QtWidgets.QVBoxLayout()

        # スクロールバーの作成
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.whole_layout.addWidget(scroll_area)

        # メインのオブジェクトリスト
        self.centralWidget = QtWidgets.QWidget()
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.addWidget(self.list)

        # メインボタンを下に配置
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.addWidget(self.addButton)
        self.bottom_layout.addWidget(self.removeButton)
        self.bottom_layout.addWidget(self.infoButton)
        self.bottom_layout.addWidget(self.refreshButton)

        # チェックボックスの配置
        self.bottom_layout.addWidget(self.select_enable_CheckBox)

        # wholewidgetの中のレイアウト
        scroll_area.setWidget(self.centralWidget)
        self.whole_layout.addWidget(self.infoeditor)
        self.whole_layout.addWidget(self.text_editor)
        self.whole_layout.addLayout(self.bottom_layout)

        # Info Editorの配置
        self.setLayout(self.whole_layout)

    # 接続の作成
    def create_connections(self):
        self.addButton.clicked.connect(self.addButton_onClicked)
        self.removeButton.clicked.connect(self.removeButton_onClicked)
        self.refreshButton.clicked.connect(self.refreshButton_onClicked)
        self.select_enable_CheckBox.stateChanged.connect(self.select_enable)
        self.infoButton.clicked.connect(self.infoButton_onClicked)
        self.infoeditor.clicked.connect(self.toggle_text_editor)
        self.list.itemSelectionChanged.connect(self.list_selection_changed)

    # addButtonの関数
    def addButton_onClicked(self):
        sl_obj = cmds.ls(selection=True, long=True)
        self.add_items_to_list(sl_obj)

    # removeButtonの関数
    def removeButton_onClicked(self):
        selected_items = self.list.selectedItems()
        self.remove_selected_items(selected_items)

    # select_enableの関数
    def select_enable(self):
        if self.select_enable_CheckBox.isChecked():
            cmds.select(clear=True)
            self.select_items_in_list()

    # refrshButtonの関数
    def refreshButton_onClicked(self):
        self.list.clear()
        print("Clear list")

    # infoButtonの関数
    def infoButton_onClicked(self):
        selected_items = self.list.selectedItems()
        self.update_info_editor(selected_items)

    # リストで選択するとMayaでも選択状態にする
    def list_selection_changed(self):
        selected_items = self.list.selectedItems()
        if self.select_enable_CheckBox.isChecked() and selected_items:
            cmds.select(clear=True)
            self.select_items_in_list(selected_items)

    # Info Editorをクリックしたときの処理
    def toggle_text_editor(self):
        current_visibility = self.text_editor.isVisible()
        self.text_editor.setVisible(not current_visibility)
        if current_visibility:
            selected_items = self.list.selectedItems()
            self.update_info_editor(selected_items)

    # オブジェクトをリストに追加
    def add_items_to_list(self, items):
        if items:
            for item in items:
                short_name = cmds.ls(item, shortNames=True)[0]
                self.list.addItem(short_name)
                print(f"Added: {short_name}")
        else:
            print("No objects in list selected")

    # 選択されたアイテムをリストから削除
    def remove_selected_items(self, selected_items):
        if selected_items:
            for item in selected_items:
                self.list.takeItem(self.list.row(item))
            print(f"{len(selected_items)} items removed from the list")
        else:
            print("No objects in list selected")

    # リスト内のアイテムをMayaで選択状態にする
    def select_items_in_list(self, items=None):
        if not items:
            items = [self.list.item(i) for i in range(self.list.count())]

        for item in items:
            cmds.select(item.text(), add=True)

    # Info Editorを更新
    def update_info_editor(self, selected_items):
        if self.text_editor:
            if selected_items:
                text = self.get_object_info(selected_items)
                self.text_editor.setPlainText(text)
            else:
                self.text_editor.setPlainText("No objects in list selected")
        else:
            print("Error: 'text_editor' is None.")

    # 選択されたオブジェクトの情報を取得
    def get_object_info(self, selected_items):
        text = ""
        for item in selected_items:
            translate = cmds.getAttr(item.text() + '.translate')[0]
            rotate = cmds.getAttr(item.text() + '.rotate')[0]
            scale = cmds.getAttr(item.text() + '.scale')[0]

            text += f"{item.text()}:\n"
            text += f"  Translate: {translate}\n"
            text += f"  Rotate: {rotate}\n"
            text += f"  Scale: {scale}\n\n"
        return text


# クリック可能なフレームを作成するクラス
class ClickableFrame(QFrame):
    clicked = Signal()

    def __init__(self, parent=None):
        super(ClickableFrame, self).__init__(parent)
        self.setMouseTracking(True)
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def update_info_editor(self, selected_items):
        if self.text_edit:
            text = self.get_object_info(selected_items)
            self.text_edit.setPlainText(text)
        else:
            print("Error: 'text_edit' is None.")

    def setVisible(self, visible):
        super(ClickableFrame, self).setVisible(visible)

    def set_text_edit(self, text_edit):
        self.text_edit = text_edit


# Maya のウィンドウ取得
def get_maya_window():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    widget = wrapInstance(int(ptr), QtWidgets.QWidget)
    return widget


# Maya 用の起動
def launch_from_maya():
    maya_window = get_maya_window()
    window = MainWindow(parent=maya_window)
    window.show()


launch_from_maya()
