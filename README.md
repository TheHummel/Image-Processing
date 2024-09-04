# Image Processing for Bachelor Thesis

This repository contains image processing code developed for my bachelor thesis.
 It includes scripts and modules for image denoising, metric evaluation, helper functions, and capturing images using an OV camera.

 ## Denoising
 **denoising/** contains modules for Noise Reduction via Ensemble Averaging, ROF denoising and image stacking, **run_NREA.py**, **run_ROF.py** and **run_image_stacking.py** are the corresponding scripts. **run_NREA_filter_comparison.py** runs NREA for circular averaging and gaussian blurring for different kernel sizes.

 ## Metrics
 **metrics/** contains module for calculaing the signal-to-noise ratio (SNR) of images and calculating the variation of signal, noise and SNR.

 ## OV camera control
 **ov_control/** contains code for taking pictures with an OV2640 or OV5640 camera.

 ## Other stuff
 **helpers/** contains helper functions.

 **cropping.py** allows cropping images by a given factor to squares.

 **compare_native_to_custom.py** compares SNRs of images taken by the native camera app from Android and a custom camera app which can be found [here](https://github.com/TheHummel/BTCamera).

 **compare_settings_range.py** compares SNR for images taken with different ISO and exposure times.

**find_circle.py** finds circles in an image via Circle Hough Transform.

**find_circles_grid.py** finds a 3x3 grid of circles:
<img width="758" alt="image" src="https://github.com/user-attachments/assets/2784dfb0-f66c-4844-82cc-264de12cb3d2">
