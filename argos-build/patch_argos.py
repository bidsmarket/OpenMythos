from pathlib import Path

main_path = Path("app/src/main/java/com/argos/mobile/MainActivity.kt")
gradle_path = Path("app/build.gradle.kts")
strings_path = Path("app/src/main/res/values/strings.xml")
capability_path = Path("app/src/main/java/com/argos/mobile/CapabilityInspector.kt")
localization_path = Path("app/src/main/java/com/argos/mobile/Localization.kt")

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

capability = capability_path.read_text(encoding="utf-8")
old_capability_header = "class CapabilityInspector(context: Context) {"
new_capability_header = "class CapabilityInspector(private val context: Context) {"
if capability.count(old_capability_header) != 1:
    raise SystemExit("CapabilityInspector constructor token not found exactly once")
capability = capability.replace(old_capability_header, new_capability_header, 1)
if capability.count("private val context: Context") != 1:
    raise SystemExit("CapabilityInspector Context property repair was not applied exactly once")
capability_path.write_text(capability, encoding="utf-8")

localization = localization_path.read_text(encoding="utf-8")
old_hmc_localizer = '''fun Context.localizedHmcReason(reason: String): String = getString(
    when (reason) {
        "No gyroscope samples" -> R.string.hmc_reason_no_samples
        "Insufficient or irregular IMU sampling" -> R.string.hmc_reason_irregular_sampling
        "Predicted exposure/row-time blur exceeds target budget" -> R.string.hmc_reason_blur_exceeds
        "Abrupt hand motion exceeds acceleration gate" -> R.string.hmc_reason_abrupt_motion
        "Motion within capture envelope" -> R.string.hmc_reason_stable
        else -> return reason
    }
)'''
new_hmc_localizer = '''fun Context.localizedHmcReason(reason: String): String = when (reason) {
    "No gyroscope samples" -> getString(R.string.hmc_reason_no_samples)
    "Insufficient or irregular IMU sampling" -> getString(R.string.hmc_reason_irregular_sampling)
    "Predicted exposure/row-time blur exceeds target budget" -> getString(R.string.hmc_reason_blur_exceeds)
    "Abrupt hand motion exceeds acceleration gate" -> getString(R.string.hmc_reason_abrupt_motion)
    "Motion within capture envelope" -> getString(R.string.hmc_reason_stable)
    else -> reason
}'''
if localization.count(old_hmc_localizer) != 1:
    raise SystemExit("localizedHmcReason expression-body defect not found exactly once")
localization = localization.replace(old_hmc_localizer, new_hmc_localizer, 1)
if "else -> return reason" in localization:
    raise SystemExit("Invalid expression-body return remains in Localization.kt")
localization_path.write_text(localization, encoding="utf-8")

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

print(
    "ARGOS 3.2.3 patch applied: telemetry moved into scroll panel; full-width square compact preview retained; "
    "CapabilityInspector Context and localized HMC fallback compile defects repaired."
)
