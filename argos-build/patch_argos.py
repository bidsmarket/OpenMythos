from pathlib import Path

main_path = Path("app/src/main/java/com/argos/mobile/MainActivity.kt")
gradle_path = Path("app/build.gradle.kts")
strings_path = Path("app/src/main/res/values/strings.xml")

main = main_path.read_text(encoding="utf-8")
replacements = [
    (
        "        previewColumn.addView(previewFrame)\n        previewColumn.addView(telemetryPanel)\n        root.addView(previewColumn)",
        "        previewColumn.addView(previewFrame)\n        root.addView(previewColumn)",
    ),
    (
        "            } else LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, AdaptiveUi.previewFraction(widthDp))",
        "            } else LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(widthDp))",
    ),
    (
        "            else LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f - AdaptiveUi.previewFraction(widthDp))",
        "            else LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f)",
    ),
    (
        "        val actionBar = LinearLayout(this).apply {",
        "        telemetryPanel.layoutParams = LinearLayout.LayoutParams(\n"
        "            ViewGroup.LayoutParams.MATCH_PARENT,\n"
        "            ViewGroup.LayoutParams.WRAP_CONTENT\n"
        "        ).apply {\n"
        "            setMargins(0, dp(8), 0, dp(12))\n"
        "        }\n"
        "        panel.addView(telemetryPanel)\n\n"
        "        val actionBar = LinearLayout(this).apply {",
    ),
]
for old, new in replacements:
    if main.count(old) != 1:
        raise SystemExit(f"Expected source token not found exactly once: {old[:90]!r}")
    main = main.replace(old, new, 1)

required = [
    "overlayView.telemetryPanel = telemetryPanel",
    "panel.addView(telemetryPanel)",
    "cameraController?.captureOne",
    "exportCurrentSession()",
    "buildQuicklookStack()",
    "showHelpDialog()",
    "runCapabilityAudit",
]
for token in required:
    if token not in main:
        raise SystemExit(f"Required preserved functionality token missing: {token}")
if "previewColumn.addView(telemetryPanel)" in main:
    raise SystemExit("Telemetry panel remains attached to preview")
if main.count("panel.addView(telemetryPanel)") != 1:
    raise SystemExit("Telemetry panel must have exactly one scroll-panel parent")
main_path.write_text(main, encoding="utf-8")

gradle = gradle_path.read_text(encoding="utf-8")
for old, new in {
    'versionCode = 30200': 'versionCode = 30203',
    'versionName = "3.2.0-multilingual"': 'versionName = "3.2.3-telemetry-scroll"',
}.items():
    if gradle.count(old) != 1:
        raise SystemExit(f"Build identity token not found exactly once: {old}")
    gradle = gradle.replace(old, new, 1)
gradle_path.write_text(gradle, encoding="utf-8")

if strings_path.exists():
    strings = strings_path.read_text(encoding="utf-8")
    strings = strings.replace(
        "Acquisition status and motion telemetry below the camera preview",
        "Acquisition status and motion telemetry in the scrollable controls area",
    )
    strings_path.write_text(strings, encoding="utf-8")

print("ARGOS 3.2.3 patch applied: telemetry moved into scroll panel; full-width square compact preview retained.")
