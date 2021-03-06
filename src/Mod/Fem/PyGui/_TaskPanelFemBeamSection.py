# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "_TaskPanelFemBeamSection"
__author__ = "Bernd Hahnebach"
__url__ = "http://www.freecadweb.org"

## @package TaskPanelFemBeamSection
#  \ingroup FEM

import FreeCAD
import FreeCADGui
from PySide import QtGui
from PySide import QtCore
import PyObjects._FemBeamSection


class _TaskPanelFemBeamSection:
    '''The TaskPanel for editing References property of FemBeamSection objects'''
    def __init__(self, obj):
        FreeCADGui.Selection.clearSelection()
        self.sel_server = None
        self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(FreeCAD.getHomePath() + "Mod/Fem/PyGui/TaskPanelFemBeamSection.ui")
        QtCore.QObject.connect(self.form.cb_crosssectiontype, QtCore.SIGNAL("activated(int)"), self.sectiontype_changed)
        QtCore.QObject.connect(self.form.if_rec_height, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.rec_height_changed)
        QtCore.QObject.connect(self.form.if_rec_width, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.rec_width_changed)
        QtCore.QObject.connect(self.form.if_circ_diameter, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.circ_diameter_changed)
        QtCore.QObject.connect(self.form.if_pipe_diameter, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.pipe_diameter_changed)
        QtCore.QObject.connect(self.form.if_pipe_thickness, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.pipe_thickness_changed)
        QtCore.QObject.connect(self.form.pushButton_Reference, QtCore.SIGNAL("clicked()"), self.add_references)
        self.form.list_References.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.form.list_References.connect(self.form.list_References, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.references_list_right_clicked)

        self.form.cb_crosssectiontype.addItems(PyObjects._FemBeamSection._FemBeamSection.known_beam_types)  # it is inside the class thus double _FemBeamSection

        self.get_beamsection_props()
        self.update()

    def accept(self):
        self.set_beamsection_props()
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        return True

    def reject(self):
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def get_beamsection_props(self):
        self.references = []
        if self.obj.References:
            self.tuplereferences = self.obj.References
            self.get_references()
        self.SectionType = self.obj.SectionType
        self.RectHeight = self.obj.RectHeight
        self.RectWidth = self.obj.RectWidth
        self.CircDiameter = self.obj.CircDiameter
        self.PipeDiameter = self.obj.PipeDiameter
        self.PipeThickness = self.obj.PipeThickness

    def set_beamsection_props(self):
        self.obj.References = self.references
        self.obj.SectionType = self.SectionType
        self.obj.RectHeight = self.RectHeight
        self.obj.RectWidth = self.RectWidth
        self.obj.CircDiameter = self.CircDiameter
        self.obj.PipeDiameter = self.PipeDiameter
        self.obj.PipeThickness = self.PipeThickness

    def update(self):
        'fills the widgets'
        index_crosssectiontype = self.form.cb_crosssectiontype.findText(self.SectionType)
        self.form.cb_crosssectiontype.setCurrentIndex(index_crosssectiontype)
        self.form.if_rec_height.setText(self.RectHeight.UserString)
        self.form.if_rec_width.setText(self.RectWidth.UserString)
        self.form.if_circ_diameter.setText(self.CircDiameter.UserString)
        self.form.if_pipe_diameter.setText(self.PipeDiameter.UserString)
        self.form.if_pipe_thickness.setText(self.PipeThickness.UserString)
        self.rebuild_list_References()

    def sectiontype_changed(self, index):
        if index < 0:
            return
        self.form.cb_crosssectiontype.setCurrentIndex(index)
        self.SectionType = str(self.form.cb_crosssectiontype.itemText(index))  # form returns unicode

    def rec_height_changed(self, base_quantity_value):
        self.RectHeight = base_quantity_value

    def rec_width_changed(self, base_quantity_value):
        self.RectWidth = base_quantity_value

    def circ_diameter_changed(self, base_quantity_value):
        self.CircDiameter = base_quantity_value

    def pipe_diameter_changed(self, base_quantity_value):
        self.PipeDiameter = base_quantity_value

    def pipe_thickness_changed(self, base_quantity_value):
        self.PipeThickness = base_quantity_value

    def get_references(self):
        for ref in self.tuplereferences:
            for elem in ref[1]:
                self.references.append((ref[0], elem))

    def references_list_right_clicked(self, QPos):
        self.form.contextMenu = QtGui.QMenu()
        menu_item = self.form.contextMenu.addAction("Remove Reference")
        if not self.references:
            menu_item.setDisabled(True)
        self.form.connect(menu_item, QtCore.SIGNAL("triggered()"), self.remove_reference)
        parentPosition = self.form.list_References.mapToGlobal(QtCore.QPoint(0, 0))
        self.form.contextMenu.move(parentPosition + QPos)
        self.form.contextMenu.show()

    def remove_reference(self):
        if not self.references:
            return
        currentItemName = str(self.form.list_References.currentItem().text())
        for ref in self.references:
            refname_to_compare_listentry = ref[0].Name + ':' + ref[1]
            if refname_to_compare_listentry == currentItemName:
                self.references.remove(ref)
        self.rebuild_list_References()

    def add_references(self):
        '''Called if Button add_reference is triggered'''
        # in constraints EditTaskPanel the selection is active as soon as the taskpanel is open
        # here the addReference button EditTaskPanel has to be triggered to start selection mode
        FreeCADGui.Selection.clearSelection()
        # start SelectionObserver and parse the function to add the References to the widget
        print_message = "Select Edges by single click on them to add them to the list"
        import FemSelectionObserver
        self.sel_server = FemSelectionObserver.FemSelectionObserver(self.selectionParser, print_message)

    def selectionParser(self, selection):
        # print('selection: ', selection[0].Shape.ShapeType, '  ', selection[0].Name, '  ', selection[1])
        if hasattr(selection[0], "Shape"):
            if selection[1]:
                elt = selection[0].Shape.getElement(selection[1])
                if elt.ShapeType == 'Edge':
                    if selection not in self.references:
                        self.references.append(selection)
                        self.rebuild_list_References()
                    else:
                        FreeCAD.Console.PrintMessage(selection[0].Name + ' --> ' + selection[1] + ' is in reference list already!\n')

    def rebuild_list_References(self):
        self.form.list_References.clear()
        items = []
        for ref in self.references:
            item_name = ref[0].Name + ':' + ref[1]
            items.append(item_name)
        for listItemName in sorted(items):
            self.form.list_References.addItem(listItemName)
