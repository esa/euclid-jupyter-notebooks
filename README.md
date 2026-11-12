# Euclid Jupyter Notebooks

Copyright (c) European Space Agency, 2026.

This repository contains **ESA-maintained Jupyter notebooks for accessing, visualising and analysing public data from the ESA Euclid Mission**.

The notebooks are designed primarily for use with the **Euclid App on Euclid Data Space**, where Euclid data products are available through mounted data volumes and the Euclid Science Archive.

## Getting started

The [Euclid App](https://euclid.dataspace.esa.int/) is based on JupyterLab and provides pre-configured environments for working with Euclid data.

When the Euclid App is launched, the notebooks from this repository are copied to:

```text
my_workspace/euclid-jupyterlab-notebooks
```

To get the latest version, delete the `euclid-jupyterlab-notebooks` folder from `my_workspace` and relaunch the Euclid App.

## Data releases

The repository contains examples for the following public Euclid data releases:

- **DR1-Foundation** — [release information](https://www.cosmos.esa.int/web/euclid/data-release-dr1)
- **Q1** — [release information](https://www.cosmos.esa.int/web/euclid/euclid-q1-data-release)
- **Early Release Observations (ERO)** — [release information](https://www.cosmos.esa.int/web/euclid/ero-public-release)

If you are new to Euclid data, we recommend starting with the **DR1-Foundation examples**.

## What the notebooks cover

The examples demonstrate common workflows including:

- querying the Euclid Science Archive with **ADQL** and **Astroquery**;
- accessing products directly from Euclid data volumes on ESA Datalabs;
- visualising Euclid images and spectra;
- creating image cutouts;
- source extraction;
- image colourisation;
- retrieving spectra in bulk; and
- preparing and generating bulk image cutouts.

The Euclid App provides the **EUCLID-TOOLS** environment for general Euclid data access and scientific analysis, together with specialised environments for image colourisation and bulk cutout creation.

## Community-contributed notebooks

Additional scientific workflows contributed by members of the Euclid community are maintained separately in the [Euclid Contributed Jupyter Notebooks repository](https://github.com/esa/euclid-contributed-jupyter-notebooks).

These notebooks are maintained by their respective developers and are not maintained by ESA.

## Documentation and support

- [Euclid Data Space Help Pages]([https://s2e2.cosmos.esa.int/www/euclid_iscience/Public_User_Guide.html](https://euclid.dataspace.esa.int/community/help-pages/EDS_Help_Pages.html))
- [Euclid DR1 information](https://www.cosmos.esa.int/web/euclid/euclid-dr1)
- [ESA Datalabs documentation](https://datalabs.esa.int/help/Datalabs.html)
- [Euclid Helpdesk](https://support.cosmos.esa.int/euclid/)

## Citation and data use

When using Euclid data in a publication, follow the citation, acknowledgement and data-credit requirements for the relevant release:

- [DR1 Data License and Credits](https://www.cosmos.esa.int/web/euclid/dr1-data-credits)
- [Q2 Data License and Credits](https://www.cosmos.esa.int/web/euclid/q2-data-credits)
- [Q1 Data License and Credits](https://www.cosmos.esa.int/en/web/euclid/q1-data-credits)

Data hosted in the ESA Space Science Archives are subject to the [ESA Space Science Archives Terms and Conditions](https://www.cosmos.esa.int/web/esdc/terms-and-conditions).

If ESA Datalabs resources contribute to a scientific publication, please cite:

> Navarro, V. et al. (2024). *ESA Datalabs: Digital Innovation in Space Science*. In: Cortesi, A. (eds) Space Data Management. Studies in Big Data, vol 141. Springer, Singapore.  
> [https://doi.org/10.1007/978-981-97-0041-7_1](https://doi.org/10.1007/978-981-97-0041-7_1)

## Licence

This repository is subject to the terms and conditions defined in `LICENSE.txt`. No part of this package may be copied, modified, propagated or distributed except according to the terms contained in that file.

## About Euclid

**Euclid** is a European space mission built and operated by ESA, with contributions from NASA. The Euclid Consortium provided the scientific instruments and is responsible for the scientific data analysis.

More information: [ESA Euclid Mission](https://www.cosmos.esa.int/web/euclid)
