# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class UiForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 214)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(400, 214))
        Form.setMaximumSize(QtCore.QSize(16777215, 214))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.pymolObjectLabel = QtWidgets.QLabel(Form)
        self.pymolObjectLabel.setObjectName("pymolObjectLabel")
        self.gridLayout.addWidget(self.pymolObjectLabel, 3, 0, 1, 1)
        self.pdbFileBrowseButton = QtWidgets.QPushButton(Form)
        self.pdbFileBrowseButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pdbFileBrowseButton
                                     .sizePolicy().hasHeightForWidth())
        self.pdbFileBrowseButton.setSizePolicy(sizePolicy)
        self.pdbFileBrowseButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pdbFileBrowseButton.setObjectName("pdbFileBrowseButton")
        self.gridLayout.addWidget(self.pdbFileBrowseButton, 5, 2, 1, 1)
        self.enlightenEdit = QtWidgets.QLineEdit(Form)
        self.enlightenEdit.setObjectName("enlightenEdit")
        self.gridLayout.addWidget(self.enlightenEdit, 7, 1, 1, 1)
        self.outputBrowseButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputBrowseButton
                                     .sizePolicy().hasHeightForWidth())
        self.outputBrowseButton.setSizePolicy(sizePolicy)
        self.outputBrowseButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.outputBrowseButton.setObjectName("outputBrowseButton")
        self.gridLayout.addWidget(self.outputBrowseButton, 9, 2, 1, 1)
        self.radioLayout = QtWidgets.QHBoxLayout()
        self.radioLayout.setObjectName("radioLayout")
        self.pdbFileRadio = QtWidgets.QRadioButton(Form)
        self.pdbFileRadio.setObjectName("pdbFileRadio")
        self.radioLayout.addWidget(self.pdbFileRadio)
        self.pymolObjectRadio = QtWidgets.QRadioButton(Form)
        self.pymolObjectRadio.setObjectName("pymolObjectRadio")
        self.radioLayout.addWidget(self.pymolObjectRadio)
        spacerItem = QtWidgets.QSpacerItem(425, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.radioLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.radioLayout, 1, 0, 1, 3)
        self.pymolObjectCombo = QtWidgets.QComboBox(Form)
        self.pymolObjectCombo.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pymolObjectCombo.sizePolicy().hasHeightForWidth())
        self.pymolObjectCombo.setSizePolicy(sizePolicy)
        self.pymolObjectCombo.setObjectName("pymolObjectCombo")
        self.gridLayout.addWidget(self.pymolObjectCombo, 3, 1, 1, 2)
        self.pdbFileEdit = QtWidgets.QLineEdit(Form)
        self.pdbFileEdit.setObjectName("pdbFileEdit")
        self.gridLayout.addWidget(self.pdbFileEdit, 5, 1, 1, 1)
        self.outputLabel = QtWidgets.QLabel(Form)
        self.outputLabel.setObjectName("outputLabel")
        self.gridLayout.addWidget(self.outputLabel, 9, 0, 1, 1)
        self.enlightenLabel = QtWidgets.QLabel(Form)
        self.enlightenLabel.setObjectName("enlightenLabel")
        self.gridLayout.addWidget(self.enlightenLabel, 7, 0, 1, 1)
        self.pdbFileLabel = QtWidgets.QLabel(Form)
        self.pdbFileLabel.setObjectName("pdbFileLabel")
        self.gridLayout.addWidget(self.pdbFileLabel, 5, 0, 1, 1)
        self.amberLabel = QtWidgets.QLabel(Form)
        self.amberLabel.setObjectName("amberLabel")
        self.gridLayout.addWidget(self.amberLabel, 8, 0, 1, 1)
        self.amberBrowseButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amberBrowseButton
                                     .sizePolicy().hasHeightForWidth())
        self.amberBrowseButton.setSizePolicy(sizePolicy)
        self.amberBrowseButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.amberBrowseButton.setObjectName("amberBrowseButton")
        self.gridLayout.addWidget(self.amberBrowseButton, 8, 2, 1, 1)
        self.enlightenBrowseButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.enlightenBrowseButton
                                     .sizePolicy().hasHeightForWidth())
        self.enlightenBrowseButton.setSizePolicy(sizePolicy)
        self.enlightenBrowseButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.enlightenBrowseButton.setObjectName("enlightenBrowseButton")
        self.gridLayout.addWidget(self.enlightenBrowseButton, 7, 2, 1, 1)
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.runPrepButton = QtWidgets.QPushButton(Form)
        self.runPrepButton.setObjectName("runPrepButton")
        self.buttonsLayout.addWidget(self.runPrepButton)
        self.websiteButton = QtWidgets.QPushButton(Form)
        self.websiteButton.setObjectName("websiteButton")
        self.buttonsLayout.addWidget(self.websiteButton)
        self.gridLayout.addLayout(self.buttonsLayout, 11, 0, 1, 3)
        self.outputEdit = QtWidgets.QLineEdit(Form)
        self.outputEdit.setObjectName("outputEdit")
        self.gridLayout.addWidget(self.outputEdit, 9, 1, 1, 1)
        self.amberEdit = QtWidgets.QLineEdit(Form)
        self.amberEdit.setObjectName("amberEdit")
        self.gridLayout.addWidget(self.amberEdit, 8, 1, 1, 1)
        self.ligandLayout = QtWidgets.QHBoxLayout()
        self.ligandLayout.setObjectName("ligandLayout")
        self.ligandNameLabel = QtWidgets.QLabel(Form)
        self.ligandNameLabel.setObjectName("ligandNameLabel")
        self.ligandLayout.addWidget(self.ligandNameLabel)
        self.ligandNameEdit = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ligandNameEdit
                                     .sizePolicy().hasHeightForWidth())
        self.ligandNameEdit.setSizePolicy(sizePolicy)
        self.ligandNameEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.ligandNameEdit.setObjectName("ligandNameEdit")
        self.ligandLayout.addWidget(self.ligandNameEdit)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20,
                                            QtWidgets.QSizePolicy.Fixed,
                                            QtWidgets.QSizePolicy.Minimum)
        self.ligandLayout.addItem(spacerItem1)
        self.ligandChargeLabel = QtWidgets.QLabel(Form)
        self.ligandChargeLabel.setObjectName("ligandChargeLabel")
        self.ligandLayout.addWidget(self.ligandChargeLabel)
        self.ligandChargeEdit = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ligandChargeEdit
                                     .sizePolicy().hasHeightForWidth())
        self.ligandChargeEdit.setSizePolicy(sizePolicy)
        self.ligandChargeEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.ligandChargeEdit.setObjectName("ligandChargeEdit")
        self.ligandLayout.addWidget(self.ligandChargeEdit)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        self.ligandLayout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.ligandLayout, 10, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pymolObjectLabel.setText(_translate("Form", "PyMOL object"))
        self.pdbFileBrowseButton.setText(_translate("Form", "..."))
        self.outputBrowseButton.setText(_translate("Form", "..."))
        self.pdbFileRadio.setText(_translate("Form", "Choose from fi&le"))
        self.pymolObjectRadio.setText(_translate("Form",
                                                 "Choose from P&yMOL object"))
        self.outputLabel.setText(_translate("Form", "Output folder"))
        self.enlightenLabel.setText(_translate("Form", "Enlighten folder"))
        self.pdbFileLabel.setText(_translate("Form", "PDB file"))
        self.amberLabel.setText(_translate("Form", "AMBER folder"))
        self.amberBrowseButton.setText(_translate("Form", "..."))
        self.enlightenBrowseButton.setText(_translate("Form", "..."))
        self.runPrepButton.setText(_translate("Form", "Run PREP"))
        self.websiteButton.setText(_translate("Form", "Enlighten Website"))
        self.ligandNameLabel.setText(_translate("Form", "Ligand Name"))
        self.ligandChargeLabel.setText(_translate("Form", "Ligand Charge"))
