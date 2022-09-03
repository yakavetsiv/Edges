# Edges_GUI

The script help to detect the edge of the liquid interface for gravity-driven microfluidics platforms

Raw RBG images from the camera were preprocessed in Fiji:
1. Organizing the images in time sequence (File - Import - Image Sequence)
2. Cropping (Image - Crop)
3. Edges detection (Process - Find Edges)
4. BW (Image - Type - 8-Bit)
5. Save as *.tif (File - Save as - Tiff) 
 
 
Script workflow:
1. Open file (*.tif) - Open the time-sequence
2. Scale (1 cm) - Set a scale (1cm on the image)
3. Set the scales (1 mm in pixels; 1 mm in uL; time interval between the frames)
4. Add line - (Minimal point - precision is important; Maximal point) - Set a middle line, which is perpendicular to the liquid interface
5. Analyze
