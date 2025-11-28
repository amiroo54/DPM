from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, EnumProperty

ARROW_LABELS = {
    "N": "↑",
    "S": "↓",
    "E": "→",
    "W": "←",
    "NE": "↗",
    "NW": "↖",
    "SE": "↘",
    "SW": "↙",
}

SLOT_ITEMS = [
    ("W", ARROW_LABELS["W"], "West/Left segment of the pie"),
    ("E", ARROW_LABELS["E"], "East/Right segment of the pie"),
    ("S", ARROW_LABELS["S"], "South/Bottom segment of the pie"),
    ("N", ARROW_LABELS["N"], "North/Top segment of the pie"),
    ("NW", ARROW_LABELS["NW"], "North-West segment of the pie"),
    ("NE", ARROW_LABELS["NE"], "North-East segment of the pie"),
    ("SW", ARROW_LABELS["SW"], "South-West segment of the pie"),
    ("SE", ARROW_LABELS["SE"], "South-East segment of the pie"),
]

SLOT_ORDER = [slot for slot, _, _ in SLOT_ITEMS]

MODE_ITEMS = [
    ('Window', "Global", "Always active"),
    ('3D View', "3D View", ""),
    ('Object Mode', "Object Mode", ""),
    ('Mesh', "Edit Mode", ""),
    ('Sculpt', "Sculpt Mode", ""),
    ('Pose', "Pose Mode", ""),
    ('Vertex Paint', "Vertex Paint Mode", ""),
    ('Weight Paint', "Weight Paint Mode", ""),
    ('Image Paint', "Texture Paint Mode", ""),
    ('Grease Pencil', "Grease Pencil Paint", ""),
    ('Node Editor', "Node Editor", ""),
    # add more if needed
]

KEYMAP_DEFS = {
    "Window": {"name": "Window", "space_type":'EMPTY'},
    "3D View": {"name": "3D View", "space_type":'VIEW_3D'},
    "Object Mode": {"name": "Object Mode", "space_type":'EMPTY'},
    "Mesh": {"name": "Mesh", "space_type":'EMPTY'},
    "Sculpt": {"name": "Sculpt", "space_type":'EMPTY'},
    "Pose": {"name": "Pose", "space_type":'EMPTY'},
    "Vertex Paint": {"name": "Vertex Paint", "space_type":'EMPTY'},
    "Weight Paint": {"name": "Weight Paint", "space_type":'EMPTY'},
    "Image Paint": {"name": "Image Paint", "space_type":'EMPTY'},
    "Grease Pencil": {"name": "Grease Pencil", "space_type":'EMPTY'},
    "Node Editor": {"name": "Node Editor", "space_type":'NODE_EDITOR'},
}


class PMAction(PropertyGroup):
    label: StringProperty(name="Label", default="Action")
    direction: EnumProperty(name="Direction", items=SLOT_ITEMS, default="N")
    icon: StringProperty(name="Icon", default="")
    code: StringProperty(name="Python Code", default="# bpy and context available\n")
    highlight: StringProperty(name="Highlight if (Python expr)", default="False")

class PMPie(PropertyGroup):
    name: StringProperty(name="Pie Name", default="New Pie")
    shortcut: StringProperty(name="Shortcut (e.g. Q, ALT+W, F3, NUMPAD_1)", default="")
    mode: EnumProperty(name="Mode", items=MODE_ITEMS, default='Window')
    enabled: BoolProperty(name="Enabled", default=True)
    export: BoolProperty(name="Include In Export", default=False)
    uid: StringProperty(name="UID", default="")
    actions: CollectionProperty(type=PMAction)
    collapsed: BoolProperty(name="Collapsed", default=False)


class DPM_AddonPreferences(AddonPreferences):
    bl_idname = __name__.split(".")[0]
    pies: CollectionProperty(type=PMPie)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Dynamic Pie Menu Manager — full Python actions")
        layout.label(text="WARNING: Python code in preferences executes in your Blender process. Only import configs you trust.")
        layout.separator()
        for i, pie in enumerate(self.pies):
            box = layout.box()
            
            header = box.row()
            
            row = header.row(align=True)
            row.alignment = 'LEFT'
            
            icon = 'TRIA_DOWN' if not pie.collapsed else 'TRIA_RIGHT'
            row.prop(pie, "collapsed", text="", icon=icon, emboss=False)
            
            row.prop(pie, "name", text="", emboss=False)
            header.prop(pie, "enabled", text="Enabled", toggle=True)
            header.prop(pie, "export", text="Mark for Export", toggle=True)
            ops = header.row(align=True)
            ops.operator("dpm.add_action", text="Add Action").pie_index = i
            ops.operator("dpm.remove_pie", text="Remove Pie").pie_index = i
            
            if not pie.collapsed:
                col = box.column(align=True)
                col.separator()
                
                header2 = col.row()
                header2.prop(pie, "shortcut")
                header2.prop(pie, "mode", text="")
                
                # actions
                for j, act in enumerate(pie.actions):
                    act_box = col.box()
                    r = act_box.row()
                    r.prop(act, "label", text="Label")
                    r.prop(act, "direction", text="Direction")
                    r.operator("dpm.remove_action", text="", icon='X').pie_index = i
                    
                    act_box.prop(act, "icon", text="Icon")
                    act_box.prop(act, "code", text="Code")
                    act_box.prop(act, "highlight", text="Highlight if")
            
        row = layout.row()
        row.operator("dpm.add_pie", text="Add New Pie")
        row.operator("dpm.refresh_shortcuts", text="Refresh Shortcuts")
        
        layout.separator()
        row2 = layout.row()
        row2.operator("dpm.export_selected", text="Export Selected Pies")
        row2.operator("dpm.import_pies", text="Import Pies")
        layout.label(text="Tip: set 'Include In Export' for pies you want to share.")
        layout.separator()
        layout.label(text="Security again: imported code runs in Blender. Do not import from untrusted sources.")