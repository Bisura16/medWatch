# DESIGN_SYSTEM.md - MedWatch Premium Visual Specifications

This document is the single source of truth for all visual decisions. the developer must read this before writing any styling code.

---

## 1. Color Palette

### Brand Colors (constant across themes)
```
--brand-blue:     #3b82f6  (blue-500)
--brand-purple:   #8b5cf6  (purple-500)
--brand-teal:     #06b6d4  (cyan-500)
--brand-pink:     #ec4899  (pink-500)
--brand-green:    #22c55e  (green-500)
--brand-amber:    #f59e0b  (amber-500)
--brand-red:      #ef4444  (red-500)
```

### Dark Mode Palette
```
Background:
--bg-base:        #0a0a0f     (near-black with slight blue)
--bg-elevated:    #12121a     (cards behind glass)
--bg-surface:     rgba(255, 255, 255, 0.05)   (glass card fill)
--bg-surface-hover: rgba(255, 255, 255, 0.08) (glass card hover)

Borders:
--border-glass:   rgba(255, 255, 255, 0.08)
--border-glass-hover: rgba(255, 255, 255, 0.15)
--border-accent:  rgba(59, 130, 246, 0.5)     (focused/active)

Text:
--text-primary:   #f8fafc     (slate-50)
--text-secondary: #94a3b8     (slate-400)
--text-muted:     #64748b     (slate-500)
--text-accent:    #60a5fa     (blue-400)

Shadows:
--shadow-glass:   0 8px 32px 0 rgba(0, 0, 0, 0.36)
--shadow-glow:    0 0 40px rgba(59, 130, 246, 0.15)
```

### Light Mode Palette
```
Background:
--bg-base:        #fafaf9     (stone-50)
--bg-elevated:    #f5f5f4     (stone-100)
--bg-surface:     rgba(255, 255, 255, 0.70)
--bg-surface-hover: rgba(255, 255, 255, 0.85)

Borders:
--border-glass:   rgba(0, 0, 0, 0.06)
--border-glass-hover: rgba(0, 0, 0, 0.12)
--border-accent:  rgba(59, 130, 246, 0.4)

Text:
--text-primary:   #0f172a     (slate-900)
--text-secondary: #64748b     (slate-500)
--text-muted:     #94a3b8     (slate-400)
--text-accent:    #2563eb     (blue-600)

Shadows:
--shadow-glass:   0 8px 32px 0 rgba(0, 0, 0, 0.08)
--shadow-glow:    0 0 40px rgba(59, 130, 246, 0.08)
```

---

## 2. Ambient Gradient Blobs

These are the most critical visual element. Without them, glassmorphism looks like nothing.

### What They Are
Large, blurred, semi-transparent circles of color positioned absolutely behind the main content. They create the colorful backdrop that glass cards blur and distort.

### Dark Mode Blobs
Place these in AmbientBackground.tsx component, rendered behind all page content:

```
Blob 1 (purple):
  position: top-left area (-10% top, -5% left)
  size: 600px x 600px
  color: radial-gradient(circle, rgba(124, 58, 237, 0.25) 0%, transparent 70%)
  filter: blur(80px)

Blob 2 (blue):
  position: top-right area (-5% top, 60% left)
  size: 500px x 500px
  color: radial-gradient(circle, rgba(59, 130, 246, 0.20) 0%, transparent 70%)
  filter: blur(80px)

Blob 3 (teal):
  position: center-bottom area (60% top, 30% left)
  size: 400px x 400px
  color: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)
  filter: blur(80px)

Blob 4 (pink):
  position: bottom-right area (70% top, 80% left)
  size: 350px x 350px
  color: radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, transparent 70%)
  filter: blur(80px)
```

### Light Mode Blobs
Same positions, but softer colors and lower opacity:

```
Blob 1: rgba(167, 139, 250, 0.15)   (lavender)
Blob 2: rgba(147, 197, 253, 0.15)   (sky blue)
Blob 3: rgba(110, 231, 183, 0.10)   (mint)
Blob 4: rgba(251, 191, 36, 0.08)    (soft amber)
```

### Implementation Notes
- Use absolute positioning inside a fixed container with pointer-events-none
- Add subtle CSS animation: slow float/drift (20-30s loop, translateY 20-40px)
- Use mix-blend-mode: normal (not multiply/screen, those cause issues)
- Container must have overflow: hidden to prevent horizontal scroll
- z-index: 0 (behind everything)

### Tailwind Implementation
```css
/* globals.css */
@layer utilities {
  .ambient-blob {
    @apply absolute rounded-full pointer-events-none;
    filter: blur(80px);
  }
  .ambient-blob-animate {
    animation: blob-float 25s ease-in-out infinite alternate;
  }
}

@keyframes blob-float {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
  100% { transform: translate(10px, -10px) scale(1.02); }
}
```

---

## 3. Glass Card System

### Base GlassCard Component

```tsx
// Base classes for ALL glass cards:

// Dark mode:
"bg-white/[0.05] backdrop-blur-xl border border-white/[0.08] rounded-2xl shadow-[0_8px_32px_0_rgba(0,0,0,0.36)]"

// Light mode (via dark: prefix inversion):
"bg-white/70 backdrop-blur-xl border border-black/[0.06] rounded-2xl shadow-[0_8px_32px_0_rgba(0,0,0,0.08)]"

// Combined Tailwind (use dark: variant):
"bg-white/70 dark:bg-white/[0.05] backdrop-blur-xl border border-black/[0.06] dark:border-white/[0.08] rounded-2xl shadow-lg dark:shadow-[0_8px_32px_0_rgba(0,0,0,0.36)]"
```

### Glass Card Variants

**Default (content cards, stat cards):**
```
padding: p-6
hover: hover:bg-white/80 dark:hover:bg-white/[0.08]
hover border: hover:border-black/[0.1] dark:hover:border-white/[0.12]
transition: transition-all duration-300
```

**Elevated (modals, popups, command palette):**
```
bg-white/80 dark:bg-white/[0.08]
backdrop-blur-2xl
border-white/[0.12] dark:border-white/[0.12]
shadow-2xl dark:shadow-[0_16px_48px_0_rgba(0,0,0,0.5)]
```

**Subtle (sidebar, nested cards):**
```
bg-white/50 dark:bg-white/[0.03]
backdrop-blur-lg
border-white/[0.04] dark:border-white/[0.05]
shadow-sm dark:shadow-none
```

**Accent Glow (active states, selected items):**
```
Same as default PLUS:
shadow-[0_0_30px_rgba(59,130,246,0.15)] (blue glow)
border-blue-500/30
```

### Gradient Borders (premium detail)
For hero cards or important sections, use a gradient border technique:

```tsx
// Outer wrapper with gradient background
<div className="p-[1px] rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20">
  // Inner card with glass fill
  <div className="bg-white/70 dark:bg-white/[0.05] backdrop-blur-xl rounded-2xl p-6">
    {children}
  </div>
</div>
```

---

## 4. Typography Scale

Use Inter font. Import via next/font/google.

```
Display (hero numbers, big KPIs):
  text-4xl md:text-5xl font-bold tracking-tight

Page Title:
  text-2xl md:text-3xl font-semibold tracking-tight

Section Title:
  text-xl font-semibold

Card Title:
  text-lg font-medium

Body:
  text-sm md:text-base font-normal leading-relaxed

Small / Caption:
  text-xs font-medium text-secondary uppercase tracking-wider

Data / Numbers:
  font-mono tabular-nums

Badge / Tag:
  text-xs font-medium px-2.5 py-0.5 rounded-full
```

### Text Colors

Always use semantic classes:
```
Primary text:     text-slate-900 dark:text-slate-50
Secondary text:   text-slate-500 dark:text-slate-400
Muted text:       text-slate-400 dark:text-slate-500
Accent text:      text-blue-600 dark:text-blue-400
Success text:     text-green-600 dark:text-green-400
Warning text:     text-amber-600 dark:text-amber-400
Danger text:      text-red-600 dark:text-red-400
```

---

## 5. Sidebar Specifications

### Layout
```
Width: w-72 (288px) expanded, w-20 (80px) collapsed
Height: h-screen, fixed left
Background: bg-white/50 dark:bg-white/[0.03] backdrop-blur-2xl
Border right: border-r border-black/[0.06] dark:border-white/[0.06]
Padding: p-4
Transition: transition-all duration-300 ease-in-out
```

### Logo Area
```
Top of sidebar
"MedWatch" text: text-xl font-bold
Subtitle: text-xs text-secondary "Drug Safety Monitor"
Collapsed: show only "M" icon
Margin bottom: mb-8
```

### Menu Items
```
Each item:
  flex items-center gap-3 px-3 py-2.5 rounded-xl
  text-sm font-medium
  text-slate-600 dark:text-slate-400
  hover:bg-white/60 dark:hover:bg-white/[0.06]
  hover:text-slate-900 dark:hover:text-slate-200
  transition-all duration-200

Active item:
  bg-white/70 dark:bg-white/[0.08]
  text-blue-600 dark:text-blue-400
  shadow-sm dark:shadow-none
  border border-black/[0.04] dark:border-white/[0.08]

Icon size: w-5 h-5
Collapsed: show icon only, centered, tooltip on hover
Gap between items: space-y-1
```

### Bottom Section
```
Separator: border-t border-black/[0.06] dark:border-white/[0.06] mt-auto pt-4

Theme toggle:
  Icon button: Sun (light) / Moon (dark)
  Animated rotation on switch (180deg, 300ms)
  Same hover styling as menu items

Collapse button:
  ChevronLeft icon (expanded) / ChevronRight (collapsed)
  Same hover styling as menu items
```

---

## 6. Component Specifications

### Stat Card (Dashboard KPI)
```
GlassCard with:
  - Small icon top-left (in a rounded-lg bg-blue-500/10 p-2 container)
  - Value: text-3xl font-bold font-mono (animated counter)
  - Label: text-sm text-secondary
  - Optional sparkline (50px tall, right side)
  - Optional trend indicator: +12% (green) or -5% (red) with arrow
```

### Data Table
```
GlassCard wrapping the table:
  - Header row: text-xs uppercase tracking-wider text-secondary
  - Header bg: bg-white/30 dark:bg-white/[0.03]
  - Rows: border-b border-black/[0.04] dark:border-white/[0.04]
  - Row hover: bg-white/40 dark:bg-white/[0.03]
  - Alternating rows: not needed (glass style works without)
  - Pagination: bottom of card, flex justify-between
  - Status badges: rounded-full with appropriate color bg/text
```

### Form Inputs
```
shadcn Input with glass override:
  bg-white/50 dark:bg-white/[0.05]
  border border-black/[0.08] dark:border-white/[0.08]
  focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20
  rounded-xl
  placeholder:text-slate-400 dark:placeholder:text-slate-500
```

### Buttons

```
Primary:
  bg-blue-600 hover:bg-blue-700 text-white
  shadow-lg shadow-blue-600/25
  rounded-xl px-4 py-2.5

Secondary (glass):
  bg-white/50 dark:bg-white/[0.06]
  border border-black/[0.08] dark:border-white/[0.08]
  hover:bg-white/70 dark:hover:bg-white/[0.1]
  rounded-xl px-4 py-2.5

Danger:
  bg-red-600 hover:bg-red-700 text-white
  shadow-lg shadow-red-600/25

Ghost:
  bg-transparent hover:bg-white/50 dark:hover:bg-white/[0.05]
  text-secondary hover:text-primary
```

### Badges / Status Pills
```
Active/Online:    bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20
Warning:          bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20
Danger/Critical:  bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20
Info:             bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20
Neutral:          bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-500/20
```

### Chart Styling
```
All charts sit inside GlassCard

Recharts overrides:
  - Background: transparent
  - Grid lines: stroke rgba(148, 163, 184, 0.1)
  - Axis text: fill #94a3b8 (dark), fill #64748b (light), fontSize 12
  - Tooltip:
      bg-white/80 dark:bg-slate-900/90
      backdrop-blur-xl
      border border-black/[0.08] dark:border-white/[0.08]
      rounded-xl shadow-xl
      text-sm
  - Colors for data series (in order):
      #3b82f6 (blue)
      #8b5cf6 (purple)
      #06b6d4 (teal)
      #ec4899 (pink)
      #22c55e (green)
      #f59e0b (amber)
  - Area charts: fill with gradient from color/30 to transparent
  - Bar charts: rounded-t corners (radius 4-6px)
```

---

## 7. Animation Specifications

### Page Enter
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -10 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
>
```

### Card Stagger (multiple cards on a page)
```tsx
// Parent
<motion.div
  initial="hidden"
  animate="visible"
  variants={{
    hidden: {},
    visible: { transition: { staggerChildren: 0.08 } }
  }}
>

// Each child card
<motion.div
  variants={{
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } }
  }}
>
```

### Scroll Reveal
```tsx
<motion.div
  initial={{ opacity: 0, y: 30 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, ease: "easeOut" }}
  viewport={{ once: true, margin: "-50px" }}
>
```

### Hover Lift (cards)
```tsx
<motion.div
  whileHover={{ y: -4, transition: { duration: 0.2 } }}
>
```

### Number Counter
```tsx
// Use framer-motion useMotionValue + useTransform + animate
// Count from 0 to target over 1.5s with easeOut
// Format with toLocaleString() for comma separators
// Trigger when component mounts or scrolls into view
```

### Theme Toggle Animation
```
Icon rotation: 180deg over 300ms
Background: smooth color transition via CSS transition-colors duration-500
Ambient blobs: opacity transition 500ms
```

### Sidebar Collapse
```
Width transition: 300ms ease-in-out
Menu text: opacity fade 200ms (hide before width shrinks)
Logo: crossfade between full text and icon
```

### Skeleton Pulse
```
Use shadcn Skeleton
bg-slate-200 dark:bg-white/[0.06]
animate-pulse
Show for 800ms simulated delay, then reveal real content with fade-in
```

---

## 8. Responsive Breakpoints

```
Mobile:    < 768px   -- sidebar hidden (hamburger toggle), single column
Tablet:    768-1024px -- sidebar collapsed by default, 2-col grid
Desktop:   1024-1440px -- sidebar expanded, 3-4 col grid
Wide:      > 1440px  -- max-w-7xl centered content
```

### Mobile Sidebar Behavior
- Hidden off-screen by default
- Hamburger button in top-left
- Slides in as overlay with dark backdrop
- Close on backdrop click or X button

---

## 9. Indonesia Map Specifications

### Map Container
```
GlassCard, full width, aspect-ratio 16/9
Map centered on Indonesia: center [118, -2.5], scale ~1200
```

### Province Styling
```
Default fill: slate-700/50 (dark), slate-300/50 (light)
Choropleth scale (by patient density):
  Very low:   blue-900/40 -> blue-200/40
  Low:        blue-700/50 -> blue-300/50
  Medium:     blue-500/60 -> blue-400/60
  High:       blue-400/70 -> blue-500/70
  Very high:  blue-300/80 -> blue-600/80

Stroke: slate-500/30 (dark), slate-400/40 (light), strokeWidth 0.5
Hover: brightness increase, stroke-white/50, strokeWidth 1.5
Active/clicked: stroke-blue-400, strokeWidth 2
```

### Tooltip (on hover)
```
Glass tooltip near cursor:
  Province name (font-medium)
  Clinics: {number}
  Patients: {number}
  Density badge (Low/Med/High)
```

### Legend
```
Bottom-left of map card
Horizontal color scale bar (5 steps)
Labels: "Low" to "High"
Glass background
```

---

## 10. Drug Interaction Network Specifications

### Container
```
GlassCard, full width, min-height 500px
Dark bg inside: bg-slate-950/50 (dark), bg-slate-50/50 (light) -- darker than normal to make nodes pop
```

### Nodes
```
Circles, radius based on connection count (8-20px)
Color by drug category:
  Analgesic:      #3b82f6 (blue)
  Antibiotic:     #22c55e (green)
  Antihypertensive: #8b5cf6 (purple)
  Antihistamine:  #f59e0b (amber)
  NSAID:          #ef4444 (red)
  Gastrointestinal: #06b6d4 (teal)
  Other:          #94a3b8 (slate)

Glow effect on hover: drop-shadow with node color
Label: drug name, text-xs, white
```

### Edges
```
Stroke: rgba(148, 163, 184, 0.2)
Hover (when connected node hovered): rgba(148, 163, 184, 0.6)
Width: 1-2px based on interaction severity
```

### Controls
```
Top-right of card:
  Zoom in/out buttons (glass style)
  Reset view button
  Category filter checkboxes
```

---

## 11. 3D Molecule Viewer Specifications

### Container
```
GlassCard, aspect-ratio 4/3 or 16/10
Canvas background: transparent (shows ambient blobs through glass)
```

### Molecule Rendering
```
Atoms: spheres with element-based coloring
  Carbon: #4a4a4a
  Hydrogen: #ffffff
  Oxygen: #ef4444
  Nitrogen: #3b82f6
  Sulfur: #f59e0b
  Chlorine: #22c55e

Atom radius: proportional to atomic radius (C=0.7, H=0.3, O=0.6, N=0.65)
Bonds: cylinders between atom positions, gray #94a3b8, radius 0.1
Double bonds: two thinner cylinders with slight offset

Lighting:
  Ambient light: intensity 0.4
  Point light 1: top-right, white, intensity 0.8
  Point light 2: bottom-left, blue tint #60a5fa, intensity 0.3
```

### Controls
```
OrbitControls: rotate (left-drag), zoom (scroll), pan (right-drag)
Auto-rotate: slow spin (speed 1), pause on hover/drag
Molecule selector: dropdown above the viewer (3-5 molecules: Aspirin, Ibuprofen, Paracetamol, Amoxicillin, Caffeine)
```

### Atom Hover
```
On hover: atom glows (emissive property increase)
Tooltip near cursor: element name + atom label
```

---

## 12. Side Effect Heatmap Specifications

### Container
```
GlassCard, full width, scrollable horizontally if needed
```

### Grid
```
Rows: drugs (10-15)
Columns: side effects (10-15)
Cell size: 40-50px square

Cell coloring (by frequency percentage):
  0%:     transparent / bg-slate-800/20
  1-10%:  blue-900/30
  11-25%: blue-700/50
  26-50%: blue-500/60
  51-75%: purple-500/60
  76-100%: pink-500/70

Cell hover: border-white/50, show exact percentage
Cell border: 1px solid rgba(255,255,255,0.04)
```

### Headers
```
Row headers (drug names): sticky left, text-xs, glass bg
Column headers (side effects): sticky top, text-xs, rotated -45deg, glass bg
```

### Tooltip
```
Glass tooltip:
  Drug: {name}
  Side Effect: {name}
  Frequency: {percentage}%
  Severity: {Low/Medium/High}
```

---

## 13. globals.css Template

```css
@import "tailwindcss";

/* Glass utility classes */
@layer utilities {
  .glass {
    @apply bg-white/70 dark:bg-white/[0.05] backdrop-blur-xl
           border border-black/[0.06] dark:border-white/[0.08]
           rounded-2xl shadow-lg dark:shadow-[0_8px_32px_0_rgba(0,0,0,0.36)];
  }

  .glass-subtle {
    @apply bg-white/50 dark:bg-white/[0.03] backdrop-blur-lg
           border border-black/[0.04] dark:border-white/[0.05]
           rounded-xl;
  }

  .glass-elevated {
    @apply bg-white/80 dark:bg-white/[0.08] backdrop-blur-2xl
           border border-black/[0.08] dark:border-white/[0.12]
           rounded-2xl shadow-2xl dark:shadow-[0_16px_48px_0_rgba(0,0,0,0.5)];
  }

  .glass-hover {
    @apply transition-all duration-300
           hover:bg-white/80 dark:hover:bg-white/[0.08]
           hover:border-black/[0.1] dark:hover:border-white/[0.12]
           hover:shadow-xl;
  }

  .text-gradient {
    @apply bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500
           bg-clip-text text-transparent;
  }

  .ambient-blob {
    @apply absolute rounded-full pointer-events-none select-none;
    filter: blur(80px);
  }
}

@keyframes blob-float {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
  100% { transform: translate(10px, -10px) scale(1.02); }
}

/* Recharts tooltip override */
.recharts-tooltip-wrapper .recharts-default-tooltip {
  @apply !bg-white/80 dark:!bg-slate-900/90 !backdrop-blur-xl
         !border !border-black/[0.08] dark:!border-white/[0.08]
         !rounded-xl !shadow-xl;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}

/* Selection color */
::selection {
  @apply bg-blue-500/30 text-white;
}
```

---

## 14. Icon Usage

Use lucide-react exclusively. Import individually:

```tsx
import { LayoutDashboard, Search, GitCompare, Users, BarChart3, ShieldCheck, Map, Network, Atom, Grid3x3, FileDown, Sun, Moon, ChevronLeft, ChevronRight, Plus, Trash2, Edit, Filter, Download, AlertTriangle, CheckCircle, XCircle, TrendingUp, TrendingDown, Activity, Command } from "lucide-react";
```

Icon styling in glass context:
```
Default: w-5 h-5 text-slate-500 dark:text-slate-400
Active: text-blue-600 dark:text-blue-400
In colored container: text-white inside bg-{color}-500/10 rounded-lg p-2
```

---

## 15. Motion Preferences

Always wrap animations with reduced-motion check:

```tsx
const prefersReducedMotion = useReducedMotion();

// Then conditionally apply:
initial={prefersReducedMotion ? false : { opacity: 0, y: 20 }}
```

Or use Framer Motion's built-in:
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
  // Framer Motion auto-respects prefers-reduced-motion when using layout animations
>
```
