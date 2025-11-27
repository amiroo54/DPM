
bl_info = {
    "name": "Dynamic Pie Menu Manager",
    "author": "Amiroof",
    "version": (1, 2, 0),
    "blender": (5, 0, 0),
    "location": "Preferences → Add-ons → Dynamic Pie Menu Manager",
    "description": "Create custom pie menus with full Python actions, dynamic highlighting, per-mode keymaps, and import/export of configs. Credit to Polyfjord for the idea and ChatGPT for a bit of help.",
    "category": "Interface",
}

import bpy, json, re, uuid, os
from bpy.types import AddonPreferences, Operator, Menu, PropertyGroup
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, EnumProperty

# -----------------------------
# Utility: shortcut parsing
# -----------------------------
def parse_shortcut_string(s):
    if not s: return None, False, False, False
    parts = s.upper().split("+")
    ctrl = "CTRL" in parts or "CONTROL" in parts
    alt = "ALT" in parts
    shift = "SHIFT" in parts
    tokens = [p for p in parts if p not in ("CTRL", "CONTROL", "ALT", "SHIFT")]
    if not tokens: return None, ctrl, alt, shift
    key = tokens[-1]
    return key, ctrl, alt, shift

# -----------------------------
# ENUMs
# -----------------------------
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

# -----------------------------
# Data definitions
# -----------------------------
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

# -----------------------------
# Preferences UI
# -----------------------------
class DPM_AddonPreferences(AddonPreferences):
    bl_idname = __name__
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
# -----------------------------
# Operators for Prefs Editing
# -----------------------------
class DPM_OT_AddPie(Operator):
    bl_idname = "dpm.add_pie"
    bl_label = "Add Pie"
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        p = prefs.pies.add()
        p.name = f"Pie {len(prefs.pies)}"
        p.uid = str(uuid.uuid4())
        a = p.actions.add() 
        return {'FINISHED'}

class DPM_OT_RemovePie(Operator):
    bl_idname = "dpm.remove_pie"
    bl_label = "Remove Pie"
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        if 0 <= self.pie_index < len(prefs.pies):
            prefs.pies.remove(self.pie_index)
        return {'FINISHED'}

class DPM_OT_AddAction(Operator):
    bl_idname = "dpm.add_action"
    bl_label = "Add Action"
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        p = prefs.pies[self.pie_index]
        a = p.actions.add()
        return {'FINISHED'}

class DPM_OT_RemoveAction(Operator):
    bl_idname = "dpm.remove_action"
    bl_label = "Remove Action"
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        p = prefs.pies[self.pie_index]
        if len(p.actions) > 0:
            p.actions.remove(len(p.actions)-1)
        return {'FINISHED'}

# -----------------------------
# Generic action executor
# -----------------------------
class DPM_OT_ExecuteAction(Operator):
    bl_idname = "dpm.execute_action"
    bl_label = "Execute Dynamic Pie Action"
    bl_options = {'INTERNAL'}
    pie_index: IntProperty()
    action_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        try:
            pie = prefs.pies[self.pie_index]
            action = pie.actions[self.action_index]
        except Exception:
            self.report({'ERROR'}, "Action not found")
            return {'CANCELLED'}
        code = action.code or ""
        safe_globals = {"bpy": bpy, "context": context}
        try:
            exec(code, {"__builtins__": {}}, safe_globals) # Only giving access to bpy and context and ommiting access to builtins
        except Exception as e:
            self.report({'ERROR'}, f"Action failed: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}

# -----------------------------
# Pie menu registration generator
# -----------------------------
GENERATED_MENUS = []
def build_and_register_pies():
    unregister_generated_pies()
    prefs = bpy.context.preferences.addons[__name__].preferences
    for p_index, pie in enumerate(prefs.pies):
        cls_name = f"DPM_MT_PIE_{p_index}_{re.sub('[^0-9A-Za-z_]+','_', pie.name)}"
        bl_idname = cls_name
        def make_draw(pi_idx):
            def draw(self, context):
                prefs = context.preferences.addons[__name__].preferences
                try:
                    pie_local = prefs.pies[pi_idx]
                except Exception:
                    pie_local = None
                layout = self.layout
                pie_layout = layout.menu_pie()
                if not pie_local:
                    return
                for slot in SLOT_ORDER:
                    f = [(idx, act) for idx, act in enumerate(pie_local.actions) if act.direction == slot]
                    if f:
                        index, action = f[0]
                        label = action.label or f"Action {slot}"
                        highlight = False
                        try:
                            expr = action.highlight or "False"
                            highlight = bool(eval(expr, {"__builtins__": {}}, {"bpy": bpy, "context": context}))
                        except Exception:
                            highlight = False
                        icon = action.icon or "NONE"
                        op = pie_layout.operator("dpm.execute_action", text=label, depress=highlight, icon=icon)
                        op.pie_index = pi_idx; op.action_index = index
                    else:
                        pie_layout.separator()
            return draw
        menu_cls = type(cls_name, (Menu,), {"bl_idname": bl_idname, "bl_label": pie.name, "draw": make_draw(p_index)})
        bpy.utils.register_class(menu_cls)
        GENERATED_MENUS.append(bl_idname)

def unregister_generated_pies():
    global GENERATED_MENUS
    for name in GENERATED_MENUS:
        if hasattr(bpy.types, "name"):
            try:
                cls = getattr(bpy.types, "name")
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
    GENERATED_MENUS = []

# -----------------------------
# Operator to open a specific pie (bound to shortcuts)
# -----------------------------
class DPM_OT_OpenPie(Operator):
    bl_idname = "dpm.open_pie"
    bl_label = "Open Dynamic Pie"
    bl_options = {'INTERNAL'}
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        if self.pie_index < 0 or self.pie_index >= len(prefs.pies):
            return {'CANCELLED'}
        pie = prefs.pies[self.pie_index]
        if not pie.enabled:
            return {'CANCELLED'}
        bl_idname = GENERATED_MENUS[self.pie_index] if self.pie_index < len(GENERATED_MENUS) else None
        if not bl_idname:
            return {'CANCELLED'}
        bpy.ops.wm.call_menu_pie(name=bl_idname)
        return {'FINISHED'}

# -----------------------------
# Keymap binding / refresh (per-mode aware)
# -----------------------------
REGISTERED_KEYMAPS = []
def refresh_shortcuts():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    for (km, kmi) in REGISTERED_KEYMAPS:
        try: km.keymap_items.remove(kmi)
        except Exception: pass
    REGISTERED_KEYMAPS.clear()
    prefs = bpy.context.preferences.addons[__name__].preferences
    for idx, pie in enumerate(prefs.pies):
        if not pie.enabled: continue
        key, ctrl, alt, shift = parse_shortcut_string(pie.shortcut)
        if not key: continue

        km_name = pie.mode
        info = KEYMAP_DEFS.get(km_name)
        if not info:
            print(f"[DPM] Unknown keymap '{km_name}', using Window.")
            info = KEYMAP_DEFS["Window"]

        km = kc.keymaps.new(
            name       = info["name"],
            space_type = info["space_type"],
        )

        try:
            kmi = km.keymap_items.new("dpm.open_pie", key, 'PRESS', ctrl=ctrl, alt=alt, shift=shift)
            kmi.properties.pie_index = idx
            REGISTERED_KEYMAPS.append((km, kmi))
        except Exception:
            print(f"[DPM] Failed bind: {pie.shortcut} for pie '{pie.name}' in mode {pie.mode}")

# -----------------------------
# Refresh operator
# -----------------------------
class DPM_OT_RefreshShortcuts(Operator):
    bl_idname = "dpm.refresh_shortcuts"
    bl_label = "Refresh Shortcuts"
    def execute(self, context):
        build_and_register_pies(); refresh_shortcuts()
        self.report({'INFO'}, "Pies rebuilt and shortcuts refreshed.")
        return {'FINISHED'}

# -----------------------------
# Import / Export Operators
# -----------------------------
def pies_to_serializable(pies):
    out = []
    for p in pies:
        out.append({
            "name": p.name,
            "shortcut": p.shortcut,
            "mode": p.mode,
            "enabled": bool(p.enabled),
            "uid": p.uid or str(uuid.uuid4()),
            "actions": [
                {"label": a.label, "icon": a.icon, "direction": a.direction, "code": a.code, "highlight": a.highlight} for a in p.actions
            ]
        })
    return out

class DPM_OT_ExportSelected(Operator):
    bl_idname = "dpm.export_selected"
    bl_label = "Export Selected Pies"
    filepath: StringProperty(subtype='FILE_PATH')
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        selected = [p for p in prefs.pies if p.export]
        if not selected:
            self.report({'ERROR'}, "No pies marked for export (toggle 'Include In Export').")
            return {'CANCELLED'}
        data = pies_to_serializable(selected)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "pies": data}, f, indent=2)
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Exported {len(data)} pies to {self.filepath}")
        return {'FINISHED'}
    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = os.path.expanduser("~") + os.sep + "dpm_pies_export.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DPM_OT_ImportPies(Operator):
    bl_idname = "dpm.import_pies"
    bl_label = "Import Pies"
    filepath: StringProperty(subtype='FILE_PATH')
    mode_replace: BoolProperty(name="Replace existing pies", default=False, description="If enabled, imported pies replace all existing pies")
    def execute(self, context):
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                j = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            return {'CANCELLED'}
        pies = j.get("pies", [])
        prefs = context.preferences.addons[__name__].preferences
        if self.mode_replace:
            # clear
            while len(prefs.pies) > 0:
                prefs.pies.remove(0)
        # append pies, avoid uid collisions by generating new uid if exists
        for pd in pies:
            p = prefs.pies.add()
            p.name = pd.get("name", "Imported Pie")
            p.shortcut = pd.get("shortcut", "")
            mode = pd.get("mode", "Window")
            if mode not in KEYMAP_DEFS.keys():
                p.mode = "Window"
            else:
                p.mode = mode
            p.enabled = bool(pd.get("enabled", True))
            proposed_uid = pd.get("uid", str(uuid.uuid4()))
            # ensure unique
            existing_uids = {x.uid for x in prefs.pies if x.uid}
            if proposed_uid in existing_uids:
                proposed_uid = str(uuid.uuid4())
            p.uid = proposed_uid
            for actd in pd.get("actions", []):
                a = p.actions.add()
                a.label = actd.get("label", "Action")
                a.direction = actd.get("direction", "N")
                a.icon = actd.get("icon", "NONE")
                a.code = actd.get("code", "# python")
                a.highlight = actd.get("highlight", "False")
        build_and_register_pies(); refresh_shortcuts()
        self.report({'INFO'}, f"Imported {len(pies)} pies (append={not self.mode_replace})")
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# -----------------------------
# Registration
# -----------------------------
classes = (
    PMAction, PMPie, DPM_AddonPreferences,
    DPM_OT_AddPie, DPM_OT_RemovePie, DPM_OT_AddAction, DPM_OT_RemoveAction,
    DPM_OT_ExecuteAction, DPM_OT_OpenPie, DPM_OT_RefreshShortcuts,
    DPM_OT_ExportSelected, DPM_OT_ImportPies
)

def register():
    for c in classes: bpy.utils.register_class(c)
    # ensure prefs exists
    try:
        _ = bpy.context.preferences.addons[__name__].preferences
    except Exception:
        pass
    build_and_register_pies(); refresh_shortcuts()
    print("[DPM] Registered with import/export")

def unregister():
    for (km, kmi) in list(REGISTERED_KEYMAPS):
        try: km.keymap_items.remove(kmi)
        except Exception: pass
    REGISTERED_KEYMAPS.clear()
    unregister_generated_pies()
    for c in reversed(classes):
        try: bpy.utils.unregister_class(c)
        except Exception: pass
    print("[DPM] Unregistered")

if __name__ == "__main__":
    register()
