#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=1990s
#SBATCH --time=12:00:00
#SBATCH --account=FY220022
#SBATCH --partition=batch
#SBATCH --reservation=flight-cldera

conda activate /nscratch/bmwagma/shared_conda_envs/pytem
python pytem_merra_noclob_1990s.py
