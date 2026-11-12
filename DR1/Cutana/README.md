[//]: # (Copyright © European Space Agency, 2026.)
[//]: # ()
[//]: # (This file is subject to the terms and conditions defined in file 'LICENCE.txt', which)
[//]: # (is part of this source code package. No part of the package, including)
[//]: # (this file, may be copied, modified, propagated, or distributed except according to)
[//]: # (the terms contained in the file 'LICENCE.txt'.)
# Cutana - High-Performance Astronomical Cutout Pipeline

Cutana is a high-performance Python pipeline for creating astronomical image cutouts from large FITS tile collections, designed for efficient processing of ESA Datalabs and other astronomical datasets.

## Installation

```bash
# Create conda environment
conda env create -f environment.yml
conda activate cutana
```

## Basic Usage

```python
import pandas as pd
from cutana import get_default_config, Orchestrator

# Load source catalogue
catalogue = pd.read_csv("sources.csv")

# Configure processing using new config system
config = get_default_config()
config.source_catalogue = "sources.csv"
config.output_dir = "cutouts_output/"
config.max_workers = 4
config.output_format = "zarr"
config.target_resolution = 150
config.selected_extensions = [{"name": "VIS", "ext": "PRIMARY"}]               

# Process cutouts
orchestrator = Orchestrator(config)
results = orchestrator.start_processing(catalogue)
```

## CSV Format Requirements

Your source catalogue must contain these columns:

```csv
SourceID,RA,Dec,diameter_pixel,fits_file_paths
TILE_102018666_12345,45.123,12.456,128,"['/path/to/fits1.fits', '/path/to/fits2.fits']"
TILE_102018666_12346,45.124,12.457,256,"['/path/to/fits1.fits']"
```

**Column Specifications:**
- `SourceID` (str): Unique identifier for each source
- `RA` (float): Right Ascension in degrees (ICRS)
- `Dec` (float): Declination in degrees (ICRS)
- `diameter_pixel` (int): Cutout diameter in pixels (square cutouts)
- `fits_file_paths` (str): JSON-formatted list of FITS file paths

## Multi-Channel Processing

Cutana supports multi-channel FITS processing where sources can have multiple FITS files:

**Single-Channel:**
```csv
SourceID,RA,Dec,diameter_pixel,fits_file_paths
TILE_102018666_12345,45.123,12.456,128,"['/path/to/vis_image.fits']"
```

**Multi-Channel (NIR H, J, Y bands):**
```csv
SourceID,RA,Dec,diameter_pixel,fits_file_paths
TILE_102018666_12345,45.123,12.456,128,"['/path/to/nir_h.fits', '/path/to/nir_j.fits', '/path/to/nir_y.fits']"
```

**Note:** When using multiple FITS files with different pixel resolutions, you must use `diameter_arcsec` instead of `diameter_pixel` to avoid ambiguity about which resolution is being referenced.

## ESA Datalabs Usage

### 1. Create Data Layout CSV

```bash
python scripts/create_q1_data_layout.py --data-root /data --output Q1_data_layout.csv
```

This scans the datalabs directory structure and creates a CSV with tile information:

```csv
tileID,catalogue_path,NIR_H_path,NIR_J_path,NIR_Y_path,VIS_path,ra_min,ra_max,dec_min,dec_max,nr_of_sources
102018666,/data/user/q1/Q1_R1/MER_FINAL_CATALOG/102018666/EUC_MER_FINAL-CAT_TILE102018666.fits,/data/user/q1/Q1_R1/MER/102018666/NISP/EUC_MER_BGSUB-MOSAIC-NIR-H_TILE102018666.fits,/data/user/q1/Q1_R1/MER/102018666/NISP/EUC_MER_BGSUB-MOSAIC-NIR-J_TILE102018666.fits,/data/user/q1/Q1_R1/MER/102018666/NISP/EUC_MER_BGSUB-MOSAIC-NIR-Y_TILE102018666.fits,/data/user/q1/Q1_R1/MER/102018666/VIS/EUC_MER_BGSUB-MOSAIC-VIS_TILE102018666.fits,45.123456,45.987654,12.123456,12.987654,15000
```

### 2. Run Benchmark

```bash
# Process 2 tiles with 1000 sources each using NIR bands
python benchmarking/benchmark_q1_datalabs.py \
  --layout-csv Q1_data_layout.csv \
  --n-tiles 2 \
  --sources-per-tile 1000 \
  --fits-channels NIR_H_path,NIR_J_path,NIR_Y_path \
  --output-dir /media/team_workspaces/AnomalyMatch/Q1_experiments/ \
  --max-workers 4
```

### 3. Production Configuration
The module incorporates a [flux conversion](cutana/flux_conversion.py) from the image units to Jansky by default.

```python
from cutana import get_default_config, save_config_toml

# Start with default configuration
config = get_default_config()

# Customize for production use
config.max_workers = 8                       # Adjust based on available CPU cores
config.N_batch_cutout_process = 1000         # Batch size within each process
config.output_format = "zarr"                # "zarr" or "fits"
config.output_dir = "/path/to/output/"       # Output directory path
config.fits_extensions = ["PRIMARY"]         # FITS extensions to process
config.target_resolution = 150               # Target pixel resolution
config.normalisation_method = "linear"       # "linear", "log", "asinh", "zscale"
config.log_level = "INFO"                    # Logging verbosity
config.apply_flux_conversion = True          # Flux conversion for eg Euclid, default True
config.flux_conversion_keywords.AB_zeropoint = "MAGZERO"  # header keyword for ZP

# Unified normalization parameters (method-specific defaults applied automatically)
config.normalisation.percentile = 99.8                     # Percentile clipping for all methods (0.0-100.0)
config.normalisation.a = 0.7                               # Unified transition parameter: asinh=0.7, log=1000.0
config.normalisation.n_samples = 1000                      # ZScale samples (100-10000)  
config.normalisation.contrast = 0.25                       # ZScale contrast (0.01-1.0)

# Save configuration for reproducibility
config_path = save_config_toml(config, f"{config.output_dir}/cutana_config.toml")
```

## Stretch/Normalization Configuration

Cutana supports multiple image stretching methods with **unified parameter naming** for optimal visualization and analysis. The `normalisation_method` parameter controls the stretch algorithm, with a single set of parameters that automatically apply appropriate defaults based on the chosen method:

**Unified Parameter Details:**
All normalization parameters are now stored in the `config.normalisation` DotMap object:

- **`config.normalisation.percentile`**: Percentile for data clipping, applied to all stretch methods (default: 99.8, range: 0-100)
- **`config.normalisation.a`**: Unified transition parameter with method-specific defaults:
  - ASINH: 0.7 (controls linear-to-logarithmic transition, range: 0.001-3.0)
  - Log: 1000.0 (scale factor for transition point, range: 0.01-10000.0)
- **`config.normalisation.n_samples`**: Number of samples for ZScale algorithm (default: 1000, range: 100-10000)
- **`config.normalisation.contrast`**: Contrast adjustment for ZScale (default: 0.25, range: 0.01-1.0)

**Note**: The unified `a` parameter automatically applies the appropriate default value based on the selected normalization method, eliminating the need for method-specific parameter names.

### Linear Stretch
```python
from cutana import get_default_config

config = get_default_config()
config.normalisation_method = "linear"
config.normalisation.percentile = 99.8             # Percentile clipping (default)
```

### ASINH Stretch (Recommended for astronomical data)
```python
from cutana import get_default_config

config = get_default_config()
config.normalisation_method = 'asinh'
config.normalisation.percentile = 99.8             # Percentile clipping (default)
config.normalisation.a = 0.7                       # Transition parameter (default for asinh)
```

### Log Stretch
```python
from cutana import get_default_config

config = get_default_config()
config.normalisation_method = 'log'
config.normalisation.percentile = 99.8             # Percentile clipping (default)
config.normalisation.a = 1000.0                    # Scale factor (default for log)
```

### ZScale Stretch (DS9-compatible)
```python
from cutana import get_default_config

config = get_default_config()
config.normalisation_method = 'zscale'
config.normalisation.percentile = 99.8             # Percentile clipping (default)
config.normalisation.n_samples = 1000              # Number of samples (default)
config.normalisation.contrast = 0.25               # Contrast parameter (default)
```

## Testing

```bash
# Run all tests
pytest --cov=cutana tests/

# Run specific tests
pytest tests/cutana/test_orchestrator.py -v
pytest tests/cutana/test_cutout_process.py -v
pytest tests/ui/ -v                      # UI tests
```

## Key Features

- **High-Performance Processing**: Parallel processing with memory-isolated worker processes
- **Multi-Channel Support**: Proper grouping of sources with multiple FITS files (80-90% I/O reduction)
- **Advanced Image Stretching**: Linear, ASINH, Log, and ZScale normalization with fitsbolt integration
- **Multiple Output Formats**: Zarr archives and individual FITS files with WCS preservation
- **Resource Management**: Conservative memory estimation and system monitoring
- **Datalabs Integration**: Specialized scripts for ESA Datalabs Q1 data processing
- **Comprehensive Testing**: Full test coverage with 172+ tests

## Performance

- **Typical Throughput**: 100-1000 cutouts/second (depending on size and complexity)
- **Memory Usage**: Conservative estimation at 2.5× FITS file size per worker process
- **FITS Optimization**: Multi-channel sources processed with 80-90% fewer file loads
- **Progress Accuracy**: Correct source-based counting (no more inflated percentages)

## Architecture

**Core Components:**
1. **Orchestrator**: Process management and resource allocation
2. **JobCreator**: FITS set-based optimization for efficient grouping
3. **CutoutProcess**: Unified multi-channel FITS processing
4. **Output Writers**: Zarr archives and individual FITS files
5. **Job Tracker**: Real-time resource monitoring and progress tracking

## Support

- GitHub Issues: For bug reports and feature requests
- Documentation: See `docs/` directory for detailed architecture information
- Test Examples: Review `tests/` for usage examples

## Advanced Usage
### Custom Flux Conversion

If you want to apply a specific conversion to the FITS images when loaded, you can specify a custom flux conversion function. This function must have two inputs (image array and FITS header) and return an image of the same dimensions.

```python
import numpy as np
from astropy.io.fits import Header
from cutana import get_default_config

def my_flux_conversion(image: np.ndarray, header: Header) -> np.ndarray:
    """Custom flux conversion function."""
    # Do some processing steps here based on the FITS extension's header
    zeropoint = header.get("MAGZERO", 25.0)
    return image * 10**(-0.4 * (zeropoint - 25.0))

# Configure with custom flux conversion
config = get_default_config()
config.apply_flux_conversion = True
config.user_flux_conversion_function = my_flux_conversion
```

