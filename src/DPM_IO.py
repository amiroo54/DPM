import os, json, uuid
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from . import DPM_Prefs, DPM_Functions

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
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
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
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
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
            if mode not in DPM_Prefs.KEYMAP_DEFS.keys():
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
        DPM_Functions.build_and_register_pies(); DPM_Functions.refresh_shortcuts()
        self.report({'INFO'}, f"Imported {len(pies)} pies (append={not self.mode_replace})")
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}