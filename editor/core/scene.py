from editor.widgets import KMBNodeGraphicScene


class KMBNodeScene():

    def __init__(self):
        self.scene_width = 16000
        self.scene_height = 16000
        self.graphic_scene = KMBNodeGraphicScene(self)
        self.graphic_scene.set_graphic_scene(self.scene_width,
                                             self.scene_height)
