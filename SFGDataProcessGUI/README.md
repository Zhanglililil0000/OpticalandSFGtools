# SFGDataProcessGUI

This program is designed for fast SFG spectra processing. Main functions including background subtraction, normalization and result plotting.

Main codes are written in python and released to .exe program, which could be found and download in **Releases**.

## How to use this program

You need to have raw data in .csv or .asc format. Raw data including SFG intensity from $\alpha$-quartz surface, the sample you measured, and background signal under the same exposure condition. These data could easily be imported into the program by clicking the buttons. 

You also need to enter the experiment conditions, such as exposure time and center wavelength of visible.

After clicking the 'Process Data' button, the result, both in .csv and .jpg format, will be stored in the same position of sample signal.

## A few more things

- If you have additional demands on remove the spikes in the spectra, you can first remove the spikes in the result and background using another program I developed: https://github.com/Zhanglililil0000/SFGSpikeRemove

- We recommend using $\alpha$-quartz as an intensity standard reference in SFG-VS experiment, it is stable, high energy tolerance, and wildly used in many research groups. Another advantage is that one can easily calculate the absolute $\chi^{(2)}_{eff}$ value of the sample since the absolute $\chi^{(2)}_{eff}$ value of $\alpha$-quartz could be directly calculated. You can go to the following literature for additional information.

    - J. Phys. Chem. C 2019, 123, 15071−15086, DOI: 10.1021/acs.jpcc.9b03202
    - J. Phys. Chem. A 2011, 115, 6015–6027, DOI: 10.1021/jp110404h
    - Phys. Rev. E 2000, 62, 5160-5172, DOI: 10.1103/physreve.62.5160

## Our Group Website
For more information related to SFG, and other nonlinear spectra studies such as SHG and SRS, please go to our group website: https://hfwgroup.westlake.edu.cn/
