# Sample Medical Images for Endpoint Testing

Public-domain or openly licensed images for exercising `POST /reports`. These are **not real patient data from this project** — they are third-party samples for development only.

| File | Modality | Body part | License |
|------|----------|-----------|---------|
| `mri_lumbar_spine.jpg` | MRI | lumbar spine | [CC0](https://commons.wikimedia.org/wiki/File:Lumbar_MRI_t2-tse-rst-sagittal_10.jpg) |
| `mri_lumbar_herniation.png` | MRI | lumbar spine (L4-L5) | [CC0](https://commons.wikimedia.org/wiki/File:Hernie_discale_L4_L5.png) |
| `mri_mra_slice.png` | MRI | torso (MRA slice) | [ODC-Attribution 1.0](https://physionet.org/content/images/1.0.0/) |
| `ct_brain.png` | CT | brain | [CC0](https://commons.wikimedia.org/wiki/File:Computed_tomography_of_human_brain_-_large.png) |
| `xray_chest_pa.png` | XRAY | chest | [CC0](https://commons.wikimedia.org/wiki/File:Chest_Xray_PA_3-8-2010.png) |
| `xray_chest_normal.jpg` | XRAY | chest | [CC0](https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg) |

## Quick test (server running on :8000)

```powershell
# Lumbar spine MRI
curl.exe -X POST http://127.0.0.1:8000/reports `
  -F "image=@testdata/images/mri_lumbar_spine.jpg" `
  -F 'metadata={"modality":"MRI","body_part":"lumbar spine","clinical_context":"chronic low back pain with left leg radiculopathy"}'

# Chest X-ray
curl.exe -X POST http://127.0.0.1:8000/reports `
  -F "image=@testdata/images/xray_chest_pa.png" `
  -F 'metadata={"modality":"XRAY","body_part":"chest","clinical_context":"post-trauma screening after soccer collision"}'

# Head CT
curl.exe -X POST http://127.0.0.1:8000/reports `
  -F "image=@testdata/images/ct_brain.png" `
  -F 'metadata={"modality":"CT","body_part":"brain","clinical_context":"transient visual field loss, rule out structural lesion"}'
```

Or use the helper script from the repo root:

```powershell
.\scripts\test_report.ps1 -Image testdata/images/mri_lumbar_spine.jpg -Modality MRI -BodyPart "lumbar spine"
```

**Note:** Live LLM calls require `OPENAI_API_KEY` in `.env`.
