import re, bpy
from bpy.types import Menu
from . import KEYMAP_DEFS, SLOT_ORDER


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

GENERATED_MENUS = []
def build_and_register_pies():
    unregister_generated_pies()
    prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences
    for p_index, pie in enumerate(prefs.pies):
        cls_name = f"DPM_MT_PIE_{p_index}_{re.sub('[^0-9A-Za-z_]+','_', pie.name)}"
        bl_idname = cls_name
        def make_draw(pi_idx):
            def draw(self, context):
                prefs = context.preferences.addons[__name__.split(".")[0]].preferences
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
    prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences
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

print("[DPM] Functions Loaded")