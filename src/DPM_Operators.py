from bpy.types import Operator
from bpy.props import IntProperty
import bpy, uuid
from . import DPM_Functions

class DPM_OT_AddPie(Operator):
    bl_idname = "dpm.add_pie"
    bl_label = "Add Pie"
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
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
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
        if 0 <= self.pie_index < len(prefs.pies):
            prefs.pies.remove(self.pie_index)
        return {'FINISHED'}

class DPM_OT_AddAction(Operator):
    bl_idname = "dpm.add_action"
    bl_label = "Add Action"
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
        p = prefs.pies[self.pie_index]
        a = p.actions.add()
        return {'FINISHED'}

class DPM_OT_RemoveAction(Operator):
    bl_idname = "dpm.remove_action"
    bl_label = "Remove Action"
    pie_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
        p = prefs.pies[self.pie_index]
        if len(p.actions) > 0:
            p.actions.remove(len(p.actions)-1)
        return {'FINISHED'}

class DPM_OT_ExecuteAction(Operator):
    bl_idname = "dpm.execute_action"
    bl_label = "Execute Dynamic Pie Action"
    bl_options = {'INTERNAL'}
    pie_index: IntProperty()
    action_index: IntProperty()
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
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

class DPM_OT_OpenPie(Operator):
    bl_idname = "dpm.open_pie"
    bl_label = "Open Dynamic Pie"
    bl_options = {'INTERNAL'}
    pie_index: IntProperty()
    def execute(self, context):
        print(__name__)
        prefs = context.preferences.addons[__name__.split(".")[0]].preferences
        if self.pie_index < 0 or self.pie_index >= len(prefs.pies):
            return {'CANCELLED'}
        pie = prefs.pies[self.pie_index]
        if not pie.enabled:
            return {'CANCELLED'}
        bl_idname = DPM_Functions.GENERATED_MENUS[self.pie_index] if self.pie_index < len(DPM_Functions.GENERATED_MENUS) else None
        if not bl_idname:
            return {'CANCELLED'}
        bpy.ops.wm.call_menu_pie(name=bl_idname)
        return {'FINISHED'}

class DPM_OT_RefreshShortcuts(Operator):
    bl_idname = "dpm.refresh_shortcuts"
    bl_label = "Refresh Shortcuts"
    def execute(self, context):
        build_and_register_pies(); refresh_shortcuts()
        self.report({'INFO'}, "Pies rebuilt and shortcuts refreshed.")
        return {'FINISHED'}