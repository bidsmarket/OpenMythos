from pathlib import Path

capability_path = Path("app/src/main/java/com/argos/mobile/CapabilityInspector.kt")
localization_path = Path("app/src/main/java/com/argos/mobile/Localization.kt")

capability = capability_path.read_text(encoding="utf-8")
old_header = "class CapabilityInspector(context: Context) {"
new_header = "class CapabilityInspector(private val context: Context) {"
if capability.count(old_header) != 1:
    raise SystemExit("CapabilityInspector constructor token not found exactly once")
capability = capability.replace(old_header, new_header, 1)
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
localization_path.write_text(localization, encoding="utf-8")

print("Applied compile-only repairs required to establish the preserved-source lint baseline.")
