# Minirhizotron Tube Image Processing Tool

A Python tool for processing minirhizotron tube images to map soil depths and extract depth-specific cross-sections for root analysis.

## Overview

This tool processes images captured by minirhizotron cameras (like the CID-602) that photograph plant roots through transparent tubes installed at an angle in the soil. The software:

1. **Combines multiple tube segment images** into a single continuous image
2. **Maps horizontal soil depth levels** onto the unrolled cylindrical images as sinusoidal curves
3. **Extracts depth-specific regions** between consecutive depth levels for targeted root analysis

## Key Features

- Automatic stitching of multiple tube segment images (horizontal or vertical)
- Accurate geometric mapping of soil depths accounting for tube angle
- Color-coded depth visualization with overlay
- Extraction of individual depth regions for analysis
- High-resolution output with configurable parameters

## Installation

### Requirements

```bash
pip install numpy matplotlib pillow scipy
```

### Dependencies

- Python 3.6+
- NumPy
- Matplotlib
- Pillow (PIL)
- SciPy

## Usage

### Command Line Interface

#### Basic Usage - Process Multiple Tube Segments

```bash
python minirhizotron_processor_CID.py /path/to/input/images --output_dir output_results
```

#### Process a Single Image

```bash
python minirhizotron_processor_CID.py /path/to/input/images --process_single --output_dir output_results
```

### Command Line Arguments

- `input_dir` (required): Directory containing tube segment images
- `--pattern`: Glob pattern to match image files (default: "*L???.png")
- `--output_dir`: Directory to save output images (default: "processed_tube")
- `--angle`: Angle of cylinder in soil, measured from horizontal (default: 45 degrees)
- `--diameter`: Diameter of cylinder in cm (default: 10 cm)
- `--interval`: Interval between soil depth levels in cm (default: 40 cm)
- `--max_depth`: Maximum soil depth to map in cm (default: 200 cm)
- `--img_width`: Physical width of image in cm (default: 18.0 cm)
- `--process_single`: Process a single image instead of combining multiple

### Python API

```python
from minirhizotron_processor_CID import process_tube_images, map_soil_depths_to_image

# Process multiple tube segments
overlay_path, section_paths = process_tube_images(
    input_dir="path/to/images",
    output_dir="output",
    cylinder_angle_deg=45,
    cylinder_diameter_cm=10,
    depth_interval_cm=40,
    max_depth_cm=200
)

# Process a single image
overlay_path, section_paths = map_soil_depths_to_image(
    image_path="path/to/image.png",
    output_dir="output",
    cylinder_angle_deg=45,
    cylinder_diameter_cm=10,
    depth_interval_cm=40,
    max_depth_cm=200
)
```

## Output Files

The tool generates several output files:

1. **combined_tube.png**: Stitched image combining all input segments (if processing multiple)
2. **depth_overlay.png**: Combined image with color-coded depth lines overlaid
3. **depth_XXcm_to_YYcm.png**: Extracted regions for each depth interval (e.g., depth_0cm_to_40cm.png)
4. **all_depths.png**: Visualization showing all extracted depth regions in a single figure

## Understanding the Geometry

### Angle Convention

The `cylinder_angle_deg` parameter represents the angle of the tube **above the horizontal ground plane**:
- 0° = horizontal (parallel to ground)
- 45° = typical installation angle
- 90° = vertical (straight down)

### Image Orientation

- Input images are automatically rotated 90° to match the expected cylinder orientation
- The coordinate system assumes:
  - Horizontal (u): Corresponds to angle around the tube (0-360°)
  - Vertical (v): Corresponds to distance along the tube axis
  - Larger 's' values (deeper in soil) map to smaller 'v' values (higher in image)

### Depth Mapping Mathematics

The tool uses precise geometric calculations to map horizontal soil layers onto the cylindrical surface:

```
s(φ,d) = (d + R cos(φ) cos(θ)) / sin(θ)
```

Where:
- `s`: Distance along tube axis
- `φ`: Angle around tube circumference
- `d`: Soil depth
- `R`: Tube radius
- `θ`: Tube angle from horizontal

This creates the characteristic sinusoidal pattern of depth lines on unrolled images.

## Image Processing Pipeline

1. **Image Loading and Stitching**
   - Sorts images by position number (L001, L002, etc.)
   - Handles images with different dimensions through intelligent resizing
   - Supports both horizontal and vertical stitching

2. **Coordinate Transformation**
   - Rotates images to match expected orientation
   - Calculates pixel-to-physical unit conversions
   - Maps cylindrical coordinates to image coordinates

3. **Depth Line Calculation**
   - Computes sinusoidal curves for each depth level
   - Accounts for tube angle and radius
   - Generates high-resolution curves (1000 points)

4. **Region Extraction**
   - Creates polygon masks between consecutive depth curves
   - Extracts regions with transparent backgrounds
   - Auto-crops to remove empty space
   - Scales extracted regions for better visibility

## Customization

### Adjusting Visual Parameters

- `line_thickness`: Thickness of depth lines in pixels (default: 3, can increase to 20+ for visibility)
- Font size for depth labels: Modify in code (currently set to 100pt Arial)
- Colors: Predefined palette of 10 distinct colors, cycles for additional depths

### Physical Parameters

Ensure these match your minirhizotron setup:
- `cylinder_diameter_cm`: Actual diameter of your tube
- `cylinder_angle_deg`: Installation angle from horizontal
- `image_width_cm`: Physical width represented by the image

## Limitations and Considerations

1. **Angle Restrictions**: Cannot process perfectly horizontal tubes (0° or 180°) due to division by sin(θ)
2. **Image Format**: Expects PNG images with transparency support
3. **Naming Convention**: Default pattern expects files named with "L" followed by three digits (e.g., L001.png)
4. **Memory Usage**: High-resolution processing may require significant memory for large images

## Troubleshooting

### Common Issues

1. **"No images found" error**
   - Check that your image files match the pattern (default: *L???.png)
   - Verify the input directory path is correct

2. **Misaligned depth lines**
   - Verify the cylinder angle matches your actual installation
   - Check that image_width_cm is accurately measured

3. **Images have different dimensions warning**
   - The tool automatically resizes images to match the most common dimension
   - For best results, use consistently sized input images

## Example Workflow

```bash
# 1. Prepare your images (L001.png, L002.png, etc.) in a directory

# 2. Run the processor with your tube's specifications
python minirhizotron_processor_CID.py ./tube_images \
    --angle 45 \
    --diameter 7.5 \
    --interval 25 \
    --max_depth 150 \
    --output_dir results_2024

# 3. Review outputs in the results directory
# - Check depth_overlay.png for accuracy
# - Use individual depth_XXcm_to_YYcm.png files for root analysis
```

## Citation

If you use this tool in your research, please cite appropriately and acknowledge the geometric principles underlying the depth mapping algorithm.

## License

[Specify your license here]

## Contributing

Contributions are welcome! Please submit issues or pull requests on the project repository.
