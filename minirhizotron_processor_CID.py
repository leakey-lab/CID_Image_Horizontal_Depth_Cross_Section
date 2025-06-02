import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from PIL import Image, ImageDraw, ImageFont
import os
import math
import glob
import re
from scipy.interpolate import interp1d


def combine_tube_images(
    input_dir,
    pattern="*L???.png",
    output_path="combined_tube.png",
    stitch_direction="vertical",
):
    """
    Combines multiple tube images into a single continuous image.

    Args:
        input_dir (str): Directory containing the tube segment images
        pattern (str): Glob pattern to match the image files
        output_path (str): Path to save the combined image
        stitch_direction (str): "vertical" or "horizontal" stitching

    Returns:
        str: Path to the combined image file
    """
    # Find all matching image files
    image_files = glob.glob(os.path.join(input_dir, pattern))

    if not image_files:
        raise ValueError(f"No images found matching pattern {pattern} in {input_dir}")

    # Sort images by their position number (L001, L002, etc.)
    def extract_position(filename):
        match = re.search(r"L(\d+)", os.path.basename(filename))
        if match:
            return int(match.group(1))
        return 0  # Default if pattern not found

    image_files.sort(key=extract_position)
    print(
        f"Found {len(image_files)} images to combine: {[os.path.basename(f) for f in image_files]}"
    )

    # Load all images
    images = [Image.open(f) for f in image_files]

    # Check if all images have the same width for vertical stitching or same height for horizontal
    if stitch_direction == "vertical":
        widths = [img.width for img in images]
        if len(set(widths)) > 1:
            print(f"Warning: Images have different widths: {widths}")
            # Resize all images to match the most common width
            common_width = max(set(widths), key=widths.count)
            for i, img in enumerate(images):
                if img.width != common_width:
                    aspect = img.height / img.width
                    new_height = int(aspect * common_width)
                    images[i] = img.resize((common_width, new_height), Image.LANCZOS)
                    print(
                        f"Resized image {i + 1} from {img.width}x{img.height} to {common_width}x{new_height}"
                    )

        # Calculate dimensions of combined image
        total_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)

        # Create blank canvas for combined image
        combined = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

        # Paste each image
        y_offset = 0
        for img in images:
            combined.paste(img, (0, y_offset))
            y_offset += img.height

    else:  # horizontal stitching
        heights = [img.height for img in images]
        if len(set(heights)) > 1:
            print(f"Warning: Images have different heights: {heights}")
            # Resize all images to match the most common height
            common_height = max(set(heights), key=heights.count)
            for i, img in enumerate(images):
                if img.height != common_height:
                    aspect = img.width / img.height
                    new_width = int(aspect * common_height)
                    images[i] = img.resize((new_width, common_height), Image.LANCZOS)
                    print(
                        f"Resized image {i + 1} from {img.width}x{img.height} to {new_width}x{common_height}"
                    )

        # Calculate dimensions of combined image
        total_width = sum(img.width for img in images)
        total_height = max(img.height for img in images)

        # Create blank canvas for combined image
        combined = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

        # Paste each image
        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width

    # Save the combined image
    combined.save(output_path)
    print(f"Combined image saved to {output_path}")

    return output_path


def map_soil_depths_to_image(
    image_path,
    output_dir="output_soil_depths",
    cylinder_angle_deg=45,
    cylinder_diameter_cm=10,  # Assuming diameter, adjust as needed
    depth_interval_cm=40,  # Interval between soil depth levels
    max_depth_cm=200,  # Maximum soil depth to map
    image_height_cm=None,  # Height of the image in cm (calculated if None)
    image_width_cm=18.0,  # Width of the image in cm
    line_thickness=3,  # Thickness of depth lines
):
    """
    Maps horizontal soil depth levels to an unrolled cylindrical image and extracts
    depth-specific cross-sections, including the entire region between consecutive depths.

    Args:
        image_path (str): Path to the unrolled cylindrical image (PNG)
        output_dir (str): Directory to save output images
        cylinder_angle_deg (float): Angle of the cylinder in soil (degrees from horizontal)
        cylinder_diameter_cm (float): Diameter of the cylinder in cm
        depth_interval_cm (float): Interval between soil depth levels in cm
        max_depth_cm (float): Maximum soil depth to map in cm
        image_height_cm (float): Physical height of the image in cm (if None, will calculate based on width)
        image_width_cm (float): Physical width of the image in cm
        line_thickness (int): Thickness of depth lines in pixels

    Returns:
        tuple: (overlay_image_path, list_of_extracted_section_paths)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the image
    img = Image.open(image_path)
    img = img.rotate(90, expand=True)  # Rotate image to match the cylinder orientation
    img_width, img_height = img.size

    # If image_height_cm is not provided, calculate it maintaining aspect ratio
    if image_height_cm is None:
        image_height_cm = image_width_cm * (img_height / img_width)
        print(f"Calculated image height: {image_height_cm:.2f} cm")

    # Calculate conversion factors between pixels and cm
    pixels_per_cm_x = img_width / image_width_cm
    pixels_per_cm_y = img_height / image_height_cm

    # Calculate cylinder parameters
    cylinder_radius_cm = cylinder_diameter_cm / 2

    asscent_angle_rad = np.radians(cylinder_angle_deg)

    print(f"Cylinder angle above horizontal: {cylinder_angle_deg}°")
    # print(f"Using descent angle for calculations: {descent_angle_deg}°")

    extracted_sections = []

    # Create overlay image
    overlay_img = img.copy()
    draw = ImageDraw.Draw(overlay_img)

    # Define colors and depth levels
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 128, 0),
        (128, 0, 255),
        (0, 128, 255),
        (255, 0, 128),
    ]

    depth_levels = np.arange(0, max_depth_cm + 1, depth_interval_cm)
    if depth_levels[-1] < max_depth_cm:
        depth_levels = np.append(depth_levels, max_depth_cm)

    # Calculate projection curves using the corrected angle
    all_projection_curves = []

    for depth_cm in depth_levels:
        # Horizontal positions along the unwrapped cylinder
        x_positions = np.linspace(0, img_width, 1000)
        theta_positions = x_positions / img_width * 2 * np.pi

        # Vertical offset due to depth (using asscent angle)
        depth_offset = depth_cm / np.sin(asscent_angle_rad)

        # Sinusoidal variation around cylinder (using descent angle)
        angle_variation = (
            cylinder_radius_cm * np.cos(theta_positions) / np.tan(asscent_angle_rad)
        )

        # Combine effects
        y_positions = depth_offset + angle_variation

        # Convert to pixel coordinates
        x_px = x_positions
        y_px = img_height - (y_positions * pixels_per_cm_y)

        all_projection_curves.append(list(zip(x_px, y_px)))

        font = ImageFont.truetype("arial.ttf", 100)

    # Draw all projection lines on the overlay image
    for i, points in enumerate(all_projection_curves):
        color = colors[i % len(colors)]
        for j in range(len(points) - 1):
            draw.line([points[j], points[j + 1]], fill=color, width=line_thickness)

        # Label the depth level with specified font size
        label_x = 20
        label_y = points[0][1] - (100 + 10)  # Adjusted position for larger font
        if label_y < 0:
            label_y = points[0][1] + 20

        # Draw text with the specified font
        draw.text(
            (label_x, label_y), f"Depth: {depth_levels[i]} cm", fill=color, font=font
        )

    # Extract regions between consecutive depth levels
    for i in range(len(depth_levels) - 1):
        start_depth = depth_levels[i]
        end_depth = depth_levels[i + 1]
        color = colors[i % len(colors)]

        # Get the projection curves for this region
        upper_curve = all_projection_curves[i]
        lower_curve = all_projection_curves[i + 1]

        # Create a mask for the extraction zone (region between consecutive depths)
        mask = Image.new("L", img.size, 0)
        mask_draw = ImageDraw.Draw(mask)

        # Create a polygon connecting the upper and lower curves
        polygon_points = []
        polygon_points.extend(upper_curve)  # Add upper curve points
        polygon_points.extend(lower_curve[::-1])  # Add lower curve points in reverse

        # Draw the polygon as the extraction zone
        mask_draw.polygon(polygon_points, fill=255)

        # Extract the section using the mask
        extracted = Image.new("RGBA", img.size, (0, 0, 0, 0))
        extracted.paste(img, (0, 0), mask)

        # FIXED: Flip the image vertically so top is top and bottom is bottom
        extracted = extracted.transpose(Image.FLIP_TOP_BOTTOM)

        # Save the extracted section
        extracted_path = os.path.join(
            output_dir, f"depth_{start_depth}cm_to_{end_depth}cm.png"
        )
        extracted.save(extracted_path)
        extracted_sections.append((extracted_path, start_depth, end_depth))

    # FIXED: Flip the overlay image to match the orientation of extracted sections
    overlay_img = overlay_img.transpose(Image.FLIP_TOP_BOTTOM)

    # Save the overlay image
    overlay_path = os.path.join(output_dir, "depth_overlay.png")
    overlay_img.save(overlay_path)

    # Create a combined visualization showing all extracted sections
    create_combined_visualization(extracted_sections, output_dir)

    return overlay_path, [path for path, _, _ in extracted_sections]


def create_combined_visualization(section_infos, output_dir):
    """
    Create a combined visualization of all extracted sections.

    Args:
        section_infos (list): List of tuples (path, start_depth, end_depth)
        output_dir (str): Directory to save the visualization
    """
    # Sort sections by depth (shallow to deep)
    section_infos = sorted(section_infos, key=lambda x: x[1])

    # Create a figure with subplots for each section
    fig, axes = plt.subplots(
        len(section_infos), 1, figsize=(20, 6 * len(section_infos))
    )
    if len(section_infos) == 1:
        axes = [axes]  # Make sure axes is a list for consistent indexing

    # Load and display each section
    for i, (path, start_depth, end_depth) in enumerate(section_infos):
        img = Image.open(path)

        # Get the bounding box of non-transparent pixels
        if img.mode == "RGBA":
            # Get alpha channel data
            alpha = np.array(img.getchannel("A"))
            # Find non-transparent pixels
            non_empty_columns = np.where(alpha.max(axis=0) > 0)[0]
            non_empty_rows = np.where(alpha.max(axis=1) > 0)[0]

            # Check if there are any non-transparent pixels
            if len(non_empty_rows) > 0 and len(non_empty_columns) > 0:
                # Get bounding box
                crop_box = (
                    non_empty_columns.min(),
                    non_empty_rows.min(),
                    non_empty_columns.max() + 1,
                    non_empty_rows.max() + 1,
                )
                # Crop image to bounding box
                img = img.crop(crop_box)

        # Resize the image to make it larger
        scale_factor = 2
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)

        # Convert to numpy array for matplotlib
        img_array = np.array(img)

        # Display the image
        axes[i].imshow(img_array)
        axes[i].set_title(
            f"Soil Depth: {start_depth} cm to {end_depth} cm", fontsize=20
        )
        axes[i].axis("off")

    plt.tight_layout()
    # Higher DPI for better quality
    plt.savefig(os.path.join(output_dir, "all_depths.png"), dpi=1000)
    plt.close()


def process_tube_images(
    input_dir,
    output_dir="processed_tube",
    pattern="*L???*.png",
    cylinder_angle_deg=45,
    cylinder_diameter_cm=10,
    depth_interval_cm=40,
    max_depth_cm=200,
    image_width_cm=18.0,
    line_thickness=20,
):
    """
    Main function to process multiple tube segment images:
    1. Combines them into a single image
    2. Maps soil depths and extracts cross-sections

    Args:
        input_dir (str): Directory containing the tube segment images
        output_dir (str): Directory to save processed outputs
        pattern (str): Glob pattern to match the image files
        cylinder_angle_deg (float): Angle of the cylinder in soil (degrees from horizontal)
        cylinder_diameter_cm (float): Diameter of the cylinder in cm
        depth_interval_cm (float): Interval between soil depth levels in cm
        max_depth_cm (float): Maximum soil depth to map in cm
        image_width_cm (float): Physical width of the image in cm
        line_thickness (int): Thickness of depth lines in pixels

    Returns:
        tuple: (overlay_image_path, list_of_extracted_section_paths)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # 1. Combine the tube segment images
    combined_image_path = os.path.join(output_dir, "combined_tube.png")
    combined_image_path = combine_tube_images(
        input_dir,
        pattern=pattern,
        output_path=combined_image_path,
        stitch_direction="horizontal",
    )

    # 2. Process the combined image to map soil depths and extract cross-sections
    overlay_path, section_paths = map_soil_depths_to_image(
        combined_image_path,
        output_dir=output_dir,
        cylinder_angle_deg=cylinder_angle_deg,
        cylinder_diameter_cm=cylinder_diameter_cm,
        depth_interval_cm=depth_interval_cm,
        max_depth_cm=max_depth_cm,
        image_height_cm=None,  # Will be calculated based on aspect ratio
        image_width_cm=image_width_cm,
        line_thickness=line_thickness,
    )

    return overlay_path, section_paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process multiple tube segment images for soil depth mapping"
    )
    parser.add_argument("input_dir", help="Directory containing tube segment images")
    parser.add_argument(
        "--pattern", default="*L???*.png", help="Glob pattern to match image files"
    )
    parser.add_argument(
        "--output_dir",
        default="processed_tube",
        help="Directory to save output images",
    )
    parser.add_argument(
        "--angle", type=float, default=45, help="Angle of cylinder in soil (degrees)"
    )
    parser.add_argument(
        "--diameter", type=float, default=10, help="Diameter of cylinder in cm"
    )
    parser.add_argument(
        "--interval", type=float, default=40, help="Interval between soil depths in cm"
    )
    parser.add_argument(
        "--max_depth", type=float, default=200, help="Maximum soil depth to map in cm"
    )
    parser.add_argument(
        "--img_width", type=float, default=18.0, help="Physical width of image in cm"
    )
    parser.add_argument(
        "--process_single",
        action="store_true",
        help="Process a single image instead of combining multiple",
    )

    args = parser.parse_args()

    if args.process_single:
        # Find the first matching image and process it
        image_files = glob.glob(os.path.join(args.input_dir, args.pattern))
        if not image_files:
            print(
                f"No images found matching pattern {args.pattern} in {args.input_dir}"
            )
            exit(1)

        map_soil_depths_to_image(
            image_files[0],
            output_dir=args.output_dir,
            cylinder_angle_deg=args.angle,
            cylinder_diameter_cm=args.diameter,
            depth_interval_cm=args.interval,
            max_depth_cm=args.max_depth,
            image_width_cm=args.img_width,
        )
        print(f"Processed single image: {image_files[0]}")
    else:
        # Process and combine multiple images
        process_tube_images(
            args.input_dir,
            output_dir=args.output_dir,
            pattern=args.pattern,
            cylinder_angle_deg=args.angle,
            cylinder_diameter_cm=args.diameter,
            depth_interval_cm=args.interval,
            max_depth_cm=args.max_depth,
            image_width_cm=args.img_width,
        )

    print(f"Processing complete. Results saved to {args.output_dir}")
