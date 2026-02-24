# Product Design Document

## Project: Drive Space Analyzer (macOS-first)

# 1. Vision

**Drive Space Analyzer** is a high-performance, extensible disk analysis engine and toolchain that helps users understand exactly:

* What is consuming disk space
* Where it is located
* Why it exists
* Whether it is safe to remove

It begins as a **macOS-optimized disk analysis system**, built on a Rust core, with:

* A low-level public API
* A powerful CLI
* A future cross-platform GUI

The long-term vision is to become:

> The most accurate, fastest, and most extensible disk intelligence system for developers, power users, and professionals.

# 2. Core Problem

Users frequently run out of disk space unexpectedly and have no idea what is taking up space

* They don’t understand:
  * System caches
  * Xcode build artifacts
  * Docker volumes
  * Node modules
  * Video render caches
  * Game install artifacts
  * iOS backups
  * Time Machine local snapshots

Existing tools are:

* Slow
* Not transparent
* Not programmable
* Not extensible
* Not developer-friendly

# 3. Product Goals

## 3.1 Primary Goal

> Help users quickly and accurately understand where their disk space is going and safely reclaim it.

## 3.2 Strategic Goals

1. Build a **high-performance core engine** with a public API.
2. Build a CLI that developers and power users love.
3. Architect the system to support:
   * macOS
   * Windows
   * Linux
4. Design extensibility for:
   * OS-specific optimizations
   * Professional profiles (video editing, gaming, dev environments, etc.)
5. Maintain a clean separation between:
   * Engine
   * Analysis logic
   * OS-specific heuristics
   * UI layers

# 4. Non-Goals

## 4.1 Not a File Manager

* Not replacing Finder
* Not replacing file explorers

## 4.2 Not a Cleanup Wizard (at least not initially)

* No automatic deletion
* No “1-click clean everything”
* No registry cleaning
* No risky heuristics

## 4.3 Not a Backup System

* Not Time Machine
* Not cloud sync
* Not versioning

## 4.4 Not an Antivirus or Security Scanner

* Not scanning malware
* Not scanning for vulnerabilities

## 4.5 Not a System Optimizer

* Not RAM cleaner
* Not CPU optimizer
* Not “boost your Mac” gimmick

# 5. Objectives

## 5.1 Technical Objectives

* O(N) traversal over filesystem
* Minimal memory overhead
* Streaming analysis (no need to load everything into memory)
* Parallel directory traversal
* Bundle-aware (macOS .app, .framework, etc.)
* Handle:
  * Symlinks
  * Hard links
  * Permissions
  * Sparse files
  * APFS snapshots (macOS - eventually)

## 5.2 User Objectives

Users should be able to:
* See largest directories
* See largest files
* See size distribution by:
  * File type
  * Extension
  * Owner
  * Creation date
  * Last modified
* Identify redundant large files
* Identify development artifacts
* Identify cache directories
* Identify stale backups

# 6. High-Level Architecture

```
drive-space-analyzer/
│
├── core/                # Rust engine (filesystem scanning + metrics)
├── analysis/            # Higher-level metrics & domain logic
├── os-macos/            # macOS-specific logic & tooling
├── os-linux/
├── os-windows/
├── cli/                 # CLI interface
└── gui/                 # Future cross-platform GUI
```

# 7. Feature Set

# 7.1 Core Engine

### Purpose:

Low-level high-performance file traversal and metric computation.

### Responsibilities:

1. Recursive directory traversal
2. File metadata collection:
   * Path
   * Size
   * Allocated size
   * Creation date
   * Modified date
   * Owner
   * File type
3. Parallel scanning
4. Directory size aggregation
5. Skip rules
6. Bundle detection (macOS)

### Public API Example

```rust
pub trait FileAnalyzer {
    fn scan(&self, root: &Path) -> ScanResult;
}

pub struct ScanOptions {
    pub follow_symlinks: bool,
    pub treat_bundles_as_files: bool,
    pub include_hidden: bool,
}
```

### Design Constraints

* Must not allocate large in-memory trees unless requested
* Should allow streaming output
* Should allow incremental analysis

# 7.2 Metrics Engine

### Computed Metrics

* Total size
* Size per directory
* Size per file extension
* Size per file type
* Top N largest files
* Top N largest directories
* Histogram of file sizes
* Age distribution

# 7.3 macOS-Specific Features

macOS is phase 1 priority.

### macOS-Specific Optimizations

* Detect:

  * `.app` bundles
  * `.framework`
  * `.xcarchive`
  * Xcode DerivedData
  * iOS backups
  * Homebrew cache
  * Docker volumes
  * Time Machine local snapshots
  * iCloud local cache
  * Final Cut Pro cache
  * Adobe cache

### APFS Awareness (Future)

* Sparse files
* Snapshots
* Clones

# 7.4 CLI Tool

### Goals:

* Scriptable
* Fast
* JSON output
* UNIX-friendly

### Example Usage

```bash
dsa scan /
dsa scan ~/ --top 20
dsa scan ~/ --group-by extension
dsa scan ~/ --profile video-editing
```

### Output Modes

* Table
* JSON
* Tree
* Histogram
* CSV

### Advanced Features

* Diff between two scans
* Export results
* Pipe-friendly
* Configurable ignore rules

# 7.5 GUI (Future)

Cross-platform (Tauri or something similar TBD).

### Features:

* Treemap visualization
* Interactive drill-down
* Smart suggestions:
  * “These 12GB are Xcode build artifacts”
  * “These 45GB are Final Cut render files”
* Safe delete recommendations
* Profile-based analysis

# 8. Profiles

Profiles enable domain-specific heuristics.

### 8.1 Developer Profile

* Node modules
* Cargo target
* Xcode DerivedData
* Docker images
* Python venvs

### 8.2 Video Editor Profile

* Render caches
* Proxy media
* DaVinci Resolve cache
* Adobe Premiere cache

### 8.3 Gamer Profile

* Steam library
* Game install leftovers
* Shader cache

### 8.4 Data Scientist Profile

* Jupyter checkpoints
* Large datasets
* Model artifacts
* Docker volumes

Profiles are essentially:

```rust
struct Profile {
    name: String,
    detection_rules: Vec<Rule>,
}
```


# 9. Performance Requirements

* Must handle millions of files
* Should scan a 1TB disk within reasonable time
* Parallel traversal
* Controlled memory footprint
* Optional incremental cache system

# 10. Safety Principles

1. Never delete automatically.
2. Always explain why something is large.
3. Never hide system-critical directories.
4. Be transparent in heuristics.


# 11. UX Philosophy

This tool should feel:

* Honest
* Developer-friendly
* Transparent
* Deterministic
* Reproducible

There should be no magic and everything should be inspectable.


# 12. Future Expansion Ideas

* File similarity detection
* Duplicate detection
* Git repository analysis
* Docker layer breakdown
* Time-series disk usage
* Integration with your larger local-first ecosystem
* Drive health analytics
* NAS support
* Network scanning

# 13. Success Criteria

### Technical

* Handles > 5M files without crashing
* Deterministic results
* Works across APFS edge cases

### User

* User reclaims >10–100GB easily
* Users understand why space is consumed
* Developers use CLI in scripts


# 14. MVP Definition (macOS)

MVP should include:

* Rust scanning engine
* Directory size aggregation
* Top N largest files
* Top N largest directories
* CLI interface
* JSON output
* macOS bundle detection
* Developer profile
