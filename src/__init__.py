bl_info = {
    "name": "Dynamic Pie Menu Manager",
    "author": "Amiroof",
    "version": (1, 2, 0),
    "blender": (5, 0, 0),
    "location": "Preferences → Add-ons → Dynamic Pie Menu Manager",
    "description": "Create custom pie menus with full Python actions, dynamic highlighting, per-mode keymaps, and import/export of configs. Credit to Polyfjord for the idea and ChatGPT for a bit of help.",
    "category": "Interface",
}


from .DPM_Prefs import *
from .DPM_Functions import *
from .DPM_Operators import *
from .DPM_IO import *
import bpy

classes = (
    PMAction, PMPie, DPM_AddonPreferences,
    DPM_OT_AddPie, DPM_OT_RemovePie, DPM_OT_AddAction, DPM_OT_RemoveAction,
    DPM_OT_ExecuteAction, DPM_OT_OpenPie, DPM_OT_RefreshShortcuts,
    DPM_OT_ExportSelected, DPM_OT_ImportPies
)

def register():
    unregister()
    for c in classes: bpy.utils.register_class(c)
    # ensure prefs exists
    try:
        _ = bpy.context.preferences.addons["DPM"].preferences
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
