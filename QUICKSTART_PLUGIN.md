# MugX Plugin - Quick Start Guide

## 🚀 Quick Test (5 Minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/devyansh1809/mugxplugin.git
cd mugxplugin
git checkout pluginworkingbranch
```

### Step 2: Enable CEP Debug Mode

**Windows:**
```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Adobe\CSXS.10]
"PlayerDebugMode"="1"
```

Save as `enable_cep.reg` and double-click to import.

**macOS:**
```bash
defaults write com.adobe.CSXS.10 PlayerDebugMode 1
```

### Step 3: Install Plugin

**Windows:**
```bash
# Copy to CEP extensions folder
xcopy /E /I photoshop-extension "%APPDATA%\Adobe\CEP\extensions\mugx-plugin"
```

**macOS:**
```bash
mkdir -p ~/Library/Application\ Support/Adobe/CEP/extensions
cp -r photoshop-extension ~/Library/Application\ Support/Adobe/CEP/extensions/mugx-plugin
```

### Step 4: Create Test Data

**Create photo folder:**
```
D:\SublimationBag\Customer\Photo\
```

**Add test photos:**
- `01.jpg` (any photo)
- `02.jpg` (any photo)
- `03.jpg` (any photo)
- `04.jpg` (any photo)
- `05.jpg` (any photo)
- `06.jpg` (any photo)

**Create test PSD:**
1. Open Photoshop
2. New document: 2000x2000px, 300 DPI
3. Create 6 smart objects
4. Name them: `Photo_01`, `Photo_02`, `Photo_03`, `Photo_04`, `Photo_05`, `Photo_06`
5. Save as: `D:\SublimationBag\Templates\Mug_6Photo_Test.psd`

### Step 5: Test in Photoshop

1. **Restart Photoshop**
2. **Open template:** `D:\SublimationBag\Templates\Mug_6Photo_Test.psd`
3. **Open plugin:** `Window > Extensions > MugX Plugin`
4. **Click:** "6 Photo" button
5. **Expected:** All 6 smart objects filled with photos

## ✅ Success Indicators

- ✅ Panel opens with purple header
- ✅ All buttons visible and clickable
- ✅ Progress bar fills when clicking photo count
- ✅ Status shows: "✓ Placed 6 photo(s)"
- ✅ Smart objects contain photos in order

## ❌ Troubleshooting

### Panel doesn't open
- Verify CEP debug mode enabled
- Restart Photoshop
- Check `manifest.xml` exists in `photoshop-extension/CSXS/`

### "No document open" error
- Open PSD template before clicking auto-fill

### "Layer not found" error
- Verify smart object names: `Photo_01`, `Photo_02`, etc.
- Check spelling and case sensitivity

### Photos not placed
- Verify photo folder path in Settings tab
- Ensure photos are JPG, JPEG, or PNG
- Check photos are named: `01.jpg`, `02.jpg`, etc.

## 🧪 Run Python Tests

```bash
cd mugxplugin
python -m pytest tests/test_plugin_integration.py -v
```

**Expected:** 15+ tests pass

## 📋 Test Checklist

- [ ] Panel opens
- [ ] 6 Photo button works
- [ ] Photos placed in order
- [ ] Partial fill works (try with 4 photos)
- [ ] Auto Correct applies
- [ ] Smooth applies
- [ ] Swap Photo works
- [ ] Mirror works
- [ ] Settings save and persist

## 🎯 Next Steps

After successful testing:

1. Create more PSD templates
2. Add background library
3. Implement element library
4. Add 3D mockup generation
5. Implement print preparation

## 📖 Documentation

- `TESTING.md` - Detailed test guide
- `PHASE3_IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `README.md` - Project overview

## 🐛 Issues?

Check `TESTING.md` for detailed troubleshooting or open an issue on GitHub.
