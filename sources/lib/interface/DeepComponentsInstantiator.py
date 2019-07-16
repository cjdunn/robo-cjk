"""
Copyright 2019 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
from vanilla import *
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *
from Helpers import deepolation

class DeepComponentsInstantiator(Group):

    def __init__(self, posSize, interface):
        super(DeepComponentsInstantiator, self).__init__(posSize)
        self.ui = interface

        segmentedElements = ["Select Deep Component", "New Deep Component"]
        self.deepCompo_segmentedButton = SegmentedButton((0,0,-0,20), 
                [dict(title=e, width = (550)/len(segmentedElements)) for e in segmentedElements],
                callback = self._deepCompo_segmentedButton_callback,
                sizeStyle='regular')
        
        self.selectDeepCompo = Group((0, 30,-0, -0))
        self.newDeepCompo = Group((0, 30,-0, -0))

        checkBox = CheckBoxListCell()
        self.selectDeepCompo.list = List((0, 0, 350, -0), [],
            columnDescriptions = [{"title": "Sel", "width":30, "cell":checkBox }, 
                                    {"title": "Name", "width":320}],
            drawFocusRing=False,
            editCallback = self._selectedDeepCompo_List_editCallback)

        slider = SliderListCell(minValue = 0, maxValue = 1000)
        self.newDeepCompo.list = List((0, 0, 350, -0), 
            [],
            columnDescriptions = [{"title": "Layer" }, 
                                    {"title": "Values", "cell": slider}],
            drawFocusRing=False, 
            editCallback = self._newDeepCompo_List_editCallback)

        self.deepCompo_segmentedButton.set(0)
        self.newDeepCompo.show(0)

        self.selectDeepCompo.addDeepCompo_button = SquareButton((-200, 0, -0, 30), 
            "Add", 
            sizeStyle = "small",
            callback = self._selectDeepCompo_addDeepCompo_callback)

        self.newDeepCompo.addDeepCompo_button = SquareButton((-200, 0, -0, 30), 
            "Add", 
            sizeStyle = "small",
            callback = self._newDeepCompo_addDeepCompo_callback)


    def _deepCompo_segmentedButton_callback(self, sender):
        sel = sender.get()
        self.selectDeepCompo.show(abs(sel-1))
        self.newDeepCompo.show(sel)

        if sel:
            self.ui.newDeepComponent_active = True
            self.ui.currentGlyph_DeepComponents['Existing'][self.ui.selectedVariantName] = []
            if self.ui.selectedVariantName in self.ui.currentGlyph_DeepComponents['NewDeepComponents']:

                storageFont = self.ui.font2Storage[self.ui.font]
                storageGlyph = storageFont[self.ui.selectedVariantName]
                if self.selectDeepCompo.list.getSelection():
                    ID = self.selectDeepCompo.list.get()[self.selectDeepCompo.list.getSelection()[0]]["Name"]
                    layersInfo = storageFont.lib["deepComponentsGlyph"][self.ui.selectedVariantName][ID]
                    values = [dict(Layer=layerName, Values=layersInfo[layerName] if layerName in layersInfo else 0) for layerName in storageGlyph.lib['deepComponentsLayer'] if layerName != "foreground"]
                else:
                    values = [dict(Layer=layerName, Values=0) for layerName in storageGlyph.lib['deepComponentsLayer'] if layerName != "foreground"]
                if 'Values' not in self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]:
                    self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName] = {'Values':values}

                self.setSliderList()
        else:
            self.ui.newDeepComponent_active = False
            self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName] = {}

        self.ui.updateViews()

    def setSliderList(self):
        
        if self.ui.selectedVariantName and self.ui.selectedVariantName in self.ui.currentGlyph_DeepComponents['NewDeepComponents']:
            values = []
            if "Values" in self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]:
                values = self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]['Values']
            self.newDeepCompo.list.set(values)
        else:
            self.newDeepCompo.list.set([])

    def _selectedDeepCompo_List_editCallback(self, sender):
        if not sender.get(): return
        if self.ui.selectedVariantName in self.ui.currentGlyph_DeepComponents['Existing']:
            newList = []
            currentDeepCompo_existing = self.ui.currentGlyph_DeepComponents['Existing'][self.ui.selectedVariantName]
            for item in sender.get():
                sel = item["Sel"]
                ID = item["Name"]
                for elem in currentDeepCompo_existing:
                    if ID == elem["ID"] and sel:
                        newList.append(elem)
            self.ui.currentGlyph_DeepComponents['Existing'][self.ui.selectedVariantName] = newList

        elif not self.ui.selectedVariantName in self.ui.currentGlyph_DeepComponents['Existing']:
            self.ui.currentGlyph_DeepComponents['Existing'][self.ui.selectedVariantName] = []

        currentDeepCompo_existing = self.ui.currentGlyph_DeepComponents['Existing'][self.ui.selectedVariantName]

        for item in sender.get():
            sel = item["Sel"]
            ID = item["Name"]
            if not sel: continue

            here = 0
            for elem in currentDeepCompo_existing:
                if ID == elem["ID"]:
                    here = 1

            if not here and sel:
                storageFont = self.ui.font2Storage[self.ui.font]
                layersInfo = storageFont.lib["deepComponentsGlyph"][self.ui.selectedVariantName][ID]
                offset_x, offset_Y = 0, 0

                newGlyph = deepolation(RGlyph(), storageFont[self.ui.selectedVariantName].getLayer("foreground"), layersInfo)
                newGlyph.moveBy((offset_x, offset_Y))

                currentDeepCompo_existing.append({"ID" : ID, "Offsets" : [offset_x, offset_Y], "Glyph" : newGlyph})

        self.ui.updateViews()

    def _newDeepCompo_List_editCallback(self, sender):

        if not sender.get(): return

        self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName] = {"Values":sender.get()}

        values = self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]["Values"]
        deepCompo_GlyphMaster = self.ui.font2Storage[self.ui.font][self.ui.selectedVariantName]

        newGlyph = deepolation(RGlyph(), deepCompo_GlyphMaster, layersInfo = {e["Layer"]:int(e["Values"]) for e in values})

        if not 'Offset' in self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]:
            self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]['Offsets'] = (0, 0)
        else:
            x, y = self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]
            newGlyph.moveBy((x, y))

        self.ui.currentGlyph_DeepComponents['NewDeepComponents'][self.ui.selectedVariantName]['Glyph'] = newGlyph
        self.ui.updateViews()

    def _selectDeepCompo_addDeepCompo_callback(self, sender):
        storageFont = self.ui.font2Storage[self.ui.font]
        for deepComp_Name in self.ui.currentGlyph_DeepComponents['Existing']:
            for desc in self.ui.currentGlyph_DeepComponents['Existing'][deepComp_Name]:
                glyph = desc['Glyph']
                offsets = desc['Offsets']
                ID = desc['ID']

                # if not deepComp_Name in storageFont.lib["deepComponentsGlyph"]:
                #     storageFont.lib["deepComponentsGlyph"][deepComp_Name] = {}

                if "deepComponentsGlyph" not in self.ui.glyph.lib:
                    self.ui.glyph.lib["deepComponentsGlyph"] = {}

                self.ui.glyph.lib["deepComponentsGlyph"][deepComp_Name] = (ID, offsets)

        self.ui.glyph.update()

        self.ui.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }

        self.selectDeepCompo.list.set( dict(Sel = 0, Name = item) for item in list(storageFont.lib["deepComponentsGlyph"][self.ui.selectedVariantName].keys()) )

        self.ui.getDeepComponents_FromCurrentGlyph()
        self.ui.updateViews()


    def _newDeepCompo_addDeepCompo_callback(self, sender):
        f = self.ui.font2Storage[self.ui.font]

        for deepComp_Name, desc in self.ui.currentGlyph_DeepComponents['NewDeepComponents'].items():
                
            glyph = desc['Glyph']
            offsets = desc['Offsets']
            values = desc['Values']

            if not deepComp_Name in f.lib["deepComponentsGlyph"]:
                f.lib["deepComponentsGlyph"][deepComp_Name] = {}

            i = 0
            while True:
                index = "_%s"%str(i).zfill(2)
                ID = deepComp_Name + index
                if ID not in f.lib["deepComponentsGlyph"][deepComp_Name]:
                    break
                i+=1
            
            f.lib["deepComponentsGlyph"][deepComp_Name][ID] = {value["Layer"]: int(value["Values"]) for value in values}

            if "deepComponentsGlyph" not in self.ui.glyph.lib:
                self.ui.glyph.lib["deepComponentsGlyph"] = {}

            self.ui.glyph.lib["deepComponentsGlyph"][deepComp_Name] = (ID, offsets)

        self.ui.glyph.update()
        f.update()
        self.ui.currentGlyph_DeepComponents = {
                                            'CurrentDeepComponents':{}, 
                                            'Existing':{}, 
                                            'NewDeepComponents':{},
                                            }

        self.ui.getDeepComponents_FromCurrentGlyph()
        self.ui.updateViews()
