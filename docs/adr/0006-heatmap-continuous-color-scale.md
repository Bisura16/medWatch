# ADR-0006: Heatmap memakai skala warna kontinu d3 dengan risk matrix 5 stop

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Halaman `/heatmap` di frontend menampilkan matriks obat x efek samping.
Versi awal hanya memakai tiga kategori warna diskrit (ringan / sedang
/ serius) sehingga gradasi nilai dalam satu bucket hilang dan sel
dengan nilai nol tampak kosong. Bug B11 ("heatmap not a real heatmap")
membutuhkan setiap sel terwarnai dengan skala kontinu dan legend yang
informatif.

## Decision Drivers

- Setiap sel harus berwarna agar pola visual matriks terbaca walaupun
  beberapa nilai bernilai nol.
- Legend harus menjelaskan encoding warna ke nilai numerik secara
  visual, bukan hanya teks.
- Kontras teks angka pada sel harus mengikuti latar agar tetap terbaca
  (luminance-aware).
- Tooling sudah tersedia di `package.json` (`d3-scale`,
  `d3-interpolate`); tidak menambah dependency baru.

## Considered Options

- Tetap tiga bucket diskrit (ringan / sedang / serius).
- Skala dua warna interpolated linear (green -> red).
- Skala lima stop risk matrix (green -> light green -> pale yellow
  -> orange -> red) menggunakan `piecewise(interpolateRgb, ...)` dari
  d3.
- Skema viridis / inferno dari d3-scale-chromatic.

## Decision Outcome

Chosen option: "Skala 5 stop risk matrix dengan d3 piecewise
interpolation", karena memetakan langsung ke semantik klinis risk
matrix (semakin merah semakin berbahaya), tetap menjaga setiap sel
terwarnai, dan dapat digunakan kembali untuk gradient swatch legend di
luar grid.

### Consequences

- Good: Setiap sel terwarnai, termasuk sel nilai nol yang jatuh di
  ujung hijau ramp.
- Good: Legend gradient di-build dari konstanta yang sama (`RISK_RAMP`)
  sehingga swatch dan sel selalu match.
- Good: Kontras teks dihitung dari WCAG relative luminance, bukan
  threshold buta; angka tetap terbaca di hijau, kuning pucat, dan
  merah pekat.
- Good: Fungsi `buildColorScale(min, max)` dapat dipakai ulang oleh
  visualisasi lain yang butuh continuous color scale.
- Bad: Lima stop hex di-hardcode di kode; perubahan palet harus melalui
  PR yang menyentuh konstanta ramp.
- Bad: d3 menambah beberapa kilobyte ke bundle frontend, namun tidak
  menjadi keberatan karena library ini sudah dipakai oleh komponen
  lain dan masuk dalam tree-shaking.

### Confirmation

- Ramp 5 stop: `src/lib/heatmap-colors.ts:17-24` mendefinisikan
  `RISK_RAMP = ["#1A9850", "#A6D96A", "#FFFFBF", "#FDAE61", "#D7191C"]`
  dari hijau kuat ke merah kuat.
- Scale function: `src/lib/heatmap-colors.ts:32-40` membangun
  `scaleLinear` dengan domain `[min, max]`, clamp aktif, dan
  interpolator `piecewise(interpolateRgb, RISK_RAMP)`.
- Luminance contrast: `src/lib/heatmap-colors.ts:73-84` menghitung
  relative luminance per kanal sRGB sesuai formula WCAG; threshold
  decision text color di `src/lib/heatmap-colors.ts:92-94`.
- Gradient legend CSS: `src/lib/heatmap-colors.ts:100-105`
  membangun string `linear-gradient(90deg, ...)` dari ramp yang sama.
- Konsumsi di halaman heatmap: `src/app/heatmap/page.tsx:5-9`
  mengimpor `buildColorScale`, `buildGradientCss`, dan
  `getContrastingTextColor` untuk merender sel + legend.
- Konsistensi keparahan severity weights:
  `src/app/heatmap/page.tsx:44-48` mendefinisikan
  `SEVERITY_WEIGHT = { ringan: 1, sedang: 2, serius: 4 }`, sejalan
  dengan bobot di backend (`anggota4/data/effect_database.json`).

## More Information

- B11 bug register entry: see catatan internal proyek (project constitution).
- ADR-0005 menyebutkan modul Alia `viz_heatmap_obat_efek.py` yang
  mengikuti palet keparahan yang sama (ringan `#A6D96A`, sedang
  `#FDAE61`, serius `#D7191C`).
