# MOCK_DATA.md - MedWatch Complete Mock Data

All data in this file must be created as TypeScript files in `src/data/`. Each section below shows the type definitions and the actual data. All data is fictional but realistic.

---

## 1. Drugs Database (`src/data/drugs.ts`)

### Type Definition

```ts
export interface Drug {
  id: string;
  name: string;
  genericName: string;
  category: DrugCategory;
  manufacturer: string;
  description: string;
  dosageForm: string;
  strength: string;
  usage: string;
  sideEffects: SideEffect[];
  recallStatus: "none" | "watch" | "recalled";
  recallNote?: string;
}

export type DrugCategory =
  | "Analgesic"
  | "Antibiotic"
  | "Antihypertensive"
  | "Antihistamine"
  | "NSAID"
  | "Gastrointestinal"
  | "Antidiabetic"
  | "Antidepressant"
  | "Bronchodilator"
  | "Corticosteroid";

export interface SideEffect {
  name: string;
  frequency: "Very Common" | "Common" | "Uncommon" | "Rare" | "Very Rare";
  frequencyPercent: number;
  severity: "Mild" | "Moderate" | "Severe";
}
```

### Data (25 drugs)

```ts
export const drugs: Drug[] = [
  {
    id: "drug-001",
    name: "Paracetamol",
    genericName: "Acetaminophen",
    category: "Analgesic",
    manufacturer: "PT Kimia Farma",
    description: "Analgesik dan antipiretik untuk nyeri ringan-sedang dan demam",
    dosageForm: "Tablet",
    strength: "500mg",
    usage: "Dewasa: 500-1000mg setiap 4-6 jam, maksimal 4g/hari",
    sideEffects: [
      { name: "Mual", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Ruam Kulit", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Gangguan Hati", frequency: "Rare", frequencyPercent: 0.5, severity: "Severe" },
      { name: "Trombositopenia", frequency: "Very Rare", frequencyPercent: 0.1, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-002",
    name: "Ibuprofen",
    genericName: "Ibuprofen",
    category: "NSAID",
    manufacturer: "PT Dexa Medica",
    description: "Anti-inflamasi non-steroid untuk nyeri, demam, dan peradangan",
    dosageForm: "Tablet",
    strength: "400mg",
    usage: "Dewasa: 200-400mg setiap 4-6 jam, maksimal 1.2g/hari",
    sideEffects: [
      { name: "Mual", frequency: "Very Common", frequencyPercent: 15, severity: "Mild" },
      { name: "Pusing", frequency: "Common", frequencyPercent: 7, severity: "Mild" },
      { name: "Nyeri Lambung", frequency: "Common", frequencyPercent: 10, severity: "Moderate" },
      { name: "Perdarahan GI", frequency: "Uncommon", frequencyPercent: 2, severity: "Severe" },
      { name: "Reaksi Alergi", frequency: "Rare", frequencyPercent: 0.8, severity: "Severe" },
      { name: "Gangguan Ginjal", frequency: "Rare", frequencyPercent: 0.3, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-003",
    name: "Amoxicillin",
    genericName: "Amoxicillin Trihydrate",
    category: "Antibiotic",
    manufacturer: "PT Sanbe Farma",
    description: "Antibiotik penisilin spektrum luas untuk infeksi bakteri",
    dosageForm: "Kapsul",
    strength: "500mg",
    usage: "Dewasa: 250-500mg setiap 8 jam selama 7-14 hari",
    sideEffects: [
      { name: "Diare", frequency: "Very Common", frequencyPercent: 12, severity: "Mild" },
      { name: "Mual", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Ruam Kulit", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Kandidiasis", frequency: "Uncommon", frequencyPercent: 3, severity: "Moderate" },
      { name: "Anafilaksis", frequency: "Very Rare", frequencyPercent: 0.05, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-004",
    name: "Amlodipine",
    genericName: "Amlodipine Besylate",
    category: "Antihypertensive",
    manufacturer: "PT Kalbe Farma",
    description: "Calcium channel blocker untuk hipertensi dan angina",
    dosageForm: "Tablet",
    strength: "5mg",
    usage: "Dewasa: 5-10mg sekali sehari",
    sideEffects: [
      { name: "Edema Perifer", frequency: "Very Common", frequencyPercent: 18, severity: "Mild" },
      { name: "Pusing", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Flushing", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Palpitasi", frequency: "Uncommon", frequencyPercent: 2, severity: "Moderate" },
      { name: "Hipotensi", frequency: "Rare", frequencyPercent: 0.5, severity: "Severe" },
    ],
    recallStatus: "watch",
    recallNote: "Batch tertentu sedang dalam investigasi BPOM terkait impuritas",
  },
  {
    id: "drug-005",
    name: "Cetirizine",
    genericName: "Cetirizine HCl",
    category: "Antihistamine",
    manufacturer: "PT Tempo Scan Pacific",
    description: "Antihistamin generasi kedua untuk alergi dan urtikaria",
    dosageForm: "Tablet",
    strength: "10mg",
    usage: "Dewasa: 10mg sekali sehari",
    sideEffects: [
      { name: "Kantuk", frequency: "Common", frequencyPercent: 9, severity: "Mild" },
      { name: "Mulut Kering", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Gangguan GI", frequency: "Uncommon", frequencyPercent: 2, severity: "Mild" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-006",
    name: "Omeprazole",
    genericName: "Omeprazole",
    category: "Gastrointestinal",
    manufacturer: "PT Ferron Par Pharmaceuticals",
    description: "Proton pump inhibitor untuk GERD, tukak lambung, dan dispepsia",
    dosageForm: "Kapsul",
    strength: "20mg",
    usage: "Dewasa: 20-40mg sekali sehari sebelum makan",
    sideEffects: [
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 7, severity: "Mild" },
      { name: "Diare", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Mual", frequency: "Common", frequencyPercent: 4, severity: "Mild" },
      { name: "Nyeri Perut", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Defisiensi B12", frequency: "Rare", frequencyPercent: 0.8, severity: "Moderate" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-007",
    name: "Metformin",
    genericName: "Metformin HCl",
    category: "Antidiabetic",
    manufacturer: "PT Dexa Medica",
    description: "Antidiabetik oral lini pertama untuk diabetes mellitus tipe 2",
    dosageForm: "Tablet",
    strength: "500mg",
    usage: "Dewasa: 500mg 2-3x sehari bersama makan",
    sideEffects: [
      { name: "Mual", frequency: "Very Common", frequencyPercent: 20, severity: "Mild" },
      { name: "Diare", frequency: "Very Common", frequencyPercent: 18, severity: "Mild" },
      { name: "Nyeri Perut", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Gangguan Rasa", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Asidosis Laktat", frequency: "Very Rare", frequencyPercent: 0.03, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-008",
    name: "Captopril",
    genericName: "Captopril",
    category: "Antihypertensive",
    manufacturer: "PT Kimia Farma",
    description: "ACE inhibitor untuk hipertensi dan gagal jantung",
    dosageForm: "Tablet",
    strength: "25mg",
    usage: "Dewasa: 12.5-50mg 2-3x sehari",
    sideEffects: [
      { name: "Batuk Kering", frequency: "Very Common", frequencyPercent: 15, severity: "Mild" },
      { name: "Pusing", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Gangguan Rasa", frequency: "Common", frequencyPercent: 4, severity: "Mild" },
      { name: "Hiperkalemia", frequency: "Uncommon", frequencyPercent: 2, severity: "Moderate" },
      { name: "Angioedema", frequency: "Very Rare", frequencyPercent: 0.1, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-009",
    name: "Dexamethasone",
    genericName: "Dexamethasone",
    category: "Corticosteroid",
    manufacturer: "PT Novell Pharmaceutical",
    description: "Kortikosteroid untuk inflamasi berat, alergi, dan kondisi autoimun",
    dosageForm: "Tablet",
    strength: "0.5mg",
    usage: "Dewasa: 0.5-9mg/hari tergantung kondisi",
    sideEffects: [
      { name: "Peningkatan Nafsu Makan", frequency: "Very Common", frequencyPercent: 22, severity: "Mild" },
      { name: "Insomnia", frequency: "Common", frequencyPercent: 10, severity: "Mild" },
      { name: "Perubahan Mood", frequency: "Common", frequencyPercent: 8, severity: "Moderate" },
      { name: "Hiperglikemia", frequency: "Common", frequencyPercent: 7, severity: "Moderate" },
      { name: "Osteoporosis", frequency: "Uncommon", frequencyPercent: 3, severity: "Severe" },
      { name: "Supresi Adrenal", frequency: "Uncommon", frequencyPercent: 2, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-010",
    name: "Salbutamol",
    genericName: "Salbutamol Sulfate",
    category: "Bronchodilator",
    manufacturer: "PT Combiphar",
    description: "Bronkodilator short-acting untuk asma dan bronkospasme",
    dosageForm: "Inhaler",
    strength: "100mcg/puff",
    usage: "Dewasa: 1-2 puff saat dibutuhkan, maksimal 8 puff/hari",
    sideEffects: [
      { name: "Tremor", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Palpitasi", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Hipokalemia", frequency: "Uncommon", frequencyPercent: 2, severity: "Moderate" },
      { name: "Aritmia", frequency: "Rare", frequencyPercent: 0.5, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-011",
    name: "Ciprofloxacin",
    genericName: "Ciprofloxacin HCl",
    category: "Antibiotic",
    manufacturer: "PT Kalbe Farma",
    description: "Antibiotik fluorokuinolon untuk infeksi bakteri gram-negatif",
    dosageForm: "Tablet",
    strength: "500mg",
    usage: "Dewasa: 250-750mg setiap 12 jam selama 7-14 hari",
    sideEffects: [
      { name: "Mual", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Diare", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Tendinitis", frequency: "Uncommon", frequencyPercent: 1.5, severity: "Severe" },
      { name: "Neuropati Perifer", frequency: "Rare", frequencyPercent: 0.3, severity: "Severe" },
    ],
    recallStatus: "recalled",
    recallNote: "Batch CBX-2026-04 ditarik karena kontaminasi partikel asing",
  },
  {
    id: "drug-012",
    name: "Ranitidine",
    genericName: "Ranitidine HCl",
    category: "Gastrointestinal",
    manufacturer: "PT Sanbe Farma",
    description: "H2 receptor antagonist untuk tukak lambung dan GERD",
    dosageForm: "Tablet",
    strength: "150mg",
    usage: "Dewasa: 150mg 2x sehari atau 300mg sebelum tidur",
    sideEffects: [
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Pusing", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Konstipasi", frequency: "Uncommon", frequencyPercent: 2, severity: "Mild" },
      { name: "Hepatitis", frequency: "Very Rare", frequencyPercent: 0.05, severity: "Severe" },
    ],
    recallStatus: "recalled",
    recallNote: "Ditarik global karena kandungan NDMA (nitrosamine) melebihi batas aman",
  },
  {
    id: "drug-013",
    name: "Losartan",
    genericName: "Losartan Potassium",
    category: "Antihypertensive",
    manufacturer: "PT Ferron Par Pharmaceuticals",
    description: "Angiotensin II receptor blocker untuk hipertensi",
    dosageForm: "Tablet",
    strength: "50mg",
    usage: "Dewasa: 50-100mg sekali sehari",
    sideEffects: [
      { name: "Pusing", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Hiperkalemia", frequency: "Uncommon", frequencyPercent: 3, severity: "Moderate" },
      { name: "Kelelahan", frequency: "Common", frequencyPercent: 4, severity: "Mild" },
      { name: "Angioedema", frequency: "Very Rare", frequencyPercent: 0.1, severity: "Severe" },
    ],
    recallStatus: "watch",
    recallNote: "Beberapa batch dalam pengawasan BPOM terkait impuritas azido",
  },
  {
    id: "drug-014",
    name: "Sertraline",
    genericName: "Sertraline HCl",
    category: "Antidepressant",
    manufacturer: "PT Novell Pharmaceutical",
    description: "SSRI untuk depresi, gangguan kecemasan, dan OCD",
    dosageForm: "Tablet",
    strength: "50mg",
    usage: "Dewasa: 50-200mg sekali sehari",
    sideEffects: [
      { name: "Mual", frequency: "Very Common", frequencyPercent: 18, severity: "Mild" },
      { name: "Insomnia", frequency: "Common", frequencyPercent: 10, severity: "Mild" },
      { name: "Diare", frequency: "Common", frequencyPercent: 9, severity: "Mild" },
      { name: "Pusing", frequency: "Common", frequencyPercent: 7, severity: "Mild" },
      { name: "Disfungsi Seksual", frequency: "Common", frequencyPercent: 8, severity: "Moderate" },
      { name: "Sindrom Serotonin", frequency: "Very Rare", frequencyPercent: 0.02, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-015",
    name: "Diclofenac",
    genericName: "Diclofenac Sodium",
    category: "NSAID",
    manufacturer: "PT Tempo Scan Pacific",
    description: "NSAID untuk nyeri muskuloskeletal dan inflamasi",
    dosageForm: "Tablet",
    strength: "50mg",
    usage: "Dewasa: 50mg 2-3x sehari",
    sideEffects: [
      { name: "Nyeri Lambung", frequency: "Very Common", frequencyPercent: 14, severity: "Moderate" },
      { name: "Mual", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Edema", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Perdarahan GI", frequency: "Uncommon", frequencyPercent: 1.5, severity: "Severe" },
      { name: "Risiko Kardiovaskular", frequency: "Rare", frequencyPercent: 0.5, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-016",
    name: "Loratadine",
    genericName: "Loratadine",
    category: "Antihistamine",
    manufacturer: "PT Combiphar",
    description: "Antihistamin non-sedatif untuk rhinitis alergi",
    dosageForm: "Tablet",
    strength: "10mg",
    usage: "Dewasa: 10mg sekali sehari",
    sideEffects: [
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Kantuk", frequency: "Uncommon", frequencyPercent: 2, severity: "Mild" },
      { name: "Mulut Kering", frequency: "Uncommon", frequencyPercent: 2, severity: "Mild" },
      { name: "Kelelahan", frequency: "Uncommon", frequencyPercent: 1.5, severity: "Mild" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-017",
    name: "Azithromycin",
    genericName: "Azithromycin Dihydrate",
    category: "Antibiotic",
    manufacturer: "PT Dexa Medica",
    description: "Antibiotik makrolida untuk infeksi saluran napas dan kulit",
    dosageForm: "Tablet",
    strength: "500mg",
    usage: "Dewasa: 500mg hari 1, lalu 250mg hari 2-5",
    sideEffects: [
      { name: "Diare", frequency: "Common", frequencyPercent: 9, severity: "Mild" },
      { name: "Mual", frequency: "Common", frequencyPercent: 7, severity: "Mild" },
      { name: "Nyeri Perut", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Gangguan Pendengaran", frequency: "Rare", frequencyPercent: 0.3, severity: "Moderate" },
      { name: "Aritmia (QT prolongation)", frequency: "Very Rare", frequencyPercent: 0.05, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-018",
    name: "Simvastatin",
    genericName: "Simvastatin",
    category: "Antihypertensive",
    manufacturer: "PT Kalbe Farma",
    description: "Statin untuk menurunkan kolesterol dan risiko kardiovaskular",
    dosageForm: "Tablet",
    strength: "20mg",
    usage: "Dewasa: 10-40mg sekali sehari malam hari",
    sideEffects: [
      { name: "Nyeri Otot", frequency: "Common", frequencyPercent: 8, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Common", frequencyPercent: 5, severity: "Mild" },
      { name: "Gangguan GI", frequency: "Common", frequencyPercent: 4, severity: "Mild" },
      { name: "Peningkatan Enzim Hati", frequency: "Uncommon", frequencyPercent: 2, severity: "Moderate" },
      { name: "Rhabdomyolysis", frequency: "Very Rare", frequencyPercent: 0.01, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-019",
    name: "Prednisone",
    genericName: "Prednisone",
    category: "Corticosteroid",
    manufacturer: "PT Sanbe Farma",
    description: "Kortikosteroid untuk inflamasi, alergi berat, dan autoimun",
    dosageForm: "Tablet",
    strength: "5mg",
    usage: "Dewasa: 5-60mg/hari tergantung kondisi, tapering dose",
    sideEffects: [
      { name: "Peningkatan Nafsu Makan", frequency: "Very Common", frequencyPercent: 25, severity: "Mild" },
      { name: "Insomnia", frequency: "Very Common", frequencyPercent: 15, severity: "Mild" },
      { name: "Perubahan Mood", frequency: "Common", frequencyPercent: 10, severity: "Moderate" },
      { name: "Hiperglikemia", frequency: "Common", frequencyPercent: 8, severity: "Moderate" },
      { name: "Osteoporosis", frequency: "Uncommon", frequencyPercent: 4, severity: "Severe" },
    ],
    recallStatus: "none",
  },
  {
    id: "drug-020",
    name: "Domperidone",
    genericName: "Domperidone",
    category: "Gastrointestinal",
    manufacturer: "PT Ferron Par Pharmaceuticals",
    description: "Antiemetik dan prokinetik untuk mual, muntah, dan dispepsia",
    dosageForm: "Tablet",
    strength: "10mg",
    usage: "Dewasa: 10mg 3x sehari sebelum makan",
    sideEffects: [
      { name: "Mulut Kering", frequency: "Common", frequencyPercent: 6, severity: "Mild" },
      { name: "Sakit Kepala", frequency: "Uncommon", frequencyPercent: 3, severity: "Mild" },
      { name: "Gangguan GI", frequency: "Uncommon", frequencyPercent: 2, severity: "Mild" },
      { name: "Aritmia (QT prolongation)", frequency: "Rare", frequencyPercent: 0.5, severity: "Severe" },
    ],
    recallStatus: "watch",
    recallNote: "EMA membatasi penggunaan karena risiko kardiovaskular, BPOM monitoring",
  },
];
```

---

## 2. Patients Database (`src/data/patients.ts`)

### Type Definition

```ts
export interface Patient {
  id: string;
  name: string;
  nik: string;
  age: number;
  gender: "Laki-laki" | "Perempuan";
  phone: string;
  address: string;
  province: string;
  registeredDate: string;
  lastVisit: string;
  status: "Aktif" | "Tidak Aktif";
  complaint: string;
  assignedDrugs: string[];
}
```

### Data (generate 50 patients)

the developer should generate 50 patients with:
- Indonesian names (mix of Javanese, Sundanese, Batak, Minang, etc.)
- NIK format: 16 digits (e.g., "3204150601980001")
- Ages: range 18-75
- Provinces distributed across Indonesia (weight toward Java)
- Registered dates: between Jan 2025 - Mar 2026
- Last visit: within 6 months of current date
- Complaints: realistic clinical complaints in Indonesian
  - "Hipertensi", "Demam", "Infeksi Saluran Napas", "Nyeri Sendi",
    "Diabetes Mellitus", "GERD", "Alergi", "Asma", "Migrain",
    "Infeksi Saluran Kemih", "Dermatitis", "Dispepsia",
    "Bronkitis", "Anemia", "Gangguan Kecemasan"
- assignedDrugs: 1-3 drug IDs from the drugs list

Here are 10 sample entries to show the pattern (the developer generates the remaining 40):

```ts
export const patients: Patient[] = [
  {
    id: "patient-001",
    name: "Siti Aminah Putri",
    nik: "3204156507850001",
    age: 41,
    gender: "Perempuan",
    phone: "081234567890",
    address: "Jl. Merdeka No. 45, Bandung",
    province: "Jawa Barat",
    registeredDate: "2025-03-15",
    lastVisit: "2026-03-10",
    status: "Aktif",
    complaint: "Hipertensi",
    assignedDrugs: ["drug-004", "drug-008"],
  },
  {
    id: "patient-002",
    name: "Budi Santoso",
    nik: "3374011203780005",
    age: 48,
    gender: "Laki-laki",
    phone: "085678901234",
    address: "Jl. Diponegoro No. 12, Semarang",
    province: "Jawa Tengah",
    registeredDate: "2025-05-20",
    lastVisit: "2026-02-28",
    status: "Aktif",
    complaint: "Diabetes Mellitus",
    assignedDrugs: ["drug-007"],
  },
  {
    id: "patient-003",
    name: "Dewi Lestari",
    nik: "3175024408900003",
    age: 36,
    gender: "Perempuan",
    phone: "087812345678",
    address: "Jl. Sudirman Kav. 52, Jakarta Selatan",
    province: "DKI Jakarta",
    registeredDate: "2025-01-10",
    lastVisit: "2026-03-20",
    status: "Aktif",
    complaint: "GERD",
    assignedDrugs: ["drug-006"],
  },
  {
    id: "patient-004",
    name: "Muhammad Rizki Pratama",
    nik: "3578010205950002",
    age: 31,
    gender: "Laki-laki",
    phone: "081345678901",
    address: "Jl. Raya Darmo No. 88, Surabaya",
    province: "Jawa Timur",
    registeredDate: "2025-07-08",
    lastVisit: "2026-01-15",
    status: "Aktif",
    complaint: "Asma",
    assignedDrugs: ["drug-010", "drug-009"],
  },
  {
    id: "patient-005",
    name: "Ni Made Ayu Kusuma",
    nik: "5171034509880004",
    age: 38,
    gender: "Perempuan",
    phone: "089923456789",
    address: "Jl. Sunset Road No. 7, Denpasar",
    province: "Bali",
    registeredDate: "2025-09-12",
    lastVisit: "2026-03-05",
    status: "Aktif",
    complaint: "Migrain",
    assignedDrugs: ["drug-001"],
  },
  {
    id: "patient-006",
    name: "Arief Rahman Hakim",
    nik: "1271050302870006",
    age: 39,
    gender: "Laki-laki",
    phone: "082156789012",
    address: "Jl. Gatot Subroto No. 25, Medan",
    province: "Sumatera Utara",
    registeredDate: "2025-04-22",
    lastVisit: "2026-02-10",
    status: "Aktif",
    complaint: "Infeksi Saluran Napas",
    assignedDrugs: ["drug-003", "drug-001"],
  },
  {
    id: "patient-007",
    name: "Rina Wulandari",
    nik: "3273015606920007",
    age: 34,
    gender: "Perempuan",
    phone: "085567890123",
    address: "Jl. Asia Afrika No. 100, Bandung",
    province: "Jawa Barat",
    registeredDate: "2025-06-18",
    lastVisit: "2025-12-20",
    status: "Tidak Aktif",
    complaint: "Alergi",
    assignedDrugs: ["drug-005", "drug-009"],
  },
  {
    id: "patient-008",
    name: "I Wayan Dharma Putra",
    nik: "5103011508750008",
    age: 51,
    gender: "Laki-laki",
    phone: "087845678901",
    address: "Jl. Imam Bonjol No. 33, Tabanan",
    province: "Bali",
    registeredDate: "2025-02-05",
    lastVisit: "2026-03-18",
    status: "Aktif",
    complaint: "Nyeri Sendi",
    assignedDrugs: ["drug-002", "drug-015"],
  },
  {
    id: "patient-009",
    name: "Putri Handayani",
    nik: "3471025003830009",
    age: 43,
    gender: "Perempuan",
    phone: "081267890123",
    address: "Jl. Malioboro No. 56, Yogyakarta",
    province: "DI Yogyakarta",
    registeredDate: "2025-08-30",
    lastVisit: "2026-02-22",
    status: "Aktif",
    complaint: "Dermatitis",
    assignedDrugs: ["drug-009", "drug-016"],
  },
  {
    id: "patient-010",
    name: "Hasan Basri",
    nik: "7371011204680010",
    age: 58,
    gender: "Laki-laki",
    phone: "085378901234",
    address: "Jl. Pettarani No. 18, Makassar",
    province: "Sulawesi Selatan",
    registeredDate: "2025-11-14",
    lastVisit: "2026-03-01",
    status: "Aktif",
    complaint: "Hipertensi",
    assignedDrugs: ["drug-013", "drug-018"],
  },
  // ... the developer generates patient-011 through patient-050
  // following same patterns, diverse provinces, diverse complaints
];
```

---

## 3. Drug Interactions Network (`src/data/interactions.ts`)

### Type Definition

```ts
export interface DrugNode {
  id: string;
  name: string;
  category: DrugCategory;
  connections: number;
}

export interface DrugEdge {
  source: string;
  target: string;
  severity: "Minor" | "Moderate" | "Major";
  description: string;
}

export interface InteractionNetwork {
  nodes: DrugNode[];
  edges: DrugEdge[];
}
```

### Data

```ts
export const interactionNetwork: InteractionNetwork = {
  nodes: [
    { id: "drug-001", name: "Paracetamol", category: "Analgesic", connections: 3 },
    { id: "drug-002", name: "Ibuprofen", category: "NSAID", connections: 6 },
    { id: "drug-003", name: "Amoxicillin", category: "Antibiotic", connections: 3 },
    { id: "drug-004", name: "Amlodipine", category: "Antihypertensive", connections: 4 },
    { id: "drug-005", name: "Cetirizine", category: "Antihistamine", connections: 2 },
    { id: "drug-006", name: "Omeprazole", category: "Gastrointestinal", connections: 5 },
    { id: "drug-007", name: "Metformin", category: "Antidiabetic", connections: 4 },
    { id: "drug-008", name: "Captopril", category: "Antihypertensive", connections: 5 },
    { id: "drug-009", name: "Dexamethasone", category: "Corticosteroid", connections: 7 },
    { id: "drug-010", name: "Salbutamol", category: "Bronchodilator", connections: 2 },
    { id: "drug-011", name: "Ciprofloxacin", category: "Antibiotic", connections: 5 },
    { id: "drug-013", name: "Losartan", category: "Antihypertensive", connections: 3 },
    { id: "drug-014", name: "Sertraline", category: "Antidepressant", connections: 5 },
    { id: "drug-015", name: "Diclofenac", category: "NSAID", connections: 6 },
    { id: "drug-018", name: "Simvastatin", category: "Antihypertensive", connections: 4 },
  ],
  edges: [
    { source: "drug-002", target: "drug-008", severity: "Major", description: "NSAID mengurangi efek antihipertensi ACE inhibitor" },
    { source: "drug-002", target: "drug-015", severity: "Major", description: "Kombinasi NSAID meningkatkan risiko perdarahan GI" },
    { source: "drug-002", target: "drug-007", severity: "Moderate", description: "Ibuprofen dapat mengurangi efek hipoglikemik metformin" },
    { source: "drug-002", target: "drug-009", severity: "Major", description: "Kombinasi NSAID + kortikosteroid: risiko ulkus GI tinggi" },
    { source: "drug-002", target: "drug-013", severity: "Moderate", description: "NSAID mengurangi efek antihipertensi ARB" },
    { source: "drug-009", target: "drug-007", severity: "Moderate", description: "Kortikosteroid meningkatkan glukosa darah, melawan metformin" },
    { source: "drug-009", target: "drug-008", severity: "Minor", description: "Kortikosteroid dapat mengurangi efek ACE inhibitor" },
    { source: "drug-009", target: "drug-015", severity: "Major", description: "Kombinasi kortikosteroid + NSAID: risiko ulkus GI sangat tinggi" },
    { source: "drug-009", target: "drug-014", severity: "Moderate", description: "Dexamethasone dapat menurunkan kadar sertraline dalam darah" },
    { source: "drug-009", target: "drug-004", severity: "Minor", description: "Dexamethasone dapat mengurangi efek amlodipine" },
    { source: "drug-006", target: "drug-011", severity: "Moderate", description: "Omeprazole mengurangi absorpsi ciprofloxacin" },
    { source: "drug-006", target: "drug-007", severity: "Minor", description: "Omeprazole dapat sedikit meningkatkan absorpsi metformin" },
    { source: "drug-006", target: "drug-018", severity: "Moderate", description: "Omeprazole meningkatkan kadar simvastatin dalam darah" },
    { source: "drug-011", target: "drug-014", severity: "Major", description: "Ciprofloxacin + Sertraline: risiko perpanjangan interval QT" },
    { source: "drug-011", target: "drug-001", severity: "Minor", description: "Ciprofloxacin dapat meningkatkan kadar paracetamol" },
    { source: "drug-011", target: "drug-009", severity: "Moderate", description: "Risiko tendinopati meningkat dengan kombinasi fluorokuinolon + kortikosteroid" },
    { source: "drug-014", target: "drug-002", severity: "Major", description: "SSRI + NSAID: risiko perdarahan meningkat signifikan" },
    { source: "drug-014", target: "drug-015", severity: "Major", description: "SSRI + NSAID: risiko perdarahan GI meningkat" },
    { source: "drug-008", target: "drug-013", severity: "Major", description: "Kombinasi ACE inhibitor + ARB: risiko hiperkalemia dan gagal ginjal" },
    { source: "drug-008", target: "drug-004", severity: "Minor", description: "Efek aditif antihipertensi, monitor tekanan darah" },
    { source: "drug-004", target: "drug-018", severity: "Moderate", description: "Amlodipine meningkatkan kadar simvastatin, risiko miopati" },
    { source: "drug-001", target: "drug-014", severity: "Minor", description: "Paracetamol aman dikombinasi, interaksi minimal" },
    { source: "drug-015", target: "drug-008", severity: "Major", description: "Diclofenac mengurangi efek antihipertensi dan merusak fungsi ginjal" },
    { source: "drug-015", target: "drug-013", severity: "Moderate", description: "NSAID mengurangi efek antihipertensi ARB" },
    { source: "drug-005", target: "drug-014", severity: "Minor", description: "Cetirizine + Sertraline: sedikit peningkatan efek sedasi" },
  ],
};
```

---

## 4. Indonesia Province Data (`src/data/indonesia-map.ts`)

### Type Definition

```ts
export interface ProvinceData {
  id: string;
  name: string;
  clinicCount: number;
  patientCount: number;
  density: "Very Low" | "Low" | "Medium" | "High" | "Very High";
}
```

### Data (34 provinces)

```ts
export const provinceData: ProvinceData[] = [
  { id: "ID-AC", name: "Aceh", clinicCount: 12, patientCount: 89, density: "Low" },
  { id: "ID-SU", name: "Sumatera Utara", clinicCount: 28, patientCount: 215, density: "Medium" },
  { id: "ID-SB", name: "Sumatera Barat", clinicCount: 15, patientCount: 112, density: "Low" },
  { id: "ID-RI", name: "Riau", clinicCount: 14, patientCount: 98, density: "Low" },
  { id: "ID-JA", name: "Jambi", clinicCount: 8, patientCount: 56, density: "Very Low" },
  { id: "ID-SS", name: "Sumatera Selatan", clinicCount: 18, patientCount: 134, density: "Medium" },
  { id: "ID-BE", name: "Bengkulu", clinicCount: 5, patientCount: 32, density: "Very Low" },
  { id: "ID-LA", name: "Lampung", clinicCount: 16, patientCount: 120, density: "Medium" },
  { id: "ID-BB", name: "Kep. Bangka Belitung", clinicCount: 4, patientCount: 24, density: "Very Low" },
  { id: "ID-KR", name: "Kep. Riau", clinicCount: 6, patientCount: 42, density: "Very Low" },
  { id: "ID-JK", name: "DKI Jakarta", clinicCount: 65, patientCount: 520, density: "Very High" },
  { id: "ID-JB", name: "Jawa Barat", clinicCount: 78, patientCount: 680, density: "Very High" },
  { id: "ID-JT", name: "Jawa Tengah", clinicCount: 55, patientCount: 445, density: "Very High" },
  { id: "ID-YO", name: "DI Yogyakarta", clinicCount: 22, patientCount: 178, density: "High" },
  { id: "ID-JI", name: "Jawa Timur", clinicCount: 62, patientCount: 510, density: "Very High" },
  { id: "ID-BT", name: "Banten", clinicCount: 30, patientCount: 240, density: "High" },
  { id: "ID-BA", name: "Bali", clinicCount: 18, patientCount: 145, density: "Medium" },
  { id: "ID-NB", name: "Nusa Tenggara Barat", clinicCount: 10, patientCount: 72, density: "Low" },
  { id: "ID-NT", name: "Nusa Tenggara Timur", clinicCount: 8, patientCount: 48, density: "Very Low" },
  { id: "ID-KB", name: "Kalimantan Barat", clinicCount: 9, patientCount: 64, density: "Low" },
  { id: "ID-KT", name: "Kalimantan Tengah", clinicCount: 6, patientCount: 38, density: "Very Low" },
  { id: "ID-KS", name: "Kalimantan Selatan", clinicCount: 11, patientCount: 82, density: "Low" },
  { id: "ID-KI", name: "Kalimantan Timur", clinicCount: 13, patientCount: 95, density: "Low" },
  { id: "ID-KU", name: "Kalimantan Utara", clinicCount: 3, patientCount: 18, density: "Very Low" },
  { id: "ID-SA", name: "Sulawesi Utara", clinicCount: 10, patientCount: 75, density: "Low" },
  { id: "ID-ST", name: "Sulawesi Tengah", clinicCount: 7, patientCount: 45, density: "Very Low" },
  { id: "ID-SN", name: "Sulawesi Selatan", clinicCount: 25, patientCount: 198, density: "Medium" },
  { id: "ID-SG", name: "Sulawesi Tenggara", clinicCount: 6, patientCount: 35, density: "Very Low" },
  { id: "ID-GO", name: "Gorontalo", clinicCount: 4, patientCount: 22, density: "Very Low" },
  { id: "ID-SR", name: "Sulawesi Barat", clinicCount: 3, patientCount: 15, density: "Very Low" },
  { id: "ID-MA", name: "Maluku", clinicCount: 5, patientCount: 28, density: "Very Low" },
  { id: "ID-MU", name: "Maluku Utara", clinicCount: 3, patientCount: 16, density: "Very Low" },
  { id: "ID-PA", name: "Papua", clinicCount: 7, patientCount: 38, density: "Very Low" },
  { id: "ID-PB", name: "Papua Barat", clinicCount: 4, patientCount: 20, density: "Very Low" },
];
```

Note: For the TopoJSON file, the developer should fetch Indonesia province boundaries from:
`https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-provinces.geojson`
or generate/find a suitable TopoJSON. The province IDs in the data above use ISO 3166-2:ID codes.

---

## 5. Molecule Data (`src/data/molecules.ts`)

### Type Definition

```ts
export interface Atom {
  id: number;
  element: "C" | "H" | "O" | "N" | "S" | "Cl";
  label: string;
  position: [number, number, number];
}

export interface Bond {
  atom1: number;
  atom2: number;
  order: 1 | 2 | 3;
}

export interface Molecule {
  id: string;
  name: string;
  formula: string;
  atoms: Atom[];
  bonds: Bond[];
}
```

### Data (5 molecules)

the developer should generate realistic 3D coordinates for these molecules. Approximate coordinates are fine since this is visual-only. Here are the molecules to model:

```ts
export const molecules: Molecule[] = [
  {
    id: "mol-aspirin",
    name: "Aspirin (Asam Asetilsalisilat)",
    formula: "C9H8O4",
    atoms: [
      // 9 Carbon, 8 Hydrogen, 4 Oxygen atoms
      // the developer generates positions based on aspirin molecular geometry
      // Benzene ring flat on XY plane, acetyl group extending from ring
    ],
    bonds: [
      // Benzene ring: alternating single/double C-C bonds
      // C-OH, C=O (carboxyl), O-C=O (ester)
      // C-H bonds on ring
    ],
  },
  {
    id: "mol-paracetamol",
    name: "Paracetamol (Asetaminofen)",
    formula: "C8H9NO2",
    atoms: [/* 8C, 9H, 1N, 2O */],
    bonds: [/* benzene ring + OH + NHCOCH3 */],
  },
  {
    id: "mol-ibuprofen",
    name: "Ibuprofen",
    formula: "C13H18O2",
    atoms: [/* 13C, 18H, 2O */],
    bonds: [/* benzene ring + isobutyl + propionic acid */],
  },
  {
    id: "mol-caffeine",
    name: "Caffeine (Kafein)",
    formula: "C8H10N4O2",
    atoms: [/* 8C, 10H, 4N, 2O */],
    bonds: [/* purine ring system + methyl groups */],
  },
  {
    id: "mol-amoxicillin",
    name: "Amoxicillin",
    formula: "C16H19N3O5S",
    atoms: [/* 16C, 19H, 3N, 5O, 1S */],
    bonds: [/* beta-lactam ring + thiazolidine + phenol */],
  },
];

// NOTE: the developer should generate actual [x, y, z] coordinates.
// Use approximate molecular geometry. Scale: 1 unit = 1 Angstrom.
// Center each molecule at origin [0, 0, 0].
```

---

## 6. Side Effect Heatmap Data (`src/data/heatmap.ts`)

### Type Definition

```ts
export interface HeatmapCell {
  drugId: string;
  drugName: string;
  sideEffect: string;
  frequency: number;     // 0-100 percentage
  severity: "Low" | "Medium" | "High";
}

export interface HeatmapData {
  drugs: string[];        // row labels
  sideEffects: string[];  // column labels
  cells: HeatmapCell[];
}
```

### Data

```ts
export const heatmapData: HeatmapData = {
  drugs: [
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Amlodipine", "Cetirizine",
    "Omeprazole", "Metformin", "Captopril", "Dexamethasone", "Ciprofloxacin",
    "Sertraline", "Diclofenac",
  ],
  sideEffects: [
    "Mual", "Pusing", "Sakit Kepala", "Diare", "Kantuk",
    "Nyeri Lambung", "Ruam Kulit", "Edema", "Insomnia", "Batuk Kering",
    "Tremor", "Mulut Kering",
  ],
  cells: [
    // the developer generates the full matrix (12 drugs x 12 side effects = 144 cells)
    // Use the frequency data from the drugs database above
    // If a drug doesn't have a specific side effect, frequency = 0
    // Example entries:
    { drugId: "drug-001", drugName: "Paracetamol", sideEffect: "Mual", frequency: 8, severity: "Low" },
    { drugId: "drug-001", drugName: "Paracetamol", sideEffect: "Ruam Kulit", frequency: 3, severity: "Low" },
    { drugId: "drug-002", drugName: "Ibuprofen", sideEffect: "Mual", frequency: 15, severity: "Low" },
    { drugId: "drug-002", drugName: "Ibuprofen", sideEffect: "Pusing", frequency: 7, severity: "Low" },
    { drugId: "drug-002", drugName: "Ibuprofen", sideEffect: "Nyeri Lambung", frequency: 10, severity: "Medium" },
    { drugId: "drug-007", drugName: "Metformin", sideEffect: "Mual", frequency: 20, severity: "Low" },
    { drugId: "drug-007", drugName: "Metformin", sideEffect: "Diare", frequency: 18, severity: "Low" },
    { drugId: "drug-009", drugName: "Dexamethasone", sideEffect: "Insomnia", frequency: 10, severity: "Medium" },
    // ... the developer fills in the remaining cells using drug side effect data
  ],
};
```

---

## 7. Activity Feed (`src/data/activity.ts`)

### Type Definition

```ts
export interface Activity {
  id: string;
  type: "patient_added" | "drug_checked" | "warning" | "recall" | "report_generated" | "visit";
  title: string;
  description: string;
  timestamp: string;
  icon: "UserPlus" | "Search" | "AlertTriangle" | "XCircle" | "FileDown" | "Activity";
  severity?: "info" | "warning" | "danger" | "success";
}
```

### Data (20 entries)

```ts
export const activities: Activity[] = [
  {
    id: "act-001",
    type: "patient_added",
    title: "Pasien baru ditambahkan",
    description: "Siti Aminah Putri terdaftar di klinik Bandung",
    timestamp: "2026-03-28T14:30:00",
    icon: "UserPlus",
    severity: "success",
  },
  {
    id: "act-002",
    type: "drug_checked",
    title: "Obat diperiksa",
    description: "Safety check: Amoxicillin untuk pasien Budi Santoso",
    timestamp: "2026-03-28T13:15:00",
    icon: "Search",
    severity: "info",
  },
  {
    id: "act-003",
    type: "warning",
    title: "Peringatan interaksi obat",
    description: "Ibuprofen + Captopril: risiko penurunan efek antihipertensi",
    timestamp: "2026-03-28T11:45:00",
    icon: "AlertTriangle",
    severity: "warning",
  },
  {
    id: "act-004",
    type: "recall",
    title: "Recall obat terdeteksi",
    description: "Ciprofloxacin batch CBX-2026-04 ditarik dari peredaran",
    timestamp: "2026-03-27T16:00:00",
    icon: "XCircle",
    severity: "danger",
  },
  {
    id: "act-005",
    type: "report_generated",
    title: "Laporan digenerate",
    description: "Rekap pasien bulanan Maret 2026 berhasil di-export",
    timestamp: "2026-03-27T10:30:00",
    icon: "FileDown",
    severity: "info",
  },
  {
    id: "act-006",
    type: "visit",
    title: "Kunjungan pasien",
    description: "Dewi Lestari - kontrol GERD, kondisi membaik",
    timestamp: "2026-03-27T09:00:00",
    icon: "Activity",
    severity: "success",
  },
  {
    id: "act-007",
    type: "warning",
    title: "Peringatan efek samping",
    description: "Laporan efek samping baru: Amlodipine - edema perifer pada 3 pasien",
    timestamp: "2026-03-26T15:20:00",
    icon: "AlertTriangle",
    severity: "warning",
  },
  {
    id: "act-008",
    type: "patient_added",
    title: "Pasien baru ditambahkan",
    description: "Arief Rahman Hakim terdaftar di klinik Medan",
    timestamp: "2026-03-26T11:10:00",
    icon: "UserPlus",
    severity: "success",
  },
  {
    id: "act-009",
    type: "drug_checked",
    title: "Perbandingan obat",
    description: "Perbandingan: Ibuprofen vs Paracetamol vs Diclofenac",
    timestamp: "2026-03-26T09:45:00",
    icon: "Search",
    severity: "info",
  },
  {
    id: "act-010",
    type: "recall",
    title: "Update status recall",
    description: "Ranitidine: status recall global masih berlaku, NDMA terdeteksi",
    timestamp: "2026-03-25T14:00:00",
    icon: "XCircle",
    severity: "danger",
  },
  {
    id: "act-011",
    type: "visit",
    title: "Kunjungan pasien",
    description: "Muhammad Rizki Pratama - kontrol asma, spirometri normal",
    timestamp: "2026-03-25T10:30:00",
    icon: "Activity",
    severity: "success",
  },
  {
    id: "act-012",
    type: "warning",
    title: "Peringatan dosis",
    description: "Pasien Hasan Basri: dosis Losartan perlu evaluasi ulang",
    timestamp: "2026-03-24T16:45:00",
    icon: "AlertTriangle",
    severity: "warning",
  },
  {
    id: "act-013",
    type: "report_generated",
    title: "Laporan keamanan obat",
    description: "Profil keamanan Dexamethasone Q1-2026 berhasil di-export",
    timestamp: "2026-03-24T11:20:00",
    icon: "FileDown",
    severity: "info",
  },
  {
    id: "act-014",
    type: "drug_checked",
    title: "Safety check",
    description: "Sertraline diperiksa untuk pasien baru dengan riwayat NSAID",
    timestamp: "2026-03-23T14:00:00",
    icon: "Search",
    severity: "info",
  },
  {
    id: "act-015",
    type: "patient_added",
    title: "Pasien baru ditambahkan",
    description: "Rina Wulandari terdaftar di klinik Bandung",
    timestamp: "2026-03-23T09:30:00",
    icon: "UserPlus",
    severity: "success",
  },
  {
    id: "act-016",
    type: "warning",
    title: "Peringatan interaksi obat",
    description: "Ciprofloxacin + Sertraline: risiko perpanjangan interval QT",
    timestamp: "2026-03-22T15:10:00",
    icon: "AlertTriangle",
    severity: "danger",
  },
  {
    id: "act-017",
    type: "visit",
    title: "Kunjungan pasien",
    description: "Ni Made Ayu Kusuma - follow-up migrain, frekuensi berkurang",
    timestamp: "2026-03-22T10:00:00",
    icon: "Activity",
    severity: "success",
  },
  {
    id: "act-018",
    type: "drug_checked",
    title: "Obat diperiksa",
    description: "Metformin compatibility check untuk pasien diabetes baru",
    timestamp: "2026-03-21T13:40:00",
    icon: "Search",
    severity: "info",
  },
  {
    id: "act-019",
    type: "recall",
    title: "Peringatan batch",
    description: "Domperidone: EMA monitoring aktif, penggunaan dibatasi",
    timestamp: "2026-03-21T09:15:00",
    icon: "XCircle",
    severity: "warning",
  },
  {
    id: "act-020",
    type: "report_generated",
    title: "Laporan kunjungan",
    description: "Rekap kunjungan pasien Februari 2026 berhasil di-export",
    timestamp: "2026-03-20T16:30:00",
    icon: "FileDown",
    severity: "info",
  },
];
```

---

## 8. Dashboard Stats (`src/data/dashboard.ts`)

### Type Definition & Data

```ts
export interface DashboardStat {
  id: string;
  label: string;
  value: number;
  previousValue: number;
  format: "number" | "percent";
  icon: string;
  color: "blue" | "purple" | "teal" | "pink" | "green" | "amber";
}

export interface SparklinePoint {
  date: string;
  value: number;
}

export const dashboardStats: DashboardStat[] = [
  { id: "total-drugs", label: "Total Obat di Database", value: 127, previousValue: 115, format: "number", icon: "Pill", color: "blue" },
  { id: "total-patients", label: "Total Pasien Terdaftar", value: 1243, previousValue: 1180, format: "number", icon: "Users", color: "purple" },
  { id: "active-warnings", label: "Peringatan Aktif", value: 18, previousValue: 22, format: "number", icon: "AlertTriangle", color: "amber" },
  { id: "monthly-visits", label: "Kunjungan Bulan Ini", value: 342, previousValue: 298, format: "number", icon: "Activity", color: "teal" },
  { id: "recall-alerts", label: "Alert Recall Obat", value: 5, previousValue: 3, format: "number", icon: "XCircle", color: "pink" },
  { id: "safety-checks", label: "Safety Check Hari Ini", value: 47, previousValue: 38, format: "number", icon: "ShieldCheck", color: "green" },
];

// Sparkline data for each stat (last 7 days)
export const sparklineData: Record<string, SparklinePoint[]> = {
  "total-drugs": [
    { date: "Mar 24", value: 122 }, { date: "Mar 25", value: 123 },
    { date: "Mar 26", value: 124 }, { date: "Mar 27", value: 125 },
    { date: "Mar 28", value: 126 }, { date: "Mar 29", value: 126 },
    { date: "Mar 30", value: 127 },
  ],
  "total-patients": [
    { date: "Mar 24", value: 1210 }, { date: "Mar 25", value: 1218 },
    { date: "Mar 26", value: 1225 }, { date: "Mar 27", value: 1230 },
    { date: "Mar 28", value: 1235 }, { date: "Mar 29", value: 1240 },
    { date: "Mar 30", value: 1243 },
  ],
  "active-warnings": [
    { date: "Mar 24", value: 20 }, { date: "Mar 25", value: 22 },
    { date: "Mar 26", value: 21 }, { date: "Mar 27", value: 19 },
    { date: "Mar 28", value: 18 }, { date: "Mar 29", value: 18 },
    { date: "Mar 30", value: 18 },
  ],
  "monthly-visits": [
    { date: "Mar 24", value: 280 }, { date: "Mar 25", value: 295 },
    { date: "Mar 26", value: 305 }, { date: "Mar 27", value: 318 },
    { date: "Mar 28", value: 330 }, { date: "Mar 29", value: 335 },
    { date: "Mar 30", value: 342 },
  ],
  "recall-alerts": [
    { date: "Mar 24", value: 3 }, { date: "Mar 25", value: 3 },
    { date: "Mar 26", value: 4 }, { date: "Mar 27", value: 4 },
    { date: "Mar 28", value: 5 }, { date: "Mar 29", value: 5 },
    { date: "Mar 30", value: 5 },
  ],
  "safety-checks": [
    { date: "Mar 24", value: 35 }, { date: "Mar 25", value: 42 },
    { date: "Mar 26", value: 38 }, { date: "Mar 27", value: 45 },
    { date: "Mar 28", value: 40 }, { date: "Mar 29", value: 44 },
    { date: "Mar 30", value: 47 },
  ],
};
```

---

## 9. Visit Trend & Complaint Distribution (`src/data/visualization.ts`)

```ts
export interface MonthlyVisit {
  month: string;
  visits: number;
  newPatients: number;
}

export interface ComplaintDistribution {
  complaint: string;
  count: number;
  percentage: number;
  color: string;
}

export const monthlyVisits: MonthlyVisit[] = [
  { month: "Apr 2025", visits: 180, newPatients: 22 },
  { month: "May 2025", visits: 210, newPatients: 28 },
  { month: "Jun 2025", visits: 195, newPatients: 18 },
  { month: "Jul 2025", visits: 240, newPatients: 35 },
  { month: "Aug 2025", visits: 225, newPatients: 30 },
  { month: "Sep 2025", visits: 260, newPatients: 32 },
  { month: "Oct 2025", visits: 275, newPatients: 28 },
  { month: "Nov 2025", visits: 290, newPatients: 25 },
  { month: "Dec 2025", visits: 250, newPatients: 20 },
  { month: "Jan 2026", visits: 310, newPatients: 38 },
  { month: "Feb 2026", visits: 298, newPatients: 30 },
  { month: "Mar 2026", visits: 342, newPatients: 42 },
];

export const complaintDistribution: ComplaintDistribution[] = [
  { complaint: "Hipertensi", count: 185, percentage: 22, color: "#3b82f6" },
  { complaint: "Diabetes Mellitus", count: 142, percentage: 17, color: "#8b5cf6" },
  { complaint: "GERD/Dispepsia", count: 118, percentage: 14, color: "#06b6d4" },
  { complaint: "Infeksi Saluran Napas", count: 98, percentage: 12, color: "#ec4899" },
  { complaint: "Nyeri Sendi", count: 82, percentage: 10, color: "#22c55e" },
  { complaint: "Alergi/Dermatitis", count: 68, percentage: 8, color: "#f59e0b" },
  { complaint: "Asma", count: 52, percentage: 6, color: "#ef4444" },
  { complaint: "Migrain", count: 42, percentage: 5, color: "#64748b" },
  { complaint: "Lainnya", count: 48, percentage: 6, color: "#94a3b8" },
];
```

---

## Data Generation Notes for the developer

1. **Patients**: Generate remaining 40 patients (patient-011 to patient-050) following the same patterns. Distribute across all 34 provinces with heavier weight on Java. Use diverse Indonesian names.

2. **Heatmap cells**: Generate the full 12x12 matrix (144 cells) using the side effect data from the drugs database. Cross-reference: if a drug has a listed side effect, use its frequencyPercent. If not, use 0.

3. **Molecule coordinates**: Generate realistic 3D atom positions. Use chemistry knowledge:
   - Benzene rings: hexagonal, bond length ~1.4A, all atoms in same plane
   - C-C single bond: ~1.54A
   - C=O double bond: ~1.23A
   - C-H bond: ~1.09A
   - Tetrahedral angles: ~109.5 degrees
   - Center each molecule at [0, 0, 0]

4. **Indonesia TopoJSON**: Download or reference the GeoJSON/TopoJSON file. Match province IDs (ID-JB, ID-JT, etc.) between the map data and the TopoJSON properties.

5. **All timestamps**: Use ISO 8601 format. Range from Jan 2025 to Mar 30, 2026.
