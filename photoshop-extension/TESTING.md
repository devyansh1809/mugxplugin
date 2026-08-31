# MugX Plugin Testing Guide

## Prerequisites

1. **Photoshop CS6 or CC 2014+** installed
2. **CEP Debug Mode** enabled
3. **Test photos** in `D:/SublimationBag/Customer/Photo/`
4. **Test PSD template** with smart objects named `Photo_01`, `Photo_02`, etc.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/devyansh1809/mugxplugin.git
cd mugxplugin
git checkout pluginworkingbranch
```

### Step 2: Enable CEP Debug Mode

**Windows:**
- Open Registry Editor
- Navigate to `HKEY_CURRENT_USER\Software\Adobe\CSXS.\[version]`
- Create DWORD `PlayerDebugMode` = `1`

**macOS:**
```bash
defaults write com.adobe.CSXS.10 PlayerDebugMode 1
```

### Step 3: Install Plugin

Copy the `photoshop-extension` folder to:

**Windows:**
```
C:\Users\[User]\AppData\Roaming\Adobe\CEP\extensions\mugx-plugin
```

**macOS:**
```
~/Library/Application Support/Adobe/CEP/extensions/mugx-plugin
```

### Step 4: Restart Photoshop

Close and reopen Photoshop to load the plugin.

## Testing the Plugin

### Test 1: Panel Opens

1. Open Photoshop
2. Go to `Window > Extensions > MugX Plugin`
3. Verify the panel opens with all sections visible

**Expected:** Panel shows header, tabs, and all buttons

### Test 2: Photo Auto-Fill (Core Feature)

**Setup:**
1. Create folder: `D:/SublimationBag/Customer/Photo/`
2. Add 6 test photos named: `01.jpg`, `02.jpg`, `03.jpg`, `04.jpg`, `05.jpg`, `06.jpg`
3. Open a PSD template with smart objects: `Photo_01`, `Photo_02`, `Photo_03`, `Photo_04`, `Photo_05`, `Photo_06`

**Steps:**
1. Open the MugX plugin panel
2. Open your PSD template in Photoshop
3. Click the **"6 Photo"** button in the Auto-Fill section
4. Watch the progress bar and status message

**Expected Result:**
- Progress bar fills to 100%
- Status shows: `✓ Placed 6 photo(s)`
- All 6 smart objects are filled with photos
- Photos are placed in sequential order (01→Photo_01, 02→Photo_02, etc.)

### Test 3: Partial Fill

**Setup:** Same as Test 2, but only add 4 photos to the folder

**Steps:**
1. Open PSD template with 6 smart objects
2. Click **"6 Photo"** button

**Expected Result:**
- Status shows: `✓ Placed 4 photo(s), 2 frame(s) empty`
- First 4 smart objects filled, last 2 remain empty

### Test 4: Auto Color Correction

**Steps:**
1. Open a photo in Photoshop
2. Select the photo layer
3. Click **"🎨 Auto Correct"** button

**Expected:** Photo colors are automatically adjusted

### Test 5: Smooth Filter

**Steps:**
1. Open a photo in Photoshop
2. Select the photo layer
3. Click **"✨ Smooth"** button

**Expected:** Skin smoothing filter is applied

### Test 6: Swap Photos

**Setup:** PSD with at least 2 filled smart objects

**Steps:**
1. Ensure `Photo_01` and `Photo_02` have different photos
2. Click **"🔄 Swap Photo"** button

**Expected:** Photos in Photo_01 and Photo_02 exchange positions

### Test 7: Mirror Layer

**Steps:**
1. Select any layer in Photoshop
2. Click **"🪞 Mirror"** button

**Expected:** Layer is flipped horizontally

### Test 8: Settings Persistence

**Steps:**
1. Open Settings tab
2. Change Photo Folder path
3. Click **"💾 Save Settings"**
4. Close and reopen Photoshop
5. Open plugin panel again

**Expected:** Settings are preserved

## Troubleshooting

### Panel Doesn't Open

- Verify CEP debug mode is enabled
- Check that `manifest.xml` exists in `photoshop-extension/CSXS/`
- Restart Photoshop

### "No document open" Error

- Open a PSD file before using auto-fill
- Ensure the document has smart object layers

### "Layer not found" Error

- Verify smart object names match exactly: `Photo_01`, `Photo_02`, etc.
- Check that layers are not inside nested groups (or update the recursive search)

### Photos Not Placed

- Verify photo folder path in Settings matches actual location
- Ensure photos are JPG, JPEG, or PNG format
- Check that photos are named sequentially (01, 02, 03...)

## Test PSD Template Creation

To create a test template:

1. Create new document: 2000x2000px, 300 DPI
2. Add background layer
3. Create 6 rectangular shapes for photo frames
4. Convert each shape to smart object
5. Name them: `Photo_01`, `Photo_02`, `Photo_03`, `Photo_04`, `Photo_05`, `Photo_06`
6. Save as `Mug_6Photo_Test.psd`

## Success Criteria

✅ Panel opens and displays correctly
✅ Auto-fill places photos in sequential order
✅ Partial fill works (fewer photos than frames)
✅ Auto color correction applies
✅ Smooth filter applies
✅ Swap photos exchanges positions
✅ Mirror flips layer horizontally
✅ Settings persist across sessions
✅ Progress bar shows fill progress
✅ Status messages are clear and accurate

## Next Steps

After successful testing:

1. Create more PSD templates (1-8 photos, various designs)
2. Add background library
3. Implement element library (bokeh, text, clipart)
4. Add 3D mockup generation
5. Implement print preparation (A4 layout, mirroring)

## Support

For issues or questions, check:
- `README.md` - Project overview
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `PHASE2B_IMPLEMENTATION_SUMMARY.md` - Phase 2B features
