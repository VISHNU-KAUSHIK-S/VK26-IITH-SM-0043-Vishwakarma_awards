# CAD Model

The rover chassis is modelled in **FreeCAD** using a single Python macro, [rover_chassis.py](assets/rover_chassis.py). All dimensions are in mm.

[Back to README](README.md)

## Contents of the Model

| Area | Parts |
| --- | --- |
| Tracks | 2 chains with cleats, 1 drive sprocket, 1 idler, 3 road wheels per side |
| Inside the hull | Power supply, motor driver, 2 drive motors with encoders |
| On the deck | Raspberry Pi, ESP32, gas sensor, temperature and humidity sensor |
| Protective layer | See-through plate above the electronics |
| On top | LiDAR on a grey mount, thermal camera, normal camera |

## Option 1 - View on the Website (no install)

Open the live 3D viewer: [https://rover-chasis.vercel.app/](https://rover-chasis.vercel.app/)

Drag to rotate, scroll or pinch to zoom.

You can also open it from a terminal (PowerShell or CMD):

```
start https://rover-chasis.vercel.app/
```

On macOS use `open https://rover-chasis.vercel.app/`. On Linux use `xdg-open https://rover-chasis.vercel.app/`.

## Option 2 - View in FreeCAD

Requires FreeCAD 1.0 or newer.

### Step 1 - Download the file

Download [rover_chassis.py](assets/rover_chassis.py) from the `assets` folder. On the file page, click the download icon.

### Step 2 - Run the macro

**Method A - From inside FreeCAD**

1. Open FreeCAD.
2. Go to **File > Open** and choose `rover_chassis.py`.
3. Go to **Macro > Execute macro**.

**Method B - Add it as a macro using a command (Windows PowerShell)**

```powershell
copy "$env:USERPROFILE\Downloads\rover_chassis.py" "$env:APPDATA\FreeCAD\v1-1\Macro\rover.FCMacro"
```

Then in FreeCAD go to **Macro > Macros...**, select `rover` and click **Execute**.

The folder name `v1-1` depends on your FreeCAD version. To see your exact macro folder, open **Macro > Macros...** and read the **User Macros Location** line.

### Step 3 - View the model

The model builds in a few seconds and appears in an isometric view. It is also saved to your Documents folder as `rover_chassis.FCStd` and `rover_chassis.step`. Each part is a separate item in the Model tree, so parts can be hidden or moved one at a time. The hull, deck and protective layer are semi-transparent so the parts inside are visible.

The macro only runs in FreeCAD. The exported `.step` file opens in other CAD software (SolidWorks, Fusion 360, Onshape) and in free viewers such as [3dviewer.net](https://3dviewer.net).

## FEA (Stress Analysis) in FreeCAD

Run the rover macro first so the model is open. Analyse one part at a time, for example the base deck (`Base_Deck`). This keeps memory use low.

1. Click the part in the Model tree.
2. Switch to the **FEM** workbench using the workbench drop-down in the toolbar.
3. Click **Analysis container** to create a new analysis.
4. Add a solver: **FEM > Solve > CalculiX Standard**. In its properties set the analysis type to **Static**.
5. Add a material: **FEM > Materials > Solid material**. Choose **Aluminum 6061**, or enter these values: Young's modulus 68900 MPa, Poisson ratio 0.33, density 2700 kg/m3. Assign it to the part.
6. Add constraints:
   - **Fixed:** select the faces where the plate is bolted to the hull walls.
   - **Pressure or Force:** select the top face for the payload load. Example: a 3 kg payload at 5g shock is about 147 N, so pressure = 147 N divided by the top face area.
   - **Self weight (gravity):** pointing down.
7. Add a mesh: **FEM > FEM mesh from shape by Gmsh**. Use a maximum element size of about 10-25 mm to keep memory use low, then click **Apply**.
8. Select the solver and click **Run solver calculations**.
9. When it finishes, double-click the result in the tree and choose **Von Mises stress**. Take a screenshot of the colored plot.

**Safety factor** = material yield strength divided by the highest von Mises stress. For Al 6061-T6 the yield strength is about 276 MPa. A safety factor of 2 or more is acceptable for this rover.

## Files

| File | Description |
| --- | --- |
| [rover_chassis.py](assets/rover_chassis.py) | FreeCAD macro that builds the full chassis |
