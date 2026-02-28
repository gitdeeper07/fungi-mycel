# 🍄 FUNGI-MYCEL Shell Completion

FUNGI-MYCEL provides shell completion for bash, zsh, and fish shells to enhance command-line productivity when working with mycelial network intelligence data.

---

## Installation

### Bash
Add to your `~/.bashrc`:
```bash
eval "$(_FUNGI_MYCEL_COMPLETE=bash_source fungi-mycel)"
```

Zsh

Add to your ~/.zshrc:

```zsh
eval "$(_FUNGI_MYCEL_COMPLETE=zsh_source fungi-mycel)"
```

Fish

Add to your ~/.config/fish/config.fish:

```fish
eval (env _FUNGI_MYCEL_COMPLETE=fish_source fungi-mycel)
```

---

Available Commands

```bash
fungi-mycel --help
```

Core Commands

Command Description
fungi-mycel analyze Run mycelial network analysis
fungi-mycel monitor Monitor network activity (ρ_e)
fungi-mycel dashboard Launch interactive dashboard
fungi-mycel sites List available monitoring sites
fungi-mycel alerts Check active network alerts
fungi-mycel export Export MNIS data

Parameter Commands

```bash
fungi-mycel analyze eta-nw          # Natural Weathering Efficiency
fungi-mycel analyze rho-e           # Bioelectrical Pulse Density
fungi-mycel analyze grad-c          # Chemotropic Navigation
fungi-mycel analyze ser             # Symbiotic Exchange Ratio
fungi-mycel analyze k-topo          # Topological Expansion
fungi-mycel analyze abi             # Biodiversity Amplification
fungi-mycel analyze bfs             # Field Stability
fungi-mycel analyze e-a             # Adaptive Resilience
fungi-mycel analyze mnis            # Composite Intelligence Score
```

Site Commands

```bash
fungi-mycel sites list                         # List all 39 sites
fungi-mycel sites show --id bialowieza-01      # Show site details
fungi-mycel sites compare --site1 a --site2 b  # Compare two sites
fungi-mycel sites biome --type temperate       # Filter by biome
```

Data Commands

```bash
fungi-mycel data import --file recordings.npy   # Import field data
fungi-mycel data validate --mnu MNU-2026-001    # Validate MNU
fungi-mycel data export --format csv            # Export data
fungi-mycel data stats --site all               # Show statistics
```

---

Options

Option Description
--site SITE Specify site code (e.g., bialowieza-01)
--mnu MNU Specify MNU ID
--start-date DATE Start date (YYYY-MM-DD)
--end-date DATE End date (YYYY-MM-DD)
--format FORMAT Output format (json, csv, table)
--output FILE Output file path
--config FILE Configuration file
--verbose Verbose output
--debug Debug mode
--biome BIOME Filter by biome type
--min-mnis VALUE Minimum MNIS threshold
--max-mnis VALUE Maximum MNIS threshold

---

Examples

```bash
# Analyze specific site
fungi-mycel analyze --site bialowieza-01 --parameters all

# Monitor bioelectrical activity
fungi-mycel monitor rho-e --site cascade-04 --duration 72h

# Compare two sites
fungi-mycel sites compare --site1 bialowieza-01 --site2 sudbury-01

# Export data as JSON
fungi-mycel export --format json --output data.json --site all

# Check active alerts
fungi-mycel alerts --status active --biome boreal

# List all sites in temperate biome
fungi-mycel sites list --biome temperate --details

# Calculate MNIS for specific MNU
fungi-mycel mnis --mnu MNU-2026-001 --verbose

# Run hypothesis test (H1-H8)
fungi-mycel test --hypothesis H2 --verbose

# Launch dashboard
fungi-mycel dashboard --port 8501 --theme dark

# Process field data
fungi-mycel process --input /data/field/ --output /data/results/ --auto-validate

# Check correlation between parameters
fungi-mycel correlate --param1 rho-e --param2 k-topo
```

---

Tab Completion Features

The completion system provides:

Site Name Completion

· Auto-completes from 39 monitored sites
· Groups by biome type
· Includes site codes and full names

Parameter Completion

· All 8 MNIS parameters
· Parameter groups (core, ml, viz)
· Measurement units

Date Completion

· YYYY-MM-DD format
· Relative dates (today, yesterday, last-week)
· Seasonal ranges

File Path Completion

· For --input and --output options
· Supports .npy, .csv, .fasta, .tif
· Network paths

Format Completion

· json, csv, table, html
· plot (png, svg, pdf)
· report (md, pdf, docx)

Biome Completion

· temperate-broadleaf
· boreal-conifer
· tropical-montane
· mediterranean-woodland
· subarctic-birch

---

Advanced Features

Pipe Support

```bash
# Chain commands
fungi-mycel sites list --biome boreal | fungi-mycel analyze --stdin

# Filter results
fungi-mycel data export --format json | jq '.mnis > 0.8'
```

Environment Variables

```bash
export FUNGI_MYCEL_SITE=bialowieza-01
export FUNGI_MYCEL_CONFIG=~/.fungi_mycel/config.yaml
export FUNGI_MYCEL_DATA_DIR=/data/fungi
```

Custom Completion

```bash
# Add custom completions
cat > ~/.fungi_mycel/completions/custom.sh << 'CUSTOM'
_fungi_mycel_custom_sites() {
    local sites=$(fungi-mycel sites list --quick)
    COMPREPLY=($(compgen -W "$sites" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _fungi_mycel_custom_sites mycel-quick
CUSTOM
```

---

Troubleshooting

If completion isn't working:

1. Check installation:
   ```bash
   which fungi-mycel
   fungi-mycel --version
   ```
2. Reload shell:
   ```bash
   exec $SHELL
   ```
3. Reinstall completions:
   ```bash
   # Bash
   source <(fungi-mycel completion bash)
   
   # Zsh
   source <(fungi-mycel completion zsh)
   
   # Fish
   fungi-mycel completion fish | source
   ```
4. Debug mode:
   ```bash
   fungi-mycel --debug completion test
   ```
5. Check permissions:
   ```bash
   ls -la ~/.fungi_mycel/completions/
   ```

---

Custom Aliases

Add to your shell config:

```bash
# Quick access
alias fm='fungi-mycel'
alias fma='fungi-mycel analyze'
alias fmm='fungi-mycel monitor'
alias fms='fungi-mycel sites'

# Common queries
alias fm-bialowieza='fungi-mycel analyze --site bialowieza-01'
alias fm-alerts='fungi-mycel alerts --status active'
alias fm-dashboard='fungi-mycel dashboard --open'

# MNIS shortcuts
alias mnis-high='fungi-mycel sites list --min-mnis 0.8'
alias mnis-low='fungi-mycel sites list --max-mnis 0.3'
```

---

For more help

```bash
fungi-mycel help completion
fungi-mycel completion --help
man fungi-mycel
```

---

Live Dashboard: https://fungi-mycel.netlify.app
Documentation: https://fungi-mycel.readthedocs.io

🍄 The forest speaks. FUNGI-MYCEL translates.
