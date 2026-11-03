# Avatar

Low-poly 3D VTuber model, built from scratch in Blender 5.2 for the live demo
(webcam → emotion model → avatar expression).

| File | Content |
|---|---|
| `vtuber_avatar.blend` | Working file: full body in T-pose, left/right symmetric |
| `previews/` | Front and side renders of the current state |

The reference images used while modelling (`reference/Front.png`, `Side.png`, `Upside.png`) were taken from the
internet and are **not** included in this repository. Blender shows them as missing images when the file is
opened elsewhere; the model itself is not affected.

## Plan

- Rig with the VRM humanoid skeleton (VRM Add-on for Blender), weight painting for head and neck
- Seven expressions, one per emotion class (neutral, happy, sad, angry, fearful, disgust, surprised)
- Export as `.vrm` and show it in a small `three-vrm` web viewer driven by the emotion model
